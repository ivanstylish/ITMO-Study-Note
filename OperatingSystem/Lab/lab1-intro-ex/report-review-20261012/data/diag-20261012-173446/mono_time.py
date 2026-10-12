#!/usr/bin/env python3
# mono_time.py WALLFILE 命令...
# 用单调时钟（不受系统时间校准影响）给命令计时：wall 秒数写入 WALLFILE，退出码 = 命令的退出码。
import subprocess, sys, time

wall_file, cmd = sys.argv[1], sys.argv[2:]
t0 = time.monotonic_ns()
rc = subprocess.call(cmd)
t1 = time.monotonic_ns()
with open(wall_file, "w") as f:
    f.write(f"{(t1 - t0) / 1e9:.6f}")
sys.exit(rc)
