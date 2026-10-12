import csv
import hashlib
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "data" / "baseline"
DEST = Path(__file__).resolve().parent


def extract(text, label):
    match = re.search(r"^\s*" + re.escape(label) + r":\s*(.*)$", text, re.M)
    if not match:
        raise ValueError(label)
    return match.group(1)


def elapsed(raw):
    seconds = 0.0
    for item in raw.split(":"):
        seconds = seconds * 60 + float(item)
    return seconds


rows = list(csv.DictReader((SOURCE / "baseline.csv").open(encoding="utf-8")))
summary = []
hashes = {}
for row in rows:
    program = SOURCE / row["program_log"]
    timing = SOURCE / row["time_log"]
    log = program.read_text(encoding="utf-8")
    text = timing.read_text(encoding="utf-8")
    count = log.count("OK (436905 nodes processed)")
    expected = int(row["iterations"])
    flags = ("--write" if row["mode"] == "write" else "")
    if row["cache"] == "no-cache":
        flags += " --no-cache"
    flags = flags.strip()
    command = extract(text, "Command being timed")
    valid = row["exit_code"] == "0" and row["valid"] == "1" and count == expected and extract(text, "Exit status") == "0"
    assert valid, row
    assert all(flag in command for flag in flags.split()), command
    summary.append({
        "topology": row["topology"], "api": row["api"], "mode": row["mode"], "cache": row["cache"],
        "flags": flags or "(none)", "iterations": expected, "nodes_per_iteration": 436905,
        "wall_seconds_time_v": elapsed(extract(text, "Elapsed (wall clock) time (h:mm:ss or m:ss)")),
        "user_seconds": float(extract(text, "User time (seconds)")),
        "system_seconds": float(extract(text, "System time (seconds)")),
        "major_faults": int(extract(text, "Major (requiring I/O) page faults")),
        "minor_faults": int(extract(text, "Minor (reclaiming a frame) page faults")),
        "maximum_rss_kbytes": int(extract(text, "Maximum resident set size (kbytes)")),
        "valid": True, "program_log": row["program_log"], "time_log": row["time_log"]
    })
    for path in (program, timing):
        hashes[str(path.relative_to(SOURCE))] = hashlib.sha256(path.read_bytes()).hexdigest()

expected_combinations = {(t, a, m, c) for t in ("seq", "rand") for a in ("read_lseek", "mmap") for m in ("read", "write") for c in ("warm", "no-cache")}
actual_combinations = {(r["topology"], r["api"], r["mode"], r["cache"]) for r in summary}
assert len(summary) == 16 and actual_combinations == expected_combinations
out = DEST / "baseline-summary.csv"
with out.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

manifest = {
    "source": str(SOURCE), "complete_factorial_combinations": 16, "all_successful": True,
    "repetitions_per_combination": 1, "traversals_per_process": 1,
    "graph_bytes": 10485760, "graph_nodes": 436905, "seed": 427,
    "source_hashes": hashes,
    "time_v_print_resolution_seconds": 0.01,
    "zero_printed_times_do_not_imply_zero_execution_time": True,
    "not_included_in_formal_statistics": True,
    "cache_policy": "Copy original graph, sync, cat before every run. No global cache eviction. --no-cache uses Linux O_DIRECT for read/lseek and advisory madvise plus write msync for mmap.",
    "rows": summary
}
(DEST / "baseline-summary.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"combinations": len(summary), "valid": sum(r["valid"] for r in summary), "csv": str(out)}))
