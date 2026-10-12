set -euo pipefail
export LC_ALL=C
cd -- "$(dirname -- "$0")"
CORE=${CORE:-2}; REPS=${REPS:-3}; ITER=${ITER:-20}; LIMIT=${LIMIT:-180}
TOOLS_REPS=${TOOLS_REPS:-1}; PERF_BIN=${PERF_BIN:-perf}
STAGE=${STAGE:-all}
[[ $STAGE == all || $STAGE == tools || $STAGE == noise ]] || { echo 'ERROR: STAGE must be all, tools, or noise' >&2; exit 1; }
for name in CORE REPS ITER LIMIT TOOLS_REPS; do
  [[ ${!name} =~ ^(0|[1-9][0-9]*)$ ]] || { echo "ERROR: Invalid integer: $name" >&2; exit 1; }
done
(( REPS>0 && ITER>0 && LIMIT>0 && TOOLS_REPS>0 && TOOLS_REPS<=10 )) || { echo 'ERROR: Positive counts required; TOOLS_REPS must be 1..10' >&2; exit 1; }
for cmd in python3 taskset timeout /usr/bin/time setsid; do
  command -v "$cmd" >/dev/null || { echo "ERROR: Missing $cmd; install time strace util-linux coreutils python3" >&2; exit 1; }
done
if [[ $STAGE != noise ]]; then command -v strace >/dev/null || { echo 'ERROR: Install strace first' >&2; exit 1; }; fi
taskset -c "$CORE" true
[[ -x out/graph_traverse && -x out/graph_traverse_mmap && -f graph-seq.orig.bin ]] || {
  echo 'ERROR: Compile the programs and generate graph-seq.orig.bin first' >&2; exit 1;
}
[[ $(stat -c %s graph-seq.orig.bin) == 10485760 ]] || { echo 'ERROR: Expected a 10 MiB graph' >&2; exit 1; }
case "$(findmnt -n -o FSTYPE -T .)" in
  9p|drvfs|ntfs|ntfs3|fuseblk) echo 'ERROR: Run from the Ubuntu home filesystem' >&2; exit 1 ;;
esac
D="$PWD/results/diag-short-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$D/logs"
G="$D/graph-work.bin"; WORKER=''; COMPLETE=0; SEQ=0
stop_worker() {
  if [[ -n $WORKER ]]; then
    kill -- "-$WORKER" 2>/dev/null || true
    wait "$WORKER" 2>/dev/null || true
    WORKER=''
  fi
}
trap 'stop_worker; if (( COMPLETE==0 )); then echo "Interrupted or failed" > "$D/STATUS.txt"; fi' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cp -- "$(basename -- "$0")" "$D/"
{
  echo "CORE=$CORE REPS=$REPS ITER=$ITER LIMIT=$LIMIT STAGE=$STAGE TOOLS_REPS=$TOOLS_REPS PERF_BIN=$PERF_BIN"
  echo 'Tools: four configurations, one traversal; tool order rotates across repeated rounds.'
  echo 'Noise: read mode, both APIs, ITER traversals, paired quiet/CPU-only load, alternating order.'
  echo 'Preparation outside timer: restore -> sync -> cat; same-CPU load starts AFTER preparation.'
  echo 'Warmup: one quiet run of ITER traversals per API, excluded from measurements.csv.'
  echo 'wall_s: monotonic time around timeout + taskset + tool + program; realtime_s: audit only.'
  sha256sum graph-seq.orig.bin out/graph_traverse out/graph_traverse_mmap
} > "$D/protocol.txt"
snapshot() { { date -Is; uname -a; uptime; free -h; top -bn1 | head -15 || true; } > "$D/environment-$1.txt" 2>&1; }
snapshot before
# 仅内嵌计时，不做Python统计；同时保存实时时钟差以检查时间一致性。
measure() {
  python3 - "$D/timing.tmp" "$@" <<'PY'
import subprocess, sys, time
r0 = time.time_ns()
m0 = time.monotonic_ns()
p = subprocess.run(sys.argv[2:])
m1 = time.monotonic_ns()
r1 = time.time_ns()
with open(sys.argv[1], 'w') as f:
    f.write(f'{(m1-m0)/1e9:.9f},{(r1-r0)/1e9:.9f},{r0},{r1}')
sys.exit(p.returncode)
PY
}
HAVE_PERF=0
EVENTS=context-switches,cpu-migrations,page-faults,cache-misses
if [[ $STAGE == noise ]]; then
  echo 'Tool diagnostics not requested in this run; use previous diagnostic evidence separately.' > "$D/stage.txt"
elif command -v "$PERF_BIN" >/dev/null; then
  "$PERF_BIN" --version > "$D/perf-version.txt" 2>&1 || true
  if timeout 10 "$PERF_BIN" stat -e "$EVENTS" -- true > "$D/perf-probe.txt" 2>&1; then
    HAVE_PERF=1
    if grep -Eq 'not supported|not counted|No permission' "$D/perf-probe.txt"; then
      echo 'Some perf events unavailable; unsupported values are not zero. See perf-probe.txt.' >> "$D/unavailable.txt"
    fi
  else echo 'perf events unavailable; see perf-probe.txt.' >> "$D/unavailable.txt"; fi
