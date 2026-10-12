#!/usr/bin/env bash
# Run a planned phase and record its position in the execution ledger.
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"
ROOT_DIR=$(cd ../../.. && pwd)
PHASE=${1:?Usage: bash run_phase.sh pilot|formal}
export PHASE
export CORE=${CORE:-2} ITER=${ITER:-20} WARMUP=${WARMUP:-2}
python3 - "$ROOT_DIR" "$PHASE" <<'PY'
from pathlib import Path
import hashlib, json, os, subprocess, sys, time
root, phase = Path(sys.argv[1]), sys.argv[2]
plan = root / 'plan/frozen-before-pilot-ru.md'
assert plan.is_file(), 'ERROR: Frozen plan is missing.'
assert phase in ('pilot', 'formal'), 'ERROR: Unknown phase.'
assert (os.environ['CORE'],os.environ['ITER'],os.environ['WARMUP']) == ('2','20','2'), 'ERROR: Parameters differ from the frozen plan.'
ledger = root / 'plan/execution-ledger.jsonl'
def event(kind, **extra):
    row = {'event':kind,'monotonic_ns':time.monotonic_ns(),'monotonic_raw_ns':time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW),'realtime_ns':time.time_ns(),**extra}
    with ledger.open('a',encoding='utf-8') as handle:
        handle.write(json.dumps(row)+'\n')
if phase == 'pilot':
    assert os.environ.get('N') == '10', 'ERROR: Pilot must use N=10.'
else:
    selection = json.loads((root/'plan/selected-n.json').read_text(encoding='utf-8'))
    chosen = selection['selected_formal_N']
    assert str(chosen) == os.environ.get('N'), 'ERROR: Formal N differs from the locked selection.'
event(phase+'_started',N=int(os.environ['N']),plan_sha256=hashlib.sha256(plan.read_bytes()).hexdigest())
real0, mono0, raw0 = time.time_ns(),time.monotonic_ns(),time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
rc = subprocess.call(['bash','run_series.sh'])
raw1, mono1, real1 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW),time.monotonic_ns(),time.time_ns()
timing={'phase':phase,'N':int(os.environ['N']),'exit_code':rc,'monotonic_s':(mono1-mono0)/1e9,'monotonic_raw_s':(raw1-raw0)/1e9,'realtime_s':(real1-real0)/1e9,'scope':'Whole phase including compilation, graph generation, warmups, preparation and snapshots.'}
(root/'plan'/('whole-'+phase+'-timing.json')).write_text(json.dumps(timing,indent=2),encoding='utf-8')
event(phase+'_completed',exit_code=rc,monotonic_s=timing['monotonic_s'])
sys.exit(rc)
PY
