#!/usr/bin/env bash
# run_diagnostics.sh -- 诊断与对照实验（README 4.3 / 第 5 节 / 第 6 节的要求），与主系列分开运行。
#   A. 四组各一次代表性运行：/usr/bin/time -v、strace -c、perf stat   -> 解释"为什么慢/快"
#   B. 工具侵入性：同一配置 裸跑 / perf stat / strace -c 各 REPS 次   -> 比较 wall
#   C. 背景负载：同一配置 安静 / stress-ng 各 REPS 次                  -> 看"有噪声的测量"
# 前提：已经运行过 run_series.sh（需要 out/ 里的程序和 graph-seq.orig.bin）。
# 用法：CORE=2 ITER=20 REPS=10 bash run_diagnostics.sh        （先用 REPS=2 试跑一遍）
set -euo pipefail
export LC_ALL=C
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"; [[ -f src/graph_traverse.c ]] || cd ../intro-exp

CORE=${CORE:-2}                 # 与主系列相同的核心
ITER=${ITER:-20}                # A 中 time -v / perf 和 C 使用，与主系列相同
TRACE_ITER=${TRACE_ITER:-1}     # A 中 strace 和 B 使用：strace 很慢，只跑 1 次遍历
REPS=${REPS:-10}                # B、C 的重复次数
LOAD_API=${LOAD_API:-read_lseek}   # C 使用的实现：read_lseek 或 mmap（模式固定为 read）
PERF=${PERF:-perf}              # perf 可执行文件；WSL2 常需手动指定
PERF_EVENTS=task-clock,context-switches,cpu-migrations,page-faults,cache-references,cache-misses
ORIG=graph-seq.orig.bin; GRAPH=graph-seq.bin
DIAG_DIR=$PWD/results/diag-$(date +%Y%m%d-%H%M%S)
CONFIGS=("read_lseek|read" "read_lseek|write" "mmap|read" "mmap|write")

for t in /usr/bin/time strace stress-ng taskset; do
  command -v "$t" > /dev/null || { echo "ERROR: 缺少 $t（sudo apt install time strace stress-ng）" >&2; exit 1; }
done
[[ -f $ORIG && -x out/graph_traverse && -x out/graph_traverse_mmap ]] ||
  { echo "ERROR: 请先运行 run_series.sh（需要 out/ 与 $ORIG）" >&2; exit 1; }
command -v "$PERF" > /dev/null && HAVE_PERF=1 || { HAVE_PERF=0; echo "WARN: 找不到 $PERF，跳过 perf（报告里如实写明）" >&2; }

mkdir -p "$DIAG_DIR"
TMP=$(mktemp); WALLF=$(mktemp); SPID=
trap 'rm -f "$TMP" "$WALLF"; [[ -n $SPID ]] && kill "$SPID" 2>/dev/null || true' EXIT
cp "$SCRIPT_DIR"/run_diagnostics.sh "$SCRIPT_DIR"/mono_time.py "$DIAG_DIR/"
CORE=$CORE ITER=$ITER bash "$SCRIPT_DIR/env_snapshot.sh" diag "$DIAG_DIR"

# ---------- 辅助函数 ----------
prepare() { cp "$ORIG" "$GRAPH"; sync; cat "$GRAPH" > /dev/null; }     # 与主系列相同的准备阶段

cmd_of() {                      # cmd_of <api> <mode> <遍历次数> -> 数组 CMD（含 taskset）
  local bin=./out/graph_traverse flag=()
  [[ $1 == mmap ]] && bin=./out/graph_traverse_mmap
  [[ $2 == write ]] && flag=(--write)
  CMD=(taskset -c "$CORE" "$bin" "${flag[@]}" "$3" "$GRAPH")
}

wall_of() {                     # wall_of <日志> <命令...> -> WALL（单调时钟），命令输出写入日志
  local log=$1; shift
  python3 "$SCRIPT_DIR/mono_time.py" "$WALLF" "$@" >"$log" 2>&1 || { echo "ERROR: 命令失败，见 $log" >&2; exit 1; }
  WALL=$(<"$WALLF")
}

