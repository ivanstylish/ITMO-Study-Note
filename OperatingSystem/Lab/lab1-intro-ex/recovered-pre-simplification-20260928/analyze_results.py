#!/usr/bin/env python3
"""Validate, summarize, compare, and plot the four formal experiment series."""
import argparse
import csv
import html
import math
import statistics
from pathlib import Path

GROUPS = [
    ("read_lseek", "read"),
    ("read_lseek", "write"),
    ("mmap", "read"),
    ("mmap", "write"),
]
EXPECTED_NODES = 436905
T95 = {
    2: 12.706204736, 3: 4.302652730, 4: 3.182446305,
    5: 2.776445105, 6: 2.570581836, 7: 2.446911851,
    8: 2.364624252, 9: 2.306004135, 10: 2.262157163,
    11: 2.228138852, 12: 2.200985160, 13: 2.178812830,
    14: 2.160368656, 15: 2.144786688, 16: 2.131449546,
    17: 2.119905299, 18: 2.109815578, 19: 2.100922040,
    20: 2.093024054, 21: 2.085963447, 22: 2.079613845,
    23: 2.073873068, 24: 2.068657610, 25: 2.063898562,
    26: 2.059538553, 27: 2.055529439, 28: 2.051830516,
    29: 2.048407142, 30: 2.045229642,
}
COLORS = ["#2864a5", "#c45735", "#36825a", "#8a5bb5"]


def t_critical_95(n):
    if n in T95:
        return T95[n]
    df = n - 1
    z = 1.959963984540054
    z2 = z * z
    return (
        z
        + (z * z2 + z) / (4 * df)
        + (5 * z * z2 * z2 + 16 * z * z2 + 3 * z) / (96 * df * df)
        + (3 * z * z2 * z2 * z2 + 19 * z * z2 * z2 + 17 * z * z2 - 15 * z)
        / (384 * df * df * df)
    )


def quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def load_rows(path):
    required = {
        "round", "api", "mode", "graph", "iterations", "wall_s",
        "exit_code", "cpu_check", "nodes",
    }
    groups = {key: {} for key in GROUPS}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing CSV columns: " + ", ".join(sorted(missing)))
        for line_number, row in enumerate(reader, start=2):
            try:
                key = (row["api"], row["mode"])
                if key not in groups:
                    raise ValueError("unexpected api/mode pair " + repr(key))
                if row["graph"] != "graph-seq.bin":
                    raise ValueError("unexpected graph " + repr(row["graph"]))
                round_number = int(row["round"])
                iterations = int(row["iterations"])
                nodes = int(row["nodes"])
                exit_code = int(row["exit_code"])
                wall_s = float(row["wall_s"])
                if round_number < 1 or iterations < 1 or wall_s <= 0:
                    raise ValueError("invalid round, iteration count, or wall time")
                if exit_code != 0 or nodes != EXPECTED_NODES:
                    raise ValueError("failed run or unexpected node count")
                if round_number in groups[key]:
                    raise ValueError("duplicate configuration in round " + str(round_number))
                groups[key][round_number] = {
                    "ms": wall_s * 1000 / iterations,
                    "cpu_check": row["cpu_check"].strip().lower(),
                }
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid data row {line_number}: {exc}") from exc

    round_sets = [set(groups[key]) for key in GROUPS]
    if any(len(rounds) < 2 for rounds in round_sets):
        raise ValueError("Each of the four series must have at least two successful measurements.")
    if any(rounds != round_sets[0] for rounds in round_sets[1:]):
        raise ValueError("The four series do not contain the same rounds; inspect the raw CSV.")
    return {key: [groups[key][r] | {"round": r} for r in sorted(groups[key])] for key in GROUPS}


def summarize(values):
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = t_critical_95(n) * sd / math.sqrt(n)
    median = statistics.median(values)
    iqr = quantile(values, 0.75) - quantile(values, 0.25)
    target_half = 0.05 * mean
    estimated_n = max(2, math.ceil((1.96 * sd / target_half) ** 2)) if sd else 2
    while sd and t_critical_95(estimated_n) * sd / math.sqrt(estimated_n) > target_half:
        estimated_n += 1
    return {
        "n": n, "mean": mean, "sd": sd, "low": mean - half,
        "high": mean + half, "half": half,
        "relative_half_pct": 100 * half / mean if mean else 0,
        "median": median, "iqr": iqr, "estimated_n_5pct": estimated_n,
    }


