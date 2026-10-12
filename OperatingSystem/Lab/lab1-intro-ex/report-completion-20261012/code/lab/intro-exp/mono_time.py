#!/usr/bin/env python3
# Measure process duration with monotonic time; retain other clocks for audit.
import subprocess, sys, time
wall_file, cmd = sys.argv[1], sys.argv[2:]
real0 = time.time_ns()
raw0 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
mono0 = time.monotonic_ns()
rc = subprocess.call(cmd)
mono1 = time.monotonic_ns()
raw1 = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
real1 = time.time_ns()
wall = (mono1 - mono0) / 1e9
with open(wall_file, 'w') as handle:
    handle.write(f'{wall:.9f}')
print(f'CLOCK realtime_s={(real1-real0)/1e9:.9f} monotonic_s={wall:.9f} monotonic_raw_s={(raw1-raw0)/1e9:.9f}', flush=True)
print(f'CLOCK_NS realtime_start={real0} realtime_end={real1} monotonic_start={mono0} monotonic_end={mono1} raw_start={raw0} raw_end={raw1}', flush=True)
sys.exit(rc)
