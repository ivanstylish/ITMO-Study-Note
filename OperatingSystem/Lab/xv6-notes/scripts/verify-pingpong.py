#!/usr/bin/env python3
"""Run Pingpong with normal and one-byte pipes, then restore the original kernel."""

import hashlib
from pathlib import Path
import subprocess
import sys


LOGS = Path("/lab-notes/logs")
PIPE = Path("kernel/pipe.c")


def build(label):
    result = subprocess.run(
        ["make", "-j2", "-W", "kernel/pipe.c", "kernel/kernel", "fs.img"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (LOGS / f"{label}-build.log").write_bytes(result.stdout)
    if result.returncode:
        sys.stdout.buffer.write(result.stdout)
        result.check_returncode()
    if b"-o kernel/pipe.o kernel/pipe.c" not in result.stdout:
        raise RuntimeError("the pipe implementation was not rebuilt")
    print(f"PASS: {label} build, kernel/pipe.o rebuilt", flush=True)


def check(label, runs):
    result = subprocess.run(
        [
            sys.executable,
            "/lab-notes/scripts/check-qemu.py",
            "pingpong",
            "--runs",
            str(runs),
            "--log",
            str(LOGS / f"{label}-qemu.log"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (LOGS / f"{label}-result.log").write_bytes(result.stdout)
    print(result.stdout.decode("utf-8", errors="replace"), end="", flush=True)
    result.check_returncode()


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    original = PIPE.read_bytes()
    marker = b"#define PIPESIZE 512"
    if original.count(marker) != 1:
        raise RuntimeError("expected exactly one default PIPESIZE=512 definition")

    try:
        build("pipe-512-initial")
        check("pipe-512-initial", 10)
        PIPE.write_bytes(original.replace(marker, b"#define PIPESIZE 1"))
        build("pipe-1")
        check("pipe-1", 20)
    finally:
        PIPE.write_bytes(original)
        if PIPE.read_bytes() != original:
            raise RuntimeError("kernel/pipe.c was not restored")
        digest = hashlib.sha256(original).hexdigest()
        (LOGS / "pipe-restored.sha256").write_text(f"{digest}  kernel/pipe.c\n")
        build("pipe-512-restored")
        print("PASS: original kernel/pipe.c restored exactly", flush=True)

    check("pipe-512-restored", 10)
    print("PASS: all 40 Pingpong runs completed with 3 virtual CPUs", flush=True)


if __name__ == "__main__":
    main()