def write_summary(out_dir, groups):
    fields = [
        "api", "mode", "n", "mean_ms_per_pass", "sd_ms_per_pass",
        "ci95_low_ms", "ci95_high_ms", "ci95_halfwidth_ms",
        "relative_halfwidth_pct", "median_ms_per_pass", "iqr_ms",
        "cpu_check_bad_count", "estimated_n_for_5pct_halfwidth",
    ]
    summaries = {}
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for key in GROUPS:
            rows = groups[key]
            values = [row["ms"] for row in rows]
            stats = summarize(values)
            summaries[key] = stats
            writer.writerow({
                "api": key[0], "mode": key[1], "n": stats["n"],
                "mean_ms_per_pass": f'{stats["mean"]:.9f}',
                "sd_ms_per_pass": f'{stats["sd"]:.9f}',
                "ci95_low_ms": f'{stats["low"]:.9f}',
                "ci95_high_ms": f'{stats["high"]:.9f}',
                "ci95_halfwidth_ms": f'{stats["half"]:.9f}',
                "relative_halfwidth_pct": f'{stats["relative_half_pct"]:.4f}',
                "median_ms_per_pass": f'{stats["median"]:.9f}',
                "iqr_ms": f'{stats["iqr"]:.9f}',
                "cpu_check_bad_count": sum(row["cpu_check"] == "bad" for row in rows),
                "estimated_n_for_5pct_halfwidth": stats["estimated_n_5pct"],
            })
    return summaries


def write_comparisons(out_dir, groups):
    fields = [
        "api", "n_pairs", "mean_write_minus_read_ms", "sd_paired_difference_ms",
        "ci95_low_difference_ms", "ci95_high_difference_ms",
        "mean_read_ms", "write_change_percent_of_read",
    ]
    results = {}
    with (out_dir / "comparisons.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for api in ("read_lseek", "mmap"):
            reads = {row["round"]: row["ms"] for row in groups[(api, "read")]}
            writes = {row["round"]: row["ms"] for row in groups[(api, "write")]}
            differences = [writes[r] - reads[r] for r in sorted(reads)]
            n = len(differences)
            mean = statistics.mean(differences)
            sd = statistics.stdev(differences)
            half = t_critical_95(n) * sd / math.sqrt(n)
            read_mean = statistics.mean(reads.values())
            result = {
                "n": n, "mean": mean, "sd": sd,
                "low": mean - half, "high": mean + half,
                "read_mean": read_mean,
                "percent": 100 * mean / read_mean if read_mean else 0,
            }
            results[api] = result
            writer.writerow({
                "api": api, "n_pairs": n,
                "mean_write_minus_read_ms": f'{mean:.9f}',
                "sd_paired_difference_ms": f'{sd:.9f}',
                "ci95_low_difference_ms": f'{mean-half:.9f}',
                "ci95_high_difference_ms": f'{mean+half:.9f}',
                "mean_read_ms": f'{read_mean:.9f}',
                "write_change_percent_of_read": f'{result["percent"]:.4f}',
            })
    return results


def write_ci_svg(path, summaries):
    width, height = 1050, 390
    left, right, top = 300, 965, 82
    labels = [f"{api} / {mode}" for api, mode in GROUPS]
    maximum = max(summaries[key]["high"] for key in GROUPS)
    upper = maximum * 1.12 if maximum else 1.0

    def xcoord(value):
        return left + value / upper * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="525" y="32" text-anchor="middle" font-family="sans-serif" font-size="20">Mean traversal time with 95% CI</text>',
    ]
    for tick in range(6):
        value = upper * tick / 5
        x = xcoord(value)
        parts.append(f'<line x1="{x:.1f}" y1="58" x2="{x:.1f}" y2="320" stroke="#dddddd"/>')
        parts.append(f'<text x="{x:.1f}" y="346" text-anchor="middle" font-family="sans-serif" font-size="12">{value:.2f}</text>')
    for index, key in enumerate(GROUPS):
        stats = summaries[key]
        y = top + index * 64
        color = COLORS[index]
        parts.append(f'<text x="20" y="{y+5}" font-family="sans-serif" font-size="14">{html.escape(labels[index])}</text>')
        parts.append(f'<line x1="{xcoord(stats["low"]):.1f}" y1="{y}" x2="{xcoord(stats["high"]):.1f}" y2="{y}" stroke="{color}" stroke-width="4"/>')
        for value in (stats["low"], stats["high"]):
            x = xcoord(value)
            parts.append(f'<line x1="{x:.1f}" y1="{y-8}" x2="{x:.1f}" y2="{y+8}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<circle cx="{xcoord(stats["mean"]):.1f}" cy="{y}" r="7" fill="{color}"/>')
        parts.append(f'<text x="{right+10}" y="{y+5}" font-family="sans-serif" font-size="12">{stats["mean"]:.2f} ms</text>')
    parts.extend([
        f'<text x="{(left+right)/2:.1f}" y="378" text-anchor="middle" font-family="sans-serif" font-size="13">Milliseconds per traversal</text>',
        "</svg>",
    ])
    path.write_text("\n".join(parts), encoding="utf-8")


