#!/usr/bin/env python3
"""Read one saved formal series and produce figures without running a workload."""

import argparse
import csv
import html
import math
import statistics
from collections import defaultdict
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APIS = ("read_lseek", "mmap")
MODES = ("read", "write")
COLORS = {"read": "#2563A6", "write": "#C24E30"}
RESOURCE_FIELDS = ("user_s", "sys_s", "vol_ctx", "invol_ctx", "minflt", "majflt")
LABELS = json.loads(r'''{"read": "\u0427\u0442\u0435\u043d\u0438\u0435", "write": "\u0417\u0430\u043f\u0438\u0441\u044c", "api_read_lseek": "read/lseek", "api_mmap": "mmap", "mean_title": "\u0421\u0440\u0435\u0434\u043d\u0435\u0435 \u0432\u0440\u0435\u043c\u044f \u043e\u0431\u0445\u043e\u0434\u0430 \u0438 95%-\u0439 \u0434\u043e\u0432\u0435\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b", "time_y": "\u0412\u0440\u0435\u043c\u044f \u043e\u0431\u0445\u043e\u0434\u0430, \u043c\u0441", "time_x": "\u0412\u0440\u0435\u043c\u044f \u043e\u0434\u043d\u043e\u0433\u043e \u043e\u0431\u0445\u043e\u0434\u0430, \u043c\u0441", "density_y": "\u041f\u043b\u043e\u0442\u043d\u043e\u0441\u0442\u044c, 1/\u043c\u0441", "round_x": "\u041d\u043e\u043c\u0435\u0440 \u0438\u0437\u043c\u0435\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u0440\u0430\u0443\u043d\u0434\u0430", "density_title": "\u0420\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u044f \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0447\u0442\u0435\u043d\u0438\u044f \u0438 \u0437\u0430\u043f\u0438\u0441\u0438", "round_title": "\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u043f\u043e \u0438\u0437\u043c\u0435\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u043c \u0440\u0430\u0443\u043d\u0434\u0430\u043c", "provisional_short": "\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0435 \u043c\u043e\u043d\u043e\u0442\u043e\u043d\u043d\u044b\u0435 \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f: \u043e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u043e \u0440\u0430\u0441\u0445\u043e\u0436\u0434\u0435\u043d\u0438\u0435 \u0441 \u0441\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u043c\u0438 \u0447\u0430\u0441\u0430\u043c\u0438, \u0432\u044b\u0432\u043e\u0434\u044b \u0443\u0441\u043b\u043e\u0432\u043d\u044b", "mean_caption": "N = 30 \u0437\u0430\u043f\u0443\u0441\u043a\u043e\u0432 \u0432 \u043a\u0430\u0436\u0434\u043e\u0439 \u0433\u0440\u0443\u043f\u043f\u0435; ITER = 20. \u0412\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u0448\u043a\u0430\u043b\u044b \u0434\u0432\u0443\u0445 \u043f\u0430\u043d\u0435\u043b\u0435\u0439 \u0440\u0430\u0437\u043b\u0438\u0447\u0430\u044e\u0442\u0441\u044f.", "density_caption": "\u0412 \u043a\u0430\u0436\u0434\u043e\u0439 \u043f\u0430\u043d\u0435\u043b\u0438 \u043e\u0434\u0438\u043d\u0430\u043a\u043e\u0432\u044b\u0435 \u0433\u0440\u0430\u043d\u0438\u0446\u044b \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b\u043e\u0432 \u0434\u043b\u044f \u0447\u0442\u0435\u043d\u0438\u044f \u0438 \u0437\u0430\u043f\u0438\u0441\u0438; \u043f\u043b\u043e\u0449\u0430\u0434\u044c \u043a\u0430\u0436\u0434\u043e\u0439 \u0433\u0438\u0441\u0442\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0440\u0430\u0432\u043d\u0430 1."}''' )

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def write_csv(path, rows):
    if not rows:
        raise ValueError('Cannot write an empty result table')
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def beta_fraction(a, b, x):
    qab, qap, qam = (a + b, a + 1.0, a - 1.0)
    tiny = 1e-300
    c = 1.0
    d = 1.0 - qab * x / qap
    d = tiny if abs(d) < tiny else d
    d = 1.0 / d
    value = d
    for step in range(1, 401):
        twice = 2 * step
        aa = step * (b - step) * x / ((qam + twice) * (a + twice))
        d = 1.0 + aa * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + aa / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        value *= d * c
        aa = -(a + step) * (qab + step) * x / ((a + twice) * (qap + twice))
        d = 1.0 + aa * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + aa / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        delta = d * c
        value *= delta
        if abs(delta - 1.0) < 3e-14:
            return value
    raise ArithmeticError('Incomplete beta calculation did not converge')

