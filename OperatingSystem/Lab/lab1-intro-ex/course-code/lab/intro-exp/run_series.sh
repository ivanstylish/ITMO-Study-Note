set -euo pipefail
export LC_ALL=C                                  # CSV 一律用小数点
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"; [[ -f src/graph_traverse.c ]] || cd ../intro-exp

# ---------- 参数（在看结果之前定好） ----------
CORE=${CORE:-2}                 # taskset 绑定的核心
N=${N:-30}                      # 正式测量轮数
ITER=${ITER:-20}                # 每次运行的完整遍历次数，四组相同
WARMUP=${WARMUP:-2}             # 每组预热次数，丢弃
for name in CORE N ITER WARMUP; do
  [[ ${!name} =~ ^(0|[1-9][0-9]*)$ ]] || { echo "ERROR: Invalid integer: $name" >&2; exit 1; }
done
(( N>=2 && ITER>=1 )) || { echo 'ERROR: N must be >=2 and ITER must be >=1' >&2; exit 1; }
taskset -c "$CORE" true
case "$(findmnt -n -o FSTYPE -T .)" in
  9p|drvfs|ntfs|ntfs3|fuseblk) echo 'ERROR: Run from the Ubuntu home filesystem' >&2; exit 1 ;;
esac
EXPECTED_NODES=436905           # graphgen 输出的顶点数，每次遍历都必须处理这么多
ORIG=graph-seq.orig.bin         # 原始图（只读）
GRAPH=graph-seq.bin             # 工作副本（Write 会改它的 value）
RUN_DIR=$PWD/results/series-$(date +%Y%m%d-%H%M%S)-$$
OUT=$RUN_DIR/results.csv
LOGDIR=$RUN_DIR/logs
export CORE N ITER WARMUP       # 让 env_snapshot.sh 把参数写进快照
CONFIGS=("read_lseek|read" "read_lseek|write" "mmap|read" "mmap|write")   # api|mode

TMP=$(mktemp); WALLF=$(mktemp); trap 'rm -f "$TMP" "$WALLF"' EXIT

# ---------- 1. 编译、生成数据、留存脚本 ----------
mkdir -p out "$LOGDIR"
gcc -O2 -Wall -o out/graph_traverse      src/graph_traverse.c
gcc -O2 -Wall -o out/graph_traverse_mmap src/graph_traverse_mmap.c
python3 ../util/graphgen.py -s 10M --seed 427 --topology sequential --verify -o "$ORIG" | tee "$LOGDIR/graphgen.log"
cp "$SCRIPT_DIR"/run_series.sh "$SCRIPT_DIR"/env_snapshot.sh "$RUN_DIR/"

# ---------- 2. 单次运行：结果放进全局变量 WALL / RUSAGE / CHECK ----------
run_once() {                    # $1=api  $2=mode  $3=日志标签
  local api=$1 mode=$2 tag=$3 bin=./out/graph_traverse flag=()
  [[ $api == mmap ]] && bin=./out/graph_traverse_mmap
  [[ $mode == write ]] && flag=(--write)

  cp "$ORIG" "$GRAPH"; sync; cat "$GRAPH" > /dev/null          # 准备阶段，不计时，四组一致

  mono_run "$WALLF" \
      /usr/bin/time -f '%U,%S,%w,%c,%R,%F' -o "$TMP" \
      taskset -c "$CORE" "$bin" "${flag[@]}" "$ITER" "$GRAPH" >"$LOGDIR/$tag.log" 2>&1 ||
    { echo "ERROR: $tag failed; see $LOGDIR/$tag.log" >&2; exit 1; }

  WALL=$(<"$WALLF")
  RUSAGE=$(tail -n1 "$TMP")                                    # user,sys,自愿切换,被动切换,minflt,majflt

  # 每次遍历都必须处理 EXPECTED_NODES 个顶点，否则说明程序没有正常完成工作
  local ok; ok=$(grep -cF "OK ($EXPECTED_NODES nodes processed)" "$LOGDIR/$tag.log" || true)
  [[ $ok -eq $ITER ]] || { echo "ERROR: $tag has an unexpected traversal/node count; see $LOGDIR/$tag.log" >&2; exit 1; }

  # 自检：单线程程序 user+sys 不应明显大于 wall，否则这条计时可疑（只标记，不删除）
  CHECK=$(awk -v w="$WALL" -v r="$RUSAGE" 'BEGIN{split(r,a,","); print ((a[1]+a[2]) > w*1.10+0.03) ? "bad" : "ok"}')
}

# ---------- 3. 预热（丢弃）-> 快照 -> 正式系列（交错 + 轮换） ----------
for w in $(seq 1 "$WARMUP"); do
  for cfg in "${CONFIGS[@]}"; do
    IFS='|' read -r api mode <<< "$cfg"
    run_once "$api" "$mode" "warmup_${w}_${api}_${mode}"
  done
done

bash "$SCRIPT_DIR/env_snapshot.sh" before "$RUN_DIR"
echo "timestamp,round,position,api,mode,graph,iterations,cache,cpu,wall_s,user_s,sys_s,vol_ctx,invol_ctx,minflt,majflt,exit_code,cpu_check,nodes" > "$OUT"

for r in $(seq 1 "$N"); do
  for k in 0 1 2 3; do
    IFS='|' read -r api mode <<< "${CONFIGS[$(( (k + r - 1) % 4 ))]}"     # 每轮起始组后移一格
    run_once "$api" "$mode" "r${r}_${api}_${mode}"
    # exit_code 恒为 0（非 0 会在 run_once 中止）；timestamp 仅作标签
    echo "$(date +%s),$r,$k,$api,$mode,$GRAPH,$ITER,warm,$CORE,$WALL,$RUSAGE,0,$CHECK,$EXPECTED_NODES" >> "$OUT"
  done
  echo "round $r/$N done"
done

bash "$SCRIPT_DIR/env_snapshot.sh" after "$RUN_DIR"
echo "Done: $OUT ($(($(wc -l < "$OUT") - 1)) rows); cpu_check=bad rows: $(awk -F, 'NR>1 && $18=="bad"' "$OUT" | wc -l)"