def write_order_svg(path, groups):
    width, height = 1050, 420
    left, right, top, bottom = 80, 1015, 45, 350
    all_values = [row["ms"] for key in GROUPS for row in groups[key]]
    low, high = min(all_values), max(all_values)
    padding = max((high - low) * 0.12, high * 0.02, 0.01)
    low -= padding
    high += padding
    max_round = max(row["round"] for key in GROUPS for row in groups[key])

    def xcoord(run):
        if max_round <= 1:
            return (left + right) / 2
        return left + (run - 1) * (right - left) / (max_round - 1)

    def ycoord(value):
        return bottom - (value - low) * (bottom - top) / (high - low)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="525" y="25" text-anchor="middle" font-family="sans-serif" font-size="18">Formal measurements by round</text>',
    ]
    for tick in range(5):
        value = low + (high - low) * tick / 4
        y = ycoord(value)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11">{value:.2f}</text>')
    for index, key in enumerate(GROUPS):
        color = COLORS[index]
        label = f"{key[0]} / {key[1]}"
        points = []
        for row in sorted(groups[key], key=lambda item: item["round"]):
            x = xcoord(row["round"])
            y = ycoord(row["ms"])
            points.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')
        point_text = " ".join(points)
        parts.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.65"/>')
        legend_x = 95 + index * 225
        parts.append(f'<line x1="{legend_x}" y1="390" x2="{legend_x+20}" y2="390" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{legend_x+26}" y="394" font-family="sans-serif" font-size="12">{html.escape(label)}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="370" text-anchor="middle" font-family="sans-serif" font-size="12">Round</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_notes(path, summaries, comparisons, groups, source):
    n = summaries[GROUPS[0]]["n"]
    lines = [
        "# Formal-series analysis",
        "",
        f"Source file: {source}",
        f"Each configuration has {n} successful observations in the same rounds.",
        "Metric: wall time divided by the number of traversals, in milliseconds per traversal.",
        "The 95% confidence interval is mean +/- t(0.975, N-1) * s / sqrt(N); s uses denominator N-1.",
        "For N above 30, the t critical value uses a Cornish-Fisher approximation.",
        "No successful observation is dropped as an outlier. Failed runs and incorrect node counts stop analysis.",
        "cpu_check=bad rows remain in the data and are counted; inspect their logs and discuss them.",
        "The paired write-read comparison matches observations from the same round; positive means write took longer.",
        "N sufficiency is checked against a target 5% relative confidence-interval half-width using the observed SD.",
        "For the same SD, doubling N reduces the half-width by about 1/sqrt(2).",
        "",
        "| API | Mode | N | Mean ms/pass | SD | 95% CI | Relative half-width | Median | IQR | cpu_check bad | Estimated N for 5% |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in GROUPS:
        stats = summaries[key]
        bad = sum(row["cpu_check"] == "bad" for row in groups[key])
        lines.append(
            f'| {key[0]} | {key[1]} | {stats["n"]} | {stats["mean"]:.4f} | '
            f'{stats["sd"]:.4f} | [{stats["low"]:.4f}, {stats["high"]:.4f}] | '
            f'{stats["relative_half_pct"]:.2f}% | {stats["median"]:.4f} | {stats["iqr"]:.4f} | '
            f'{bad} | {stats["estimated_n_5pct"]} |'
        )
    lines.extend([
        "",
        "## Paired write-read comparison",
        "",
        "| API | Paired N | Mean write-read ms/pass | 95% CI for difference | Change relative to read |",
        "|---|---:|---:|---:|---:|",
    ])
    for api in ("read_lseek", "mmap"):
        result = comparisons[api]
        lines.append(
            f'| {api} | {result["n"]} | {result["mean"]:.4f} | '
            f'[{result["low"]:.4f}, {result["high"]:.4f}] | {result["percent"]:.2f}% |'
        )
        if result["low"] > 0:
            lines.append(f"\nFor {api}, the paired interval is above zero: write was slower in this sample.")
        elif result["high"] < 0:
            lines.append(f"\nFor {api}, the paired interval is below zero: write was faster in this sample.")
        else:
            lines.append(f"\nFor {api}, the paired interval includes zero: this sample does not establish the direction clearly.")
    lines.extend([
        "",
        "See means-ci.svg for the four mean estimates and 95% confidence intervals.",
        "See run-order.svg to inspect drift across interleaved rounds.",
        "An interval overlap is a descriptive check, not a substitute for a paired test; interpret system causes using the logs and diagnostics.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyze the four formal result series.")
    parser.add_argument("results_csv", type=Path, help="Path to a run_series.sh results.csv")
    args = parser.parse_args()
    source = args.results_csv.resolve()
    if not source.is_file():
        parser.error("CSV file does not exist: " + str(source))
    groups = load_rows(source)
    out_dir = source.parent / "analysis"
    out_dir.mkdir(exist_ok=True)
    summaries = write_summary(out_dir, groups)
    comparisons = write_comparisons(out_dir, groups)
    write_ci_svg(out_dir / "means-ci.svg", summaries)
    write_order_svg(out_dir / "run-order.svg", groups)
    write_notes(out_dir / "analysis.md", summaries, comparisons, groups, source)
    print("Analysis written to " + str(out_dir))
    print("Files: summary.csv, comparisons.csv, analysis.md, means-ci.svg, run-order.svg")


if __name__ == "__main__":
    main()