def regularized_beta(x, a, b):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    factor = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return factor * beta_fraction(a, b, x) / a
    return 1.0 - factor * beta_fraction(b, a, 1.0 - x) / b

def student_cdf(value, df):
    beta = regularized_beta(df / (df + value * value), df / 2.0, 0.5)
    return 1.0 - 0.5 * beta if value >= 0 else 0.5 * beta

def student_quantile(df, probability=0.975):
    if df < 1 or not 0.5 < probability < 1.0:
        raise ValueError('Invalid Student t quantile arguments')
    low, high = (0.0, 1.0)
    while student_cdf(high, df) < probability:
        high *= 2.0
    for _ in range(80):
        middle = (low + high) / 2.0
        if student_cdf(middle, df) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0

def describe(values):
    if len(values) < 2 or any((not math.isfinite(value) for value in values)):
        raise ValueError('At least two finite observations are required')
    n = len(values)
    mean, sd = (statistics.mean(values), statistics.stdev(values))
    se = sd / math.sqrt(n)
    critical = student_quantile(n - 1)
    halfwidth = critical * se
    quartiles = statistics.quantiles(values, n=4, method='inclusive')
    q1, q3 = (quartiles[0], quartiles[2])
    iqr = q3 - q1
    return {'n': n, 'mean': mean, 'sample_sd': sd, 'standard_error': se, 't_critical_95': critical, 'ci95_low': mean - halfwidth, 'ci95_high': mean + halfwidth, 'ci95_halfwidth': halfwidth, 'relative_halfwidth_pct': 100 * halfwidth / abs(mean) if mean else None, 'median': statistics.median(values), 'q1': q1, 'q3': q3, 'iqr': iqr, 'min': min(values), 'max': max(values), 'iqr_flagged_retained': sum((value < q1 - 1.5 * iqr or value > q3 + 1.5 * iqr for value in values))}

def estimated_n(sd, target):
    if target <= 0:
        raise ValueError('The precision target must be positive')
    initial = max(2, math.ceil((1.959963984540054 * sd / target) ** 2))
    n = initial
    while student_quantile(n - 1) * sd / math.sqrt(n) > target:
        n += 1
    return (initial, n)

