#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"
[[ -f src/graph_traverse.c ]] || cd ../intro-exp

CORE=${CORE:-2}
BASELINE_ITER=${BASELINE_ITER:-1}
BASELINE_SCOPE=${BASELINE_SCOPE:-full}
BASELINE_TIMEOUT=${BASELINE_TIMEOUT:-180}
EXPECTED_NODES=436905

[[ $BASELINE_SCOPE == full || $BASELINE_SCOPE == variant ]] || { echo "ERROR: BASELINE_SCOPE must be full or variant" >&2; exit 1; }
for name in CORE BASELINE_ITER BASELINE_TIMEOUT; do
  [[ ${!name} =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: Invalid positive integer: $name" >&2; exit 1; }
done
for cmd in gcc python3 taskset timeout /usr/bin/time findmnt; do
  command -v "$cmd" >/dev/null || { echo "ERROR: Missing required tool: $cmd" >&2; exit 1; }
done
taskset -c "$CORE" true
case "$(findmnt -n -o FSTYPE -T .)" in
  9p|drvfs|ntfs|ntfs3|fuseblk) echo "ERROR: Run from the Ubuntu home filesystem" >&2; exit 1 ;;
esac

PREP_DIR="$PWD/results/preparation-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p out "$PREP_DIR/logs"
WORK_GRAPH="$PREP_DIR/graph-work.bin"
cp "$SCRIPT_DIR"/prepare_experiment.sh "$SCRIPT_DIR"/env_snapshot.sh "$PREP_DIR/"
cp ../util/graphgen.py "$PREP_DIR/"
{
  echo "CORE=$CORE BASELINE_ITER=$BASELINE_ITER BASELINE_SCOPE=$BASELINE_SCOPE BASELINE_TIMEOUT=$BASELINE_TIMEOUT"
  echo "Variant=Read/Write,Cache,10M,Seq"
  echo "Formal series: warm page cache, graph-seq.orig.bin, 10 MiB, seed 427"
  echo "Baseline scope full covers sequential/random, read/write, cache/no-cache for both APIs."
  echo "Baseline runs use one iteration; they are exploratory and excluded from the formal series."
  sha256sum src/graph_traverse.c src/graph_traverse_mmap.c src/graph_io.h ../util/graphgen.py
} > "$PREP_DIR/protocol.txt"
gcc -O2 -Wall -o out/graph_traverse src/graph_traverse.c
gcc -O2 -Wall -o out/graph_traverse_mmap src/graph_traverse_mmap.c
python3 ../util/graphgen.py -s 10M --seed 427 --topology sequential --verify -o graph-seq.orig.bin | tee "$PREP_DIR/logs/graph-seq-generator.log"
python3 ../util/graphgen.py -s 10M --seed 427 --topology chain -b 0.5 --min-step-pages 2 -o graph-rand.orig.bin | tee "$PREP_DIR/logs/graph-rand-generator.log"
[[ $(stat -c %s graph-seq.orig.bin) == 10485760 && $(stat -c %s graph-rand.orig.bin) == 10485760 ]] || {
  echo "ERROR: Generated graph size is not 10 MiB." >&2
  exit 1
}

CORE="$CORE" BASELINE_ITER="$BASELINE_ITER" bash "$SCRIPT_DIR/env_snapshot.sh" before "$PREP_DIR"

echo "topology,api,mode,cache,iterations,exit_code,valid,program_log,time_log" > "$PREP_DIR/baseline.csv"
FAILURES=0
run_baseline() {
  local topology=$1 api=$2 mode=$3 cache=$4
  local original bin tag log time_log rc=0 count valid=1 flags=()
  case "$topology" in
    seq) original=graph-seq.orig.bin ;;
    rand) original=graph-rand.orig.bin ;;
  esac
  bin=./out/graph_traverse
  [[ $api != mmap ]] || bin=./out/graph_traverse_mmap
  [[ $mode != write ]] || flags+=(--write)
  [[ $cache != no-cache ]] || flags+=(--no-cache)
  tag="${topology}_${api}_${mode}_${cache}"
  log="$PREP_DIR/logs/${tag}.log"
  time_log="$PREP_DIR/logs/${tag}.time.txt"

  cp "$original" "$WORK_GRAPH"
  sync
  cat "$WORK_GRAPH" >/dev/null
  timeout --kill-after=5s "${BASELINE_TIMEOUT}s" /usr/bin/time -v -o "$time_log" taskset -c "$CORE" "$bin" "${flags[@]}" "$BASELINE_ITER" "$WORK_GRAPH" >"$log" 2>&1 || rc=$?
  count=$(grep -cF "OK ($EXPECTED_NODES nodes processed)" "$log" || true)
  [[ $rc == 0 && $count == "$BASELINE_ITER" ]] || { valid=0; FAILURES=$((FAILURES+1)); }
  echo "$topology,$api,$mode,$cache,$BASELINE_ITER,$rc,$valid,logs/$(basename "$log"),logs/$(basename "$time_log")" >> "$PREP_DIR/baseline.csv"
  echo "Baseline: $tag (valid=$valid)"
}
if [[ $BASELINE_SCOPE == full ]]; then
  for topology in seq rand; do
    for api in read_lseek mmap; do
      for mode in read write; do
        for cache in warm no-cache; do run_baseline "$topology" "$api" "$mode" "$cache"; done
      done
    done
  done
else
  for api in read_lseek mmap; do
    for mode in read write; do run_baseline seq "$api" "$mode" warm; done
  done
fi

CORE="$CORE" bash "$SCRIPT_DIR/env_snapshot.sh" after "$PREP_DIR"
if (( FAILURES > 0 )); then
  echo "Baseline completed with $FAILURES invalid run(s). Review logs before continuing: $PREP_DIR"
  exit 1
fi
echo "Baseline complete: $PREP_DIR"
echo "Next: run run_diagnostics.sh, review the baseline, then complete experiment-plan.md before formal measurement."