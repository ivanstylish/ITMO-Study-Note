#!/usr/bin/env bash
set -euo pipefail

project='/mnt/d/Study-Note/OperatingSystem/Lab/lab2-fuse-musicfs'
python='/home/ivanstylish/venvs/musicfs/bin/python'
mountpoint='/home/ivanstylish/musicfs-mount'

fail() { printf 'MusicFS: %s\n' "$*" >&2; exit 1; }

[[ $# -eq 0 ]] || fail 'Run without arguments.'
[[ -x "$python" ]] || fail "Python not found: $python"
[[ -c /dev/fuse && -r /dev/fuse && -w /dev/fuse ]] || fail '/dev/fuse must be a readable, writable character device.'
command -v findmnt >/dev/null || fail 'findmnt is required (Ubuntu package: util-linux).'
command -v fusermount3 >/dev/null || fail 'fusermount3 is required (Ubuntu package: fuse3).'
cd -- "$project"
[[ -r local-data/metadata.json && -d /mnt/e ]] || fail 'Need local-data/metadata.json and the audio source root /mnt/e.'
"$python" -c 'import pyfuse3, trio' || fail "Dependencies missing. Install once: $python -m pip install -e $project"

[[ ! -L "$mountpoint" ]] || fail "Mountpoint is a symlink: $mountpoint"
if findmnt --mountpoint "$mountpoint" >/dev/null; then
    fail "Already mounted: $mountpoint. Inspect it first; no automatic unmount was attempted."
fi
if [[ ! -e "$mountpoint" ]]; then
    mkdir -- "$mountpoint"
fi
[[ -d "$mountpoint" && -r "$mountpoint" && -w "$mountpoint" && -x "$mountpoint" ]] || fail "Mountpoint must be an accessible, writable directory: $mountpoint"
entry=$(find "$mountpoint" -mindepth 1 -maxdepth 1 -print -quit)
[[ -z "$entry" ]] || fail "Mountpoint is not empty: $mountpoint"

"$python" - "$mountpoint" <<'PY'
import sys
from pathlib import Path
from musicfs.catalog import Catalog
from musicfs.__main__ import validate_mountpoint

catalog = Catalog(Path('local-data/metadata.json'), Path('/mnt/e'))
validate_mountpoint(Path(sys.argv[1]), catalog.source_root)
if not catalog.file_count:
    raise SystemExit('MusicFS: No readable audio files; check /mnt/e and metadata paths.')
print(f'MusicFS: {catalog.file_count} readable audio files.', flush=True)
PY

printf 'Mounting at %s\nKeep this terminal open. Press Ctrl+C here to stop and unmount.\n' "$mountpoint"
# Python owns signal handling and unmounts only the filesystem it starts.
exec "$python" -m musicfs --metadata local-data/metadata.json --source-root /mnt/e "$mountpoint"
