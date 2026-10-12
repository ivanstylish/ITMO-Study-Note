import csv
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

DEST_ROOT = Path(__file__).resolve().parents[1]
T95_DF2 = 4.302652729749464


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Work only with the saved local attachments; historical folders are not needed.
manifest_path = DEST_ROOT / "data" / "auxiliary-source-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for entry in manifest["copied_files"]:
    copied = DEST_ROOT / entry["destination"]
    assert copied.is_file() and copied.stat().st_size == entry["bytes"]
    assert sha(copied) == entry["sha256"], copied


def rows(alias, name):
    with (DEST_ROOT / "data" / alias / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def interval(values):
    values = list(values)
    n = len(values)
    assert n == 3
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = T95_DF2 * sd / math.sqrt(n)
    return {"n": n, "mean": mean, "sample_sd": sd, "ci95_half_width": half, "ci95_lower": mean - half, "ci95_upper": mean + half}


def save_csv(name, items):
    with (DEST_ROOT / "analysis" / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)


def extract(text, label):
    match = re.search(r"^\s*" + re.escape(label) + r":\s*(.*)$", text, re.M)
    assert match, label
    return match.group(1)


diagnostics = rows("diagnostics", "measurements.csv")
assert len(diagnostics) == 48
groups = defaultdict(list)
for row in diagnostics:
    assert row["phase"] == "tools" and row["exit_code"] == "0" and row["valid"] == "1" and row["iterations"] == "1"
    log = (DEST_ROOT / "data" / "diagnostics" / row["log"]).read_text(encoding="utf-8")
    assert log.count("OK (436905 nodes processed)") == 1
    groups[(row["api"], row["mode"], row["tool"])].append(row)
assert len(groups) == 16 and all(len(g) == 3 for g in groups.values())
tool_summary = []
for (api, mode, tool), items in sorted(groups.items()):
    stat = interval(float(row["wall_s"]) for row in items)
    bare_by_rep = {row["rep"]: float(row["wall_s"]) for row in groups[(api, mode, "bare")]}
    paired = interval(float(row["wall_s"]) - bare_by_rep[row["rep"]] for row in items)
    ratio = stat["mean"] / statistics.mean(bare_by_rep.values())
    tool_summary.append({"api": api, "mode": mode, "tool": tool, "iterations": 1, **stat, "ratio_of_means_to_bare": ratio,
                         "paired_tool_minus_bare_mean_s": paired["mean"], "paired_tool_minus_bare_ci95_lower_s": paired["ci95_lower"],
                         "paired_tool_minus_bare_ci95_upper_s": paired["ci95_upper"]})
save_csv("auxiliary-tools-summary.csv", tool_summary)

resource_summary = []
syscall_summary = []
perf_summary = []
for api in ("read_lseek", "mmap"):
    for mode in ("read", "write"):
        row = next(r for r in groups[(api, mode, "time_v")] if r["rep"] == "1")
        path = DEST_ROOT / "data" / "diagnostics" / row["log"].replace(".log", ".time.txt")
        text = path.read_text(encoding="utf-8")
        resource_summary.append({"api": api, "mode": mode, "rep": 1, "iterations": 1,
                                 "wall_outer_mono_s": float(row["wall_s"]),
                                 "user_s": float(extract(text, "User time (seconds)")), "system_s": float(extract(text, "System time (seconds)")),
                                 "maximum_rss_kbytes": int(extract(text, "Maximum resident set size (kbytes)")),
                                 "major_faults": int(extract(text, "Major (requiring I/O) page faults")),
                                 "minor_faults": int(extract(text, "Minor (reclaiming a frame) page faults")),
                                 "voluntary_context_switches": int(extract(text, "Voluntary context switches")),
                                 "involuntary_context_switches": int(extract(text, "Involuntary context switches"))})
        for row in groups[(api, mode, "strace")]:
            path = DEST_ROOT / "data" / "diagnostics" / row["log"].replace(".log", ".strace.txt")
            calls = {}
            for line in path.read_text(encoding="utf-8").splitlines():
                fields = line.split()
                if len(fields) in (5, 6) and re.fullmatch(r"\d+\.\d+", fields[0]):
                    calls[fields[-1]] = int(fields[3])
            syscall_summary.append({"api": api, "mode": mode, "rep": int(row["rep"]), "iterations": 1,
                                    **{name + "_calls": calls.get(name, 0) for name in ("read", "write", "lseek", "mmap", "munmap", "total")}})
        for row in groups[(api, mode, "perf")]:
            path = DEST_ROOT / "data" / "diagnostics" / row["log"].replace(".log", ".perf.txt")
            text = path.read_text(encoding="utf-8")
            result = {"api": api, "mode": mode, "rep": int(row["rep"]), "iterations": 1,
                      "outer_wall_mono_s": float(row["wall_s"]), "hardware_cache_misses_supported": False,
                      "event_scope": "user-only (:u)"}
            for label in ("context-switches", "cpu-migrations", "page-faults"):
                match = re.search(r"^\s*([\d,]+)\s+" + re.escape(label) + r":u\s", text, re.M)
                assert match, label
                result[label.replace("-", "_") + "_u"] = int(match.group(1).replace(",", ""))
            assert re.search(r"<not supported>\s+cache-misses:u", text)
            perf_summary.append(result)
save_csv("auxiliary-time-v-resources.csv", resource_summary)
save_csv("auxiliary-strace-counts.csv", syscall_summary)
save_csv("auxiliary-perf-software-events.csv", perf_summary)

background = rows("background", "load.csv")
measurement_background = [r for r in rows("background", "measurements.csv") if r["phase"] in ("quiet", "stress")]
assert len(background) == len(measurement_background) == 12
background_groups = defaultdict(list)
for row in background:
    assert row["iterations"] == "20"
    matches = [r for r in measurement_background if r["api"] == row["api"] and r["phase"] == row["condition"] and r["rep"] == row["rep"]]
    assert len(matches) == 1
    r = matches[0]
    assert r["mode"] == "read" and r["tool"] == "resource" and r["valid"] == "1" and r["exit_code"] == "0"
    assert float(r["wall_s"]) == float(row["wall_s"])
    log = (DEST_ROOT / "data" / "background" / r["log"]).read_text(encoding="utf-8")
    assert log.count("OK (436905 nodes processed)") == 20
    background_groups[(row["api"], row["condition"])].append(row)
background_summary = []
for (api, condition), items in sorted(background_groups.items()):
    stat = interval(float(r["wall_s"]) for r in items)
    background_summary.append({"api": api, "condition": condition, "iterations": 20, **stat,
                               **{"mean_" + field: statistics.mean(float(r[field]) for r in items) for field in ("user_s", "sys_s", "vol_ctx", "invol_ctx", "minflt", "majflt")}})
save_csv("auxiliary-background-summary.csv", background_summary)
background_paired = []
for api in ("read_lseek", "mmap"):
    quiet = {r["rep"]: r for r in background_groups[(api, "quiet")]}
    stress = {r["rep"]: r for r in background_groups[(api, "stress")]}
    stat = interval(float(stress[rep]["wall_s"]) - float(quiet[rep]["wall_s"]) for rep in quiet)
    ratio = statistics.mean(float(r["wall_s"]) for r in stress.values()) / statistics.mean(float(r["wall_s"]) for r in quiet.values())
    background_paired.append({"api": api, "iterations": 20, **stat, "stress_to_quiet_ratio_of_means": ratio,
                              "mean_involuntary_context_switch_difference": statistics.mean(int(stress[rep]["invol_ctx"]) - int(quiet[rep]["invol_ctx"]) for rep in quiet)})
save_csv("auxiliary-background-paired.csv", background_paired)

def clocks(rows_to_check):
    diffs = [abs(float(r["wall_s"]) - float(r["realtime_s"])) for r in rows_to_check]
    return {"rows": len(diffs), "real_minus_mono_abs_over_1ms": sum(d > 0.001 for d in diffs), "max_absolute_difference_s": max(diffs)}

summary = {
    "confidence": {"level": 0.95, "distribution": "two-sided Student t", "df": 2, "t_0_975": T95_DF2, "formula": "mean +/- t*s/sqrt(n)", "outliers_removed": 0},
    "diagnostics": {"rows": 48, "configs": 4, "tools": 4, "n_per_condition": 3, "traversals_per_process": 1,
                    "warmup": "one uncounted quiet 20-traversal read run per API",
                    "timer_scope": "outer Python monotonic timer encloses timeout + taskset + tool + program; preparation and 0.2 s delay excluded",
                    "cache": "copy original sequential 10 MiB graph, sync, cat, no --no-cache",
                    "order": "tool order rotates by repeat within each configuration",
                    "counts_include": "strace startup, runtime and program syscalls; tracing changes scheduling and execution time",
                    "hardware_perf_counters_unavailable": ["cache-misses:u"], "perf_scope": "available software events restricted to user execution (:u), not equivalent to unrestricted time-v totals",
                    "clock_audit": clocks(diagnostics), "tool_summary": tool_summary, "time_v_rep_1": resource_summary,
                    "strace": syscall_summary, "perf": perf_summary},
    "background": {"rows": 12, "n_per_api_condition": 3, "n_pairs_per_api": 3, "traversals_per_process": 20,
                   "mode": "read only, both APIs", "load": "one CPU busy-loop process pinned to the same logical processor 2",
                   "load_started": "after graph preparation, before the measured child; no injected I/O/memory load",
                   "timer_scope": "outer monotonic timer encloses timeout + taskset + time resource wrapper + program",
                   "order": "quiet/stress order alternates by paired repetition",
                   "clock_audit": clocks(measurement_background), "summary": background_summary, "paired": background_paired},
    "baseline": json.loads((DEST_ROOT / "analysis" / "baseline-summary.json").read_text(encoding="utf-8")),
    "comparison_between_historical_corpora": False,
    "source_manifest": "data/auxiliary-source-manifest.json"
}
(DEST_ROOT / "analysis" / "auxiliary-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"copied_files": len(manifest["copied_files"]), "valid_tool_rows": len(diagnostics), "valid_background_rows": len(background), "summary": str(DEST_ROOT / "analysis" / "auxiliary-summary.json")}))
