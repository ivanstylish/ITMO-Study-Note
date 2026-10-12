#!/usr/bin/env bash
# env_snapshot.sh <tag> [output directory]  -- 环境快照（паспорт системы），写入 <输出目录>/meta_<tag>.txt
# 例：bash env_snapshot.sh before results/series-xxx
# 不用 set -e：WSL 里有些命令/文件可能不存在，缺失就显示 n/a，不能因此中断实验。
set -uo pipefail
cd "$(dirname "$0")"
[[ -f src/graph_traverse.c ]] || cd ../intro-exp      # 定位到 lab/intro-exp

TAG=${1:?Usage: bash env_snapshot.sh <tag> [output directory]}
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
  echo "--- Lab filesystem ---"; findmnt -T . 2>/dev/null || echo n/a
  echo "--- CPU governor (core $CORE) ---"
  cat /sys/devices/system/cpu/cpu"$CORE"/cpufreq/scaling_governor 2>/dev/null || echo "n/a (WSL2 usually does not expose cpufreq)"
  echo "--- uptime ---";       uptime
  echo "--- top ---";          top -bn1 | head -15
  echo "--- SHA-256: executables, data, and scripts ---"
  sha256sum src/graph_traverse.c src/graph_traverse_mmap.c src/graph_io.h ../util/graphgen.py \
            graph-seq.orig.bin out/graph_traverse out/graph_traverse_mmap 2>/dev/null || echo n/a
} > "$OUT" 2>&1

echo "Environment snapshot written to $OUT"