def summarize_main(rows):
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row['api'], row['mode'])
        if key[0] not in APIS or key[1] not in MODES:
            raise ValueError('Unexpected main-series configuration')
        if row['exit_code'] != '0' or row['nodes'] != '436905':
            raise ValueError('A main-series run failed validation')
        if row['cache'] != 'warm' or row['graph'] != 'graph-seq.bin':
            raise ValueError('Unexpected graph or cache methodology')
        iterations, round_id = (int(row['iterations']), int(row['round']))
        wall = float(row['wall_s'])
        if iterations <= 0 or wall <= 0 or (key, round_id) in seen:
            raise ValueError('Invalid or duplicate main-series observation')
        seen.add((key, round_id))
        row['round_id'] = round_id
        row['ms_per_pass'] = 1000 * wall / iterations
        groups[key].append(row)
    if set(groups) != {(api, mode) for api in APIS for mode in MODES}:
        raise ValueError('All four main-series groups are required')
    if len({len(group) for group in groups.values()}) != 1:
        raise ValueError('Main-series counts differ between groups')
    summary = []
    for api in APIS:
        for mode in MODES:
            group = groups[api, mode]
            stats = describe([row['ms_per_pass'] for row in group])
            approx_n, refined_n = estimated_n(stats['sample_sd'], 0.05 * stats['mean'])
            result = {'api': api, 'mode': mode, 'unit': 'ms_per_pass', **stats, 'n_5pct_normal_approx': approx_n, 'n_5pct_t_refined': refined_n, 'reaches_5pct_target_retrospectively': stats['relative_halfwidth_pct'] <= 5, 'cpu_check_bad_count': sum((row['cpu_check'] == 'bad' for row in group)), 'iterations': int(group[0]['iterations']), 'clock_status': 'pending_separate_timing_audit'}
            summary.append(result)
    paired = []
    resource = []
    for api in APIS:
        read_by_round = {row['round_id']: row for row in groups[api, 'read']}
        write_by_round = {row['round_id']: row for row in groups[api, 'write']}
        if read_by_round.keys() != write_by_round.keys():
            raise ValueError('Read and write rounds do not match')
        differences = [write_by_round[round_id]['ms_per_pass'] - read_by_round[round_id]['ms_per_pass'] for round_id in sorted(read_by_round)]
        read_mean = statistics.mean((row['ms_per_pass'] for row in read_by_round.values()))
        write_mean = statistics.mean((row['ms_per_pass'] for row in write_by_round.values()))
        paired.append({'api': api, 'comparison': 'write_minus_read', 'unit': 'ms_per_pass', **describe(differences), 'ratio_of_means_write_over_read': write_mean / read_mean, 'percent_increase_of_means': 100 * (write_mean / read_mean - 1), 'clock_status': 'pending_separate_timing_audit'})
        for mode in MODES:
            group = groups[api, mode]
            result = {'api': api, 'mode': mode, 'n': len(group), 'iterations': int(group[0]['iterations'])}
            for field in RESOURCE_FIELDS:
                result['mean_' + field + '_per_run'] = statistics.mean((float(row[field]) for row in group))
                result['mean_' + field + '_per_pass'] = statistics.mean((float(row[field]) / int(row['iterations']) for row in group))
            result['cpu_time_exceeds_wall_count'] = sum((float(row['user_s']) + float(row['sys_s']) > float(row['wall_s']) for row in group))
            resource.append(result)
    return (groups, summary, paired, resource)

def svg_start(width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#243746} .grid{stroke:#E1E7ED;stroke-width:1} .axis{stroke:#657687;stroke-width:1.2}</style>']

def text_svg(x, y, value, size=14, anchor='start', fill=None):
    # Keep chart labels readable when two panels are placed on an A4 page.
    if y < 532:
        size = {12: 18, 13: 18, 14: 20, 15: 20, 18: 24, 22: 27}.get(size, size)
    color = f' style="fill:{fill}"' if fill else ''
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}"{color}>{html.escape(str(value))}</text>'

def line_svg(x1, y1, x2, y2, color, width=1.0):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"/>'

def nice_top(value):
    exponent = 10 ** math.floor(math.log10(value)) if value else 1
    return math.ceil(value / exponent / 0.5) * 0.5 * exponent

def panel_axes(parts, x, y, width, height, xmin, xmax, ymax, labels, xlabel=None):
    for step in range(6):
        position = y + height - height * step / 5
        parts.append(line_svg(x, position, x + width, position, '#E1E7ED'))
        parts.append(text_svg(x - 10, position + 5, f'{ymax * step / 5:.3g}', 12, 'end'))
    parts.append(line_svg(x, y, x, y + height, '#657687', 1.2))
    parts.append(line_svg(x, y + height, x + width, y + height, '#657687', 1.2))
    unit_y = y - 4 if xlabel else y - 17
    parts.append(text_svg(x, unit_y, labels['density_y'] if xlabel == 'density' else labels['time_y'], 12))
    if xlabel:
        for step in range(6):
            value = xmin + (xmax - xmin) * step / 5
            if xlabel == 'round':
                value = round(value)
            px = x + width * (value - xmin) / (xmax - xmin)
            parts.append(text_svg(px, y + height + 24, f'{value:.3g}', 12, 'middle'))
        parts.append(text_svg(x + width / 2, y + height + 55, labels['time_x'] if xlabel == 'density' else labels['round_x'], 14, 'middle'))

def save_svg(path, parts):
    path.write_text('\n'.join(parts + ['</svg>']), encoding='utf-8')

