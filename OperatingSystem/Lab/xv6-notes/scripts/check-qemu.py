#!/usr/bin/env python3
"""Check an actual xv6 shell session, with bounded waits and a saved transcript."""

import argparse
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "pingpong", "command", "demo"))
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--command")
    parser.add_argument("--expect")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.mode == "command" and (not args.command or not args.expect):
        parser.error("command mode needs --command and --expect")

    transcript = bytearray()
    proc = subprocess.Popen(
        ["make", "qemu", "CPUS=3"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)

    def read_until_prompt(start):
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            if selector.select(timeout=0.25):
                data = os.read(proc.stdout.fileno(), 65536)
                if not data:
                    raise RuntimeError("QEMU exited before returning to the shell")
                transcript.extend(data)
                segment = bytes(transcript[start:])
                if b"panic:" in segment:
                    raise RuntimeError("xv6 kernel panic")
                if segment.endswith(b"$ "):
                    return segment.decode("utf-8", errors="replace")
            if proc.poll() is not None:
                raise RuntimeError(f"make qemu exited with status {proc.returncode}")
        raise TimeoutError(f"xv6 did not return to its shell within {args.timeout} seconds")

    def command(text):
        start = len(transcript)
        proc.stdin.write(text.encode("ascii") + b"\n")
        proc.stdin.flush()
        return read_until_prompt(start)

    try:
        boot = read_until_prompt(0)
        if "init: starting sh" not in boot:
            raise RuntimeError("xv6 shell startup message was not found")
        if "-smp 3" not in boot:
            raise RuntimeError("QEMU did not start with the expected 3 CPUs")
        response = command("echo ENVIRONMENT_OK")
        if not re.search(r"^ENVIRONMENT_OK\r?$", response, re.MULTILINE):
            raise RuntimeError("xv6 echo did not produce the expected output")
        print("PASS: xv6 boot and echo", flush=True)

        if args.mode == "pingpong":
            size = re.search(
                r"^#define PIPESIZE (\d+)$",
                Path("kernel/pipe.c").read_text(),
                re.MULTILINE,
            ).group(1)
            for attempt in range(args.runs):
                response = command("pingpong")
                messages = re.findall(
                    r"^(\d+): got (ping|pong)\r?$", response, re.MULTILINE
                )
                if len(messages) != 2:
                    raise RuntimeError(f"incorrect pingpong output: {response!r}")
                if messages[0][1] != "ping" or messages[1][1] != "pong":
                    raise RuntimeError(f"incorrect message order: {response!r}")
                if messages[0][0] == messages[1][0]:
                    raise RuntimeError("parent and child PIDs must differ")
                expected = [
                    "pingpong",
                    f"{messages[0][0]}: got ping",
                    f"{messages[1][0]}: got pong",
                    "$ ",
                ]
                if response.replace("\r", "").splitlines() != expected:
                    raise RuntimeError(f"unexpected pingpong output: {response!r}")
                print(
                    f"PASS: PIPESIZE={size}, run {attempt + 1}/{args.runs}, "
                    f"child={messages[0][0]}, parent={messages[1][0]}",
                    flush=True,
                )

        if args.mode == "command":
            response = command(args.command)
            if args.expect not in response.replace("\r", "").splitlines():
                raise RuntimeError(f"expected success marker was not found: {response!r}")
            if "[FAIL]" in response or "usertrap():" in response:
                raise RuntimeError(f"unexpected failure output: {response!r}")
            print(response, end="", flush=True)
            print(f"PASS: {args.command}", flush=True)

        if args.mode == "demo":
            print(command("echo #!/echo INTERPRETER_OK > sbdemo"), end="", flush=True)
            response = command("sbdemo hello xv6")
            if "INTERPRETER_OK sbdemo hello xv6" not in response.replace("\r", "").splitlines():
                raise RuntimeError(f"shebang demonstration failed: {response!r}")
            print(response, end="", flush=True)
            command("rm sbdemo")
            print("PASS: shebang demonstration", flush=True)

        proc.stdin.write(b"\x01x")
        proc.stdin.flush()
        proc.wait(timeout=10)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and selector.select(timeout=0.25):
            data = os.read(proc.stdout.fileno(), 65536)
            if not data:
                break
            transcript.extend(data)
        if proc.returncode != 0:
            raise RuntimeError(f"make qemu exited with status {proc.returncode}")
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        if proc.poll() is None:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
        selector.close()
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_bytes(transcript)
        print(f"Transcript: {args.log}", flush=True)


if __name__ == "__main__":
    main()
