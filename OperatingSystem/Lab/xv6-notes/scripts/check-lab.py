#!/usr/bin/env python3
"""Reproduce each lab's functional checks or the school's full regression tests."""

import argparse
from pathlib import Path
import subprocess
import sys


LOGS = Path("/lab-notes/logs")
QEMU = [sys.executable, "/lab-notes/scripts/check-qemu.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", choices=("intro", "shebang"))
    parser.add_argument("mode", choices=("functional", "regression"))
    args = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)

    def run(label, command, marker=None):
        print(f"RUN: {args.project} {label}", flush=True)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        path = LOGS / f"{args.project}-recheck-{label}.log"
        path.write_bytes(result.stdout)
        if result.returncode or (marker and marker.encode() not in result.stdout):
            print(result.stdout.decode("utf-8", errors="replace"), flush=True)
            raise RuntimeError(f"{label} failed, exit {result.returncode}, log: {path}")
        print(f"PASS: {label}, log: {path}", flush=True)

    run("build", ["make", "-j2", "kernel/kernel", "fs.img"])
    if args.mode == "regression":
        run("usertests", ["timeout", "900s", sys.executable, "test-xv6.py", "usertests"],
            "ALL TESTS PASSED")
        run("crash", ["timeout", "900s", sys.executable, "test-xv6.py", "crash"])
        return

    run("format", ["make", "fmt-check"])
    if args.project == "intro":
        run("official", ["timeout", "60s", "sh", "ci/test/run.sh", "dumptests", "dump2tests"],
            "You are cool!")
        run("extra", QEMU + ["command", "--command", "dump2extra", "--expect",
            "ALL DUMP2 EXTRA TESTS PASSED", "--log", str(LOGS / "intro-recheck-extra-qemu.log")],
            "ALL DUMP2 EXTRA TESTS PASSED")
        run("pingpong", QEMU + ["pingpong", "--runs", "10", "--log",
            str(LOGS / "intro-recheck-pingpong-qemu.log")], "run 10/10")
    else:
        run("functional", QEMU + ["command", "--command", "shebangtests", "--expect",
            "ALL SHEBANG TESTS PASSED (41 cases)", "--timeout", "120", "--log",
            str(LOGS / "shebang-recheck-functional-qemu.log")],
            "ALL SHEBANG TESTS PASSED (41 cases)")


if __name__ == "__main__":
    main()
