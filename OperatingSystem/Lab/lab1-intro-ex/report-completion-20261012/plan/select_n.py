#!/usr/bin/env python3
"""Choose a fixed formal N from a saved, separate 10-round pilot CSV."""

import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics


CONFIGURATIONS = (
    ("read_lseek", "read"), ("read_lseek", "write"),
    ("mmap", "read"), ("mmap", "write"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_requirement(sd, target, student_quantile):
    def sufficient(n):
        return student_quantile(n - 1) * sd / math.sqrt(n) <= target

    if sufficient(2):
        return 2
    high = max(3, math.ceil((1.96 * sd / target) ** 2))
    while not sufficient(high):
        high *= 2
    low = 2
    while high - low > 1:
        middle = (low + high) // 2
        if sufficient(middle):
            high = middle
        else:
            low = middle
    return high


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--analyzer", type=Path, required=True,
                        help="Existing analyze_existing_data.py containing student_quantile")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not all(path.is_file() for path in (args.csv, args.plan, args.analyzer)):
        raise ValueError("Pilot CSV, frozen plan and existing analyzer must already exist")
    spec = importlib.util.spec_from_file_location("saved_data_statistics", args.analyzer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    quantile = module.student_quantile
    with args.csv.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 40:
        raise ValueError("The predeclared pilot requires exactly 40 rows")
    groups = {configuration: [] for configuration in CONFIGURATIONS}
    rounds = {configuration: [] for configuration in CONFIGURATIONS}
    for row in rows:
        configuration = (row["api"], row["mode"])
        if configuration not in groups:
            raise ValueError("Unexpected pilot configuration")
        required = {"iterations": "20", "cache": "warm", "cpu": "2",
                    "exit_code": "0", "cpu_check": "ok", "nodes": "436905"}
        if any(row.get(key) != value for key, value in required.items()):
            raise ValueError("Pilot parameters or validity flags do not match the frozen plan")
        duration = float(row["wall_s"])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("Pilot duration must be finite and positive")
        groups[configuration].append(1000.0 * duration / 20.0)
        rounds[configuration].append(int(row["round"]))
    result = {
        "status": "pilot_completed_formal_N_selected_before_formal_series",
        "pilot_csv": str(args.csv), "pilot_sha256": sha256(args.csv),
        "frozen_plan": str(args.plan), "frozen_plan_sha256": sha256(args.plan),
        "quantile_source": str(args.analyzer), "quantile_source_sha256": sha256(args.analyzer),
        "confidence": 0.95, "relative_halfwidth_target": 0.05,
        "minimum_formal_N": 30, "core": 2, "iterations": 20, "warmup": 2,
        "pilot_included_in_formal_series": False,
        "sample_unit": "process_run_with_20_traversals",
        "outlier_deletions": 0, "groups": [],
    }
    for configuration in CONFIGURATIONS:
        values = groups[configuration]
        if len(values) != 10 or sorted(rounds[configuration]) != list(range(1, 11)):
            raise ValueError("Every configuration requires ten distinct pilot rounds")
        mean = statistics.mean(values)
        sd = statistics.stdev(values)
        target = 0.05 * mean
        requirement = select_requirement(sd, target, quantile)
        result["groups"].append({
            "api": configuration[0], "mode": configuration[1], "pilot_N": 10,
            "mean_ms_per_traversal": mean, "sample_sd_ms_per_traversal": sd,
            "target_halfwidth_ms_per_traversal": target,
            "first_normal_approximation_N": max(2, math.ceil((1.96 * sd / target) ** 2)),
            "student_t_requirement_N": requirement,
        })
    selected_n = max(30, *(group["student_t_requirement_N"] for group in result["groups"]))
    result["selected_formal_N"] = selected_n
    for group in result["groups"]:
        group["pilot_predicted_formal_halfwidth_ms_per_traversal"] = (
            quantile(selected_n - 1) * group["sample_sd_ms_per_traversal"] / math.sqrt(selected_n)
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=True)
        stream.write("\n")
    print(json.dumps({"selected_formal_N": selected_n, "output": str(args.output)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