def plot_main(summary, labels, output):
    parts = svg_start(1200, 580)
    parts.append(text_svg(600, 34, labels['mean_title'], 22, 'middle'))
    parts.append(text_svg(600, 61, labels['provisional_short'], 13, 'middle'))
    for index, api in enumerate(APIS):
        x, y, width, height = (88 + index * 594, 133, 443, 322)
        stats = [item for item in summary if item['api'] == api]
        top = nice_top(max((item['ci95_high'] for item in stats)) * 1.16)
        panel_axes(parts, x, y, width, height, 0, 1, top, labels)
        parts.append(text_svg(x + width / 2, 100, labels['api_' + api], 18, 'middle'))
        for position, item in enumerate(stats):
            mode = item['mode']
            px = x + width * (0.28 if position == 0 else 0.72)
            py = lambda value: y + height - height * value / top
            low, high, middle = (py(item['ci95_low']), py(item['ci95_high']), py(item['mean']))
            parts.append(line_svg(px, low, px, high, COLORS[mode], 3))
            parts.append(line_svg(px - 11, low, px + 11, low, COLORS[mode], 3))
            parts.append(line_svg(px - 11, high, px + 11, high, COLORS[mode], 3))
            parts.append(f'<circle cx="{px:.3f}" cy="{middle:.3f}" r="6" fill="{COLORS[mode]}"/>')
            parts.append(text_svg(px, high - 17, f"{item['mean']:.3f} +/- {item['ci95_halfwidth']:.3f}", 13, 'middle'))
            parts.append(text_svg(px, y + height + 28, labels[mode], 15, 'middle'))
    parts.append(text_svg(600, 537, labels['mean_caption'], 13, 'middle'))
    save_svg(output / 'means-ci-ru.svg', parts)

def histogram(values, edges):
    counts = [0] * (len(edges) - 1)
    width = edges[1] - edges[0]
    for value in values:
        index = min(len(counts) - 1, max(0, int((value - edges[0]) / width)))
        counts[index] += 1
    return [count / len(values) / width for count in counts]

def plot_histograms(groups, labels, output):
    parts = svg_start(1200, 615)
    parts.append(text_svg(600, 34, labels['density_title'], 22, 'middle'))
    parts.append(text_svg(600, 61, labels['provisional_short'], 13, 'middle'))
    diagnostics = []
    for index, api in enumerate(APIS):
        values = {mode: [row['ms_per_pass'] for row in groups[api, mode]] for mode in MODES}
        combined = values['read'] + values['write']
        span = max(combined) - min(combined)
        low, high = (min(combined) - 0.06 * span, max(combined) + 0.06 * span)
        within_span = max((max(sample) - min(sample) for sample in values.values()))
        bins = min(120, max(20, math.ceil((high - low) / max(within_span / 8, span / 120))))
        edges = [low + (high - low) * step / bins for step in range(bins + 1)]
        density = {mode: histogram(values[mode], edges) for mode in MODES}
        top = nice_top(max((max(items) for items in density.values())) * 1.08)
        x, y, width, height = (88 + index * 594, 154, 443, 321)
        panel_axes(parts, x, y, width, height, low, high, top, labels, 'density')
        parts.append(text_svg(x + width / 2, 98, labels['api_' + api], 18, 'middle'))
        for mode, offset in (('read', 0), ('write', 1)):
            legend_x = x + 93 + 145 * offset
            parts.append(f'<rect x="{legend_x}" y="116" width="19" height="12" fill="{COLORS[mode]}" fill-opacity="0.5"/>')
            parts.append(text_svg(legend_x + 27, 128, labels[mode], 13))
            for bin_id, level in enumerate(density[mode]):
                px = x + width * bin_id / bins
                bar_height = height * level / top
                parts.append(f'<rect x="{px:.3f}" y="{y + height - bar_height:.3f}" width="{width / bins:.3f}" height="{bar_height:.3f}" fill="{COLORS[mode]}" fill-opacity="0.43" stroke="{COLORS[mode]}" stroke-width="0.55"/>')
            area = sum((level * (edges[1] - edges[0]) for level in density[mode]))
            diagnostics.append({'api': api, 'mode': mode, 'bins': bins, 'bin_width_ms': edges[1] - edges[0], 'density_area': area})
    parts.append(text_svg(600, 576, labels['density_caption'], 13, 'middle'))
    save_svg(output / 'read-write-density-ru.svg', parts)
    return diagnostics

