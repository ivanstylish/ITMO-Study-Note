set -uo pipefail
cd "$(dirname "$0")"
[[ -f src/graph_traverse.c ]] || cd ../intro-exp      

TAG=${1:?Usage: bash env_snapshot.sh <tag> [output_directory]}
OUT="${2:-.}/meta_${TAG}.txt"
CORE=${CORE:-n/a}

{
  echo "snapshot=$TAG  date=$(date -Is)"
  echo "params: CORE=$CORE N=${N:-?} ITER=${ITER:-?} WARMUP=${WARMUP:-?}"
  echo "--- os-release ---";   cat /etc/os-release
  echo "--- uname ---";        uname -a
  echo "--- gcc ---";          gcc --version | head -1
  echo "--- lscpu ---";        lscpu
  echo "--- lscpu -e ---";     lscpu -e
  echo "--- nproc ---";        nproc
  echo "--- free -h ---";      free -h
  echo "--- page size ---";    getconf PAGESIZE
  echo "--- lsblk ---";        lsblk -o NAME,TYPE,SIZE,ROTA,MODEL,MOUNTPOINTS 2>/dev/null || echo n/a
  echo "--- Filesystem containing experiment files ---"; findmnt -T . 2>/dev/null || echo n/a
  echo "--- CPU governor (core $CORE) ---"
  cat /sys/devices/system/cpu/cpu"$CORE"/cpufreq/scaling_governor 2>/dev/null || echo "n/a (cpufreq is usually unavailable in WSL2)"
  echo "--- uptime ---";       uptime
  echo "--- top ---";          top -bn1 | head -15
  echo "--- SHA-256: programs, data, scripts ---"
  sha256sum src/graph_traverse.c src/graph_traverse_mmap.c src/graph_io.h ../util/graphgen.py \
            graph-seq.orig.bin out/graph_traverse out/graph_traverse_mmap 2>/dev/null || echo n/a
} > "$OUT" 2>&1

echo "Environment snapshot saved to $OUT"