else echo 'perf is not installed; no perf counters were collected.' >> "$D/unavailable.txt"; fi
echo 'phase,api,mode,tool,rep,iterations,wall_s,realtime_s,real_start_ns,real_end_ns,exit_code,valid,log' > "$D/measurements.csv"
echo 'api,condition,rep,iterations,wall_s,user_s,sys_s,vol_ctx,invol_ctx,minflt,majflt' > "$D/load.csv"
run() {
  local phase=$1 api=$2 mode=$3 tool=$4 rep=$5 iterations=$6
  local bin=./out/graph_traverse flags=() prefix=() rc=0 valid=1 tag count
  [[ $api != mmap ]] || bin=./out/graph_traverse_mmap
  [[ $mode != write ]] || flags=(--write)
  SEQ=$((SEQ+1)); tag="${SEQ}_${phase}_${api}_${mode}_${tool}_${rep}"
  cp graph-seq.orig.bin "$G"; sync; cat "$G" >/dev/null
  case $tool in
    time_v) prefix=(/usr/bin/time -v -o "$D/logs/$tag.time.txt") ;;
    strace) prefix=(strace -c -S calls -o "$D/logs/$tag.strace.txt") ;;
    perf) prefix=("$PERF_BIN" stat -e "$EVENTS" -o "$D/logs/$tag.perf.txt" --) ;;
    resource) prefix=(/usr/bin/time -f '%U,%S,%w,%c,%R,%F' -o "$D/resource.tmp") ;;
  esac
  if [[ $phase == stress ]]; then
    # 一个CPU忙循环，不再制造I/O压力。进程组仅属于本脚本。
    setsid taskset -c "$CORE" timeout "$((LIMIT+10))" bash -c 'while :; do :; done' >/dev/null 2>&1 &
    WORKER=$!
  fi
  sleep 0.2
  [[ $phase != stress ]] || kill -0 "$WORKER"
  echo "Running: $tag (timeout ${LIMIT}s)"
  printf '%q ' timeout -k 3 "$LIMIT" taskset -c "$CORE" "${prefix[@]}" "$bin" "${flags[@]}" "$iterations" "$G" > "$D/logs/$tag.command.txt"
  measure timeout -k 3 "$LIMIT" taskset -c "$CORE" "${prefix[@]}" "$bin" "${flags[@]}" "$iterations" "$G" > "$D/logs/$tag.log" 2>&1 || rc=$?
  stop_worker
  count=$(grep -cF 'OK (436905 nodes processed)' "$D/logs/$tag.log" || true)
  [[ $rc == 0 && $count == "$iterations" ]] || valid=0
  if [[ $phase != warmup ]]; then
    echo "$phase,$api,$mode,$tool,$rep,$iterations,$(cat "$D/timing.tmp"),$rc,$valid,logs/$tag.log" >> "$D/measurements.csv"
    if [[ $tool == resource && $valid == 1 ]]; then
      echo "$api,$phase,$rep,$iterations,$(cut -d, -f1 "$D/timing.tmp"),$(tail -1 "$D/resource.tmp")" >> "$D/load.csv"
    fi
  fi
  if (( valid==0 )); then
    echo "Failed or incomplete: $tag (exit=$rc); see logs." >> "$D/unavailable.txt"
    [[ $phase == tools && $tool != bare ]] || exit 1
  fi
}
for api in read_lseek mmap; do run warmup "$api" read bare 0 "$ITER"; done
if [[ $STAGE != noise ]]; then
tools=(bare time_v strace)
(( HAVE_PERF==0 )) || tools+=(perf)
for ((rep=1; rep<=TOOLS_REPS; rep++)); do
  for api in read_lseek mmap; do
    for mode in read write; do
      for ((pos=0; pos<${#tools[@]}; pos++)); do
        tool=${tools[$(( (pos+rep-1)%${#tools[@]} ))]}
        run tools "$api" "$mode" "$tool" "$rep" 1
      done
    done
  done
done
fi
snapshot after-tools
if [[ $STAGE != tools ]]; then
for ((rep=1; rep<=REPS; rep++)); do
  for api in read_lseek mmap; do
    conditions=(quiet stress)
    (( rep%2 )) || conditions=(stress quiet)
    for condition in "${conditions[@]}"; do run "$condition" "$api" read resource "$rep" "$ITER"; done
  done
done
fi
snapshot after
awk -F, 'BEGIN{OFS=","; t[1]=12.706204736; t[2]=4.302652730; t[3]=3.182446305; t[4]=2.776445105; t[5]=2.570581836; t[6]=2.446911851; t[7]=2.364624252; t[8]=2.306004135; t[9]=2.262157163}
NR>1 && $12==1 {k=$1 "," $2 "," $3 "," $4; n[k]++; delta=$7-m[k]; m[k]+=delta/n[k]; m2[k]+=delta*($7-m[k]); p[k]+=$7*1000/$6}
END{print "phase,api,mode,tool,n,mean_wall_s,mean_ms_per_pass,sd_wall_s,ci95_low_s,ci95_high_s";
for(k in n){printf "%s,%d,%.9f,%.9f",k,n[k],m[k],p[k]/n[k];
if(n[k]>1 && (n[k]-1) in t){sd=sqrt(m2[k]/(n[k]-1)); half=t[n[k]-1]*sd/sqrt(n[k]); printf ",%.9f,%.9f,%.9f\n",sd,m[k]-half,m[k]+half}
else print ",NA,NA,NA"}}' "$D/measurements.csv" > "$D/summary.csv"
COMPLETE=1
if [[ -f $D/unavailable.txt ]]; then echo 'Completed with limitations; read unavailable.txt.' > "$D/STATUS.txt"
else echo 'Completed; review clock audit and logs.' > "$D/STATUS.txt"; fi
echo "Done: $D"
echo 'Send the whole result directory for analysis. No separate Python files are required.'