def plot_rounds(groups, labels, output):
    parts = svg_start(1200, 580)
    parts.append(text_svg(600, 34, labels['round_title'], 22, 'middle'))
    parts.append(text_svg(600, 61, labels['provisional_short'], 13, 'middle'))
    for index, api in enumerate(APIS):
        x, y, width, height = (88 + index * 594, 151, 443, 311)
        top = nice_top(max((row['ms_per_pass'] for mode in MODES for row in groups[api, mode])) * 1.05)
        first = min((row['round_id'] for row in groups[api, 'read']))
        last = max((row['round_id'] for row in groups[api, 'read']))
        panel_axes(parts, x, y, width, height, first, last, top, labels, 'round')
        parts.append(text_svg(x + width / 2, 98, labels['api_' + api], 18, 'middle'))
        for mode, offset in (('read', 0), ('write', 1)):
            legend_x = x + 93 + 145 * offset
            parts.append(line_svg(legend_x, 122, legend_x + 21, 122, COLORS[mode], 2))
            parts.append(text_svg(legend_x + 27, 128, labels[mode], 13))
            coordinates = []
            for row in sorted(groups[api, mode], key=lambda row: row['round_id']):
                px = x + width * (row['round_id'] - first) / (last - first)
                py = y + height - height * row['ms_per_pass'] / top
                coordinates.append(f'{px:.3f},{py:.3f}')
                parts.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="2.5" fill="{COLORS[mode]}"/>')
            points = ' '.join(coordinates)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{COLORS[mode]}" stroke-width="1.6"/>')
    save_svg(output / 'run-order-ru.svg', parts)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--series-status", choices=("existing_draft", "new_confirmatory"), default="existing_draft")
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    source = source_dir / "results.csv"
    output_root = args.output_root.resolve()
    out = output_root / "assets"
    out.mkdir(parents=True, exist_ok=True)
    (output_root / "analysis").mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    rows = read_csv(source)
    groups, summary, paired, resources = summarize_main(rows)
    sample_n = len(groups[APIS[0], MODES[0]])
    iterations = int(rows[0]["iterations"])
    if any(int(row["iterations"]) != iterations for row in rows):
        raise ValueError("All four groups must use the same iterations")
    for item in summary:
        group = sorted(groups[item["api"], item["mode"]], key=lambda row: row["round_id"])
        midpoint = len(group) // 2
        first_mean = statistics.mean(row["ms_per_pass"] for row in group[:midpoint])
        second_mean = statistics.mean(row["ms_per_pass"] for row in group[midpoint:])
        item["first_half_mean_ms"] = first_mean
        item["second_half_mean_ms"] = second_mean
        item["second_minus_first_half_ms"] = second_mean - first_mean
        item["second_minus_first_half_pct"] = 100 * (second_mean / first_mean - 1)
        item["iqr_flagged_rounds_retained"] = [row["round_id"] for row in group
            if row["ms_per_pass"] < item["q1"] - 1.5 * item["iqr"]
            or row["ms_per_pass"] > item["q3"] + 1.5 * item["iqr"]]
        for derived_n in ("n_5pct_normal_approx", "n_5pct_t_refined", "reaches_5pct_target_retrospectively"):
            item.pop(derived_n, None)
    labels = dict(LABELS)
    labels["provisional_short"] = f"N = {sample_n} \u0437\u0430\u043f\u0443\u0441\u043a\u043e\u0432 \u0432 \u043a\u0430\u0436\u0434\u043e\u0439 \u0433\u0440\u0443\u043f\u043f\u0435; ITER = {iterations}; \u043f\u0440\u043e\u0433\u0440\u0435\u0442\u044b\u0439 \u0444\u0430\u0439\u043b\u043e\u0432\u044b\u0439 \u043a\u044d\u0448"
    labels["mean_caption"] = f"95%-\u0439 \u0414\u0418 \u0441\u0440\u0435\u0434\u043d\u0435\u0433\u043e: \u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u0421\u0442\u044c\u044e\u0434\u0435\u043d\u0442\u0430, {sample_n - 1} \u0441\u0442\u0435\u043f\u0435\u043d\u0435\u0439 \u0441\u0432\u043e\u0431\u043e\u0434\u044b. \u0428\u043a\u0430\u043b\u044b \u043f\u0430\u043d\u0435\u043b\u0435\u0439 \u0440\u0430\u0437\u043b\u0438\u0447\u0430\u044e\u0442\u0441\u044f."
    labels["density_caption"] = "\u041e\u0431\u0449\u0438\u0435 \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b\u044b \u0434\u043b\u044f \u0447\u0442\u0435\u043d\u0438\u044f \u0438 \u0437\u0430\u043f\u0438\u0441\u0438 \u0432\u043d\u0443\u0442\u0440\u0438 \u043a\u0430\u0436\u0434\u043e\u0439 \u043f\u0430\u043d\u0435\u043b\u0438; \u043f\u043b\u043e\u0449\u0430\u0434\u044c \u043a\u0430\u0436\u0434\u043e\u0439 \u0433\u0438\u0441\u0442\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0440\u0430\u0432\u043d\u0430 1."
    plot_main(summary, labels, out)
    histogram_checks = plot_histograms(groups, labels, out)
    plot_rounds(groups, labels, out)
    if any(abs(check["density_area"] - 1.0) > 1e-10 for check in histogram_checks):
        raise AssertionError("Histogram density areas differ from one")

    clock_rows = []
    pattern = re.compile(r"CLOCK realtime_s=([0-9.e+-]+) monotonic_s=([0-9.e+-]+)")
    for row in rows:
        log = source_dir / "logs" / ("r" + row["round"] + "_" + row["api"] + "_" + row["mode"] + ".log")
        content = log.read_text(encoding="utf-8", errors="replace")
        match = pattern.search(content)
        if match:
            realtime, monotonic = float(match[1]), float(match[2])
            raw_match = re.search(r"monotonic_raw_s=([0-9.e+-]+)", content)
            raw = float(raw_match[1]) if raw_match else None
            clock_rows.append({"round": int(row["round"]), "api": row["api"], "mode": row["mode"],
                               "monotonic_s": monotonic, "realtime_s": realtime,
                               "monotonic_raw_s": raw,
                               "monotonic_minus_raw_s": monotonic - raw if raw is not None else None,
                               "difference_s": monotonic - realtime,
                               "abs_difference_s": abs(monotonic - realtime),
                               "log_matches_csv": abs(monotonic - float(row["wall_s"])) < 1e-9,
                               "successful_traversals": content.count("OK (436905 nodes processed)")})
    clock = {"logs_with_two_clocks": len(clock_rows),
             "difference_over_1ms": sum(row["abs_difference_s"] > 0.001 for row in clock_rows),
             "difference_over_100ms": sum(row["abs_difference_s"] > 0.1 for row in clock_rows),
             "max_abs_difference_s": max((row["abs_difference_s"] for row in clock_rows), default=None),
             "all_csv_values_match_monotonic_logs": all(row["log_matches_csv"] for row in clock_rows),
             "expected_successful_traversals": iterations,
             "all_logs_have_expected_successful_traversals": all(row["successful_traversals"] == iterations for row in clock_rows),
             "sum_monotonic_s": sum(row["monotonic_s"] for row in clock_rows),
             "sum_realtime_s": sum(row["realtime_s"] for row in clock_rows),
             "worst_rows": sorted(clock_rows, key=lambda row: row["abs_difference_s"], reverse=True)[:5]}
    raw_rows = [row for row in clock_rows if row["monotonic_raw_s"] is not None]
    clock["logs_with_raw_clock"] = len(raw_rows)
    clock["max_abs_monotonic_minus_raw_s"] = max(
        (abs(row["monotonic_minus_raw_s"]) for row in raw_rows), default=None)
    clock["monotonic_raw_difference_over_1ms"] = sum(
        abs(row["monotonic_minus_raw_s"]) > 0.001 for row in raw_rows)
    clock["all_measurements_have_two_clock_logs"] = len(clock_rows) == len(rows)
    clock_groups = []
    raw_pairs = []
    for api in APIS:
        for mode in MODES:
            group = [row for row in raw_rows if row["api"] == api and row["mode"] == mode]
            if not group:
                continue
            raw_stats = describe([row["monotonic_raw_s"] * 1000 / iterations for row in group])
            rel = [100 * (row["monotonic_s"] / row["monotonic_raw_s"] - 1) for row in group]
            mono_mean = statistics.mean(row["monotonic_s"] for row in group)
            raw_mean = statistics.mean(row["monotonic_raw_s"] for row in group)
            clock_groups.append({"api": api, "mode": mode, "n": len(group),
                                 "monotonic_mean_ms_per_pass": mono_mean * 1000 / iterations,
                                 "raw_summary_ms_per_pass": raw_stats,
                                 "relative_difference_pct_mean": statistics.mean(rel),
                                 "relative_difference_pct_min": min(rel),
                                 "relative_difference_pct_max": max(rel),
                                 "ratio_of_mean_monotonic_to_raw": mono_mean / raw_mean})
        read_raw = {row["round"]: row for row in raw_rows if row["api"] == api and row["mode"] == "read"}
        write_raw = {row["round"]: row for row in raw_rows if row["api"] == api and row["mode"] == "write"}
        if read_raw and read_raw.keys() == write_raw.keys():
            differences = [(write_raw[round_id]["monotonic_raw_s"] - read_raw[round_id]["monotonic_raw_s"])
                           * 1000 / iterations for round_id in sorted(read_raw)]
            read_mean = statistics.mean(row["monotonic_raw_s"] for row in read_raw.values())
            write_mean = statistics.mean(row["monotonic_raw_s"] for row in write_raw.values())
            raw_pairs.append({"api": api, "unit": "ms_per_pass", **describe(differences),
                              "ratio_of_mean_raw_write_to_read": write_mean / read_mean})
    clock["monotonic_vs_raw_groups"] = clock_groups
    clock["raw_paired_write_minus_read"] = raw_pairs
    clock_status = ("real_time_disagreement_observed" if clock["difference_over_1ms"]
                    else "clock_agreement_observed")
    clock_status += ";monotonic_used;absolute_accuracy_not_independently_calibrated"
    for result in summary:
        result["clock_status"] = clock_status
        result["precision_assessment_status"] = "achieved_precision_only;not_evidence_of_prospective_sample_size_selection"
    for result in paired:
        result["clock_status"] = clock_status
    after = hashlib.sha256(source.read_bytes()).hexdigest()
    if after != before:
        raise AssertionError("Input CSV was modified")
    result = {
        "source": str(source), "source_sha256": before, "input_unchanged": before == after,
        "observations": len(rows), "selected_series_only": True,
        "series_status": args.series_status,
        "unit": "milliseconds_per_traversal",
        "method": "x_i = 1000 * wall_s / iterations; 95 percent Student t confidence intervals",
        "notes": ["No observation was deleted or replaced.",
                  "Series status explicitly identifies an existing draft or a new confirmatory dataset.",
                  "No independent pilot dataset is manufactured.",
                  "Timestamp values identify files only and do not determine measured durations."],
        "main_summary": summary, "paired_write_minus_read": paired,
        "resource_summary": resources, "histogram_checks": histogram_checks,
        "clock_audit": clock,
    }
    (output_root / "analysis" / "selected-series.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(output_root / "analysis" / "selected-main-summary.csv", summary)
    write_csv(output_root / "analysis" / "selected-resources.csv", resources)
    write_csv(output_root / "analysis" / "selected-paired-read-write.csv", paired)
    if clock_rows:
        write_csv(output_root / "analysis" / "selected-clock-runs.csv", clock_rows)
    (out / "figures.typ").write_text(
        '#set page(width: 1200pt, height: 615pt, margin: 0pt)\n'
        '#image("read-write-density-ru.svg", width: 100%, height: 100%)\n', encoding="utf-8")
    for stem in ("means-ci-ru", "run-order-ru"):
        (out / (stem + ".typ")).write_text(
            '#set page(width: 1200pt, height: 580pt, margin: 0pt)\n'
            f'#image("{stem}.svg", width: 100%, height: 100%)\n', encoding="utf-8")
    print(json.dumps({"observations": len(rows), "histogram_checks": histogram_checks,
                      "clock_rows": len(clock_rows), "source_unchanged": before == after}))


if __name__ == "__main__":
    main()