# ---------- A. 单次诊断 ----------
echo "== A. time -v / strace -c / perf stat =="
A=$DIAG_DIR/A; mkdir -p "$A"
for cfg in "${CONFIGS[@]}"; do
  IFS='|' read -r api mode <<< "$cfg"; name=${api}_${mode}

  cmd_of "$api" "$mode" "$ITER"
  prepare; /usr/bin/time -v -o "$A/time_v_$name.txt" "${CMD[@]}" > "$A/prog_$name.log" 2>&1

  if [[ $HAVE_PERF == 1 ]]; then
    prepare; "$PERF" stat -e "$PERF_EVENTS" -o "$A/perf_$name.txt" "${CMD[@]}" > /dev/null 2>&1 ||
      echo "perf 运行失败或事件不受支持" > "$A/perf_$name.txt"
  fi

  cmd_of "$api" "$mode" "$TRACE_ITER"                            # strace 很慢：只遍历 TRACE_ITER 次
  prepare; strace -c -S calls -o "$A/strace_$name.txt" "${CMD[@]}" > /dev/null 2>&1
  echo "  $name done"
done

# ---------- B. 工具侵入性（读模式，两种实现，各 REPS 次，工具交错） ----------
echo "== B. 工具侵入性 =="
echo "api,tool,rep,wall_s" > "$DIAG_DIR/tool_overhead.csv"
TOOLS=(bare strace); [[ $HAVE_PERF == 1 ]] && TOOLS=(bare perf strace)
for rep in $(seq 1 "$REPS"); do
  for api in read_lseek mmap; do
    cmd_of "$api" read "$TRACE_ITER"
    for tool in "${TOOLS[@]}"; do
      case $tool in
        bare)   T=() ;;
        perf)   T=("$PERF" stat -e "$PERF_EVENTS" -o /dev/null) ;;
        strace) T=(strace -c -o /dev/null) ;;
      esac
      prepare; wall_of "$DIAG_DIR/B_last.log" "${T[@]}" "${CMD[@]}"
      echo "$api,$tool,$rep,$WALL" >> "$DIAG_DIR/tool_overhead.csv"
    done
  done
  echo "  B rep $rep/$REPS"
done

# ---------- C. 背景负载：stress-ng 与被测进程绑到同一个核心，保证确实发生竞争 ----------
echo "== C. 背景负载（$LOAD_API + read） =="
echo "condition,rep,wall_s,user_s,sys_s,vol_ctx,invol_ctx,minflt,majflt" > "$DIAG_DIR/load.csv"
cmd_of "$LOAD_API" read "$ITER"
for rep in $(seq 1 "$REPS"); do
  for cond in quiet stress; do
    if [[ $cond == stress ]]; then
      taskset -c "$CORE" stress-ng --cpu 2 --io 1 --vm 1 --vm-bytes 256M --timeout 600s > /dev/null 2>&1 &
      SPID=$!; sleep 2
      if [[ $rep -eq 1 ]]; then top -bn1 | head -15 > "$DIAG_DIR/C_top_during_stress.txt"; fi
    fi
    prepare
    wall_of "$DIAG_DIR/C_last.log" /usr/bin/time -f '%U,%S,%w,%c,%R,%F' -o "$TMP" "${CMD[@]}"
    echo "$cond,$rep,$WALL,$(tail -n1 "$TMP")" >> "$DIAG_DIR/load.csv"
    if [[ $cond == stress ]]; then kill "$SPID"; wait "$SPID" 2> /dev/null || true; SPID=; fi
  done
  echo "  C rep $rep/$REPS"
done

echo "完成：$DIAG_DIR"
echo "汇总统计：python3 $SCRIPT_DIR/analyze_diag.py $DIAG_DIR"
