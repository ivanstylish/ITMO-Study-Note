from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import openpyxl


ROOT = Path(r"D:\Study-Note\Modeling\lab1")
SOURCE = ROOT / "!_УИР1_Варианты_с — копия.xlsx"
OUT = ROOT / "tmp" / "analysis" / "variant115"
OUT.mkdir(parents=True, exist_ok=True)

SAMPLE_SIZES = [10, 20, 50, 100, 200, 300]
TP = {0.90: 1.643, 0.95: 1.960, 0.99: 2.576}
# Reproducible seed: variant 115 and laboratory work 01.
RNG_SEED = 11501


def load_variant() -> np.ndarray:
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    ws = wb["101-150"]
    column = None
    for cell in ws[1]:
        if cell.value == 115:
            column = cell.column
            break
    if column is None:
        raise RuntimeError("Variant 115 was not found in row 1")
    values = [ws.cell(row=r, column=column).value for r in range(2, 302)]
    wb.close()
    if len(values) != 300 or any(v is None for v in values):
        raise RuntimeError(f"Expected 300 numeric values, got {len(values)}")
    return np.asarray(values, dtype=float)


def sample_characteristics(x: np.ndarray) -> dict:
    mean = float(np.mean(x))
    variance = float(np.var(x, ddof=1))
    std = float(np.sqrt(variance))
    cv = float(std / mean)
    cis = {str(p): float(t * std / np.sqrt(len(x))) for p, t in TP.items()}
    return {
        "n": int(len(x)),
        "mean": mean,
        "variance": variance,
        "std": std,
        "cv": cv,
        "ci_half": cis,
    }


def table_characteristics(x: np.ndarray) -> dict:
    rows = {str(n): sample_characteristics(x[:n]) for n in SAMPLE_SIZES}
    ref = rows["300"]
    for n in SAMPLE_SIZES:
        row = rows[str(n)]
        row["rel_vs_300_pct"] = {
            key: float((row[key] - ref[key]) / ref[key] * 100.0)
            for key in ("mean", "variance", "std", "cv")
        }
        row["ci_rel_vs_300_pct"] = {
            p: float((row["ci_half"][p] - ref["ci_half"][p]) / ref["ci_half"][p] * 100.0)
            for p in row["ci_half"]
        }
    return rows


def lag_correlation(x: np.ndarray, lag: int) -> float:
    return float(np.corrcoef(x[:-lag], x[lag:])[0, 1])


def acf(x: np.ndarray) -> list[float]:
    return [lag_correlation(x, lag) for lag in range(1, 11)]


def ks_two_sample(x: np.ndarray, y: np.ndarray) -> float:
    grid = np.sort(np.concatenate([x, y]))
    fx = np.searchsorted(np.sort(x), grid, side="right") / len(x)
    fy = np.searchsorted(np.sort(y), grid, side="right") / len(y)
    return float(np.max(np.abs(fx - fy)))


def choose_hyperexp(mean: float, cv: float) -> dict:
    if cv <= 1.0:
        raise RuntimeError(f"CV={cv:.6f}; hyperexponential law is not applicable")
    q_max = 2.0 / (1.0 + cv * cv)
    q = min(0.30, 0.80 * q_max)
    a = np.sqrt((1.0 - q) * (cv * cv - 1.0) / (2.0 * q))
    b = np.sqrt(q * (cv * cv - 1.0) / (2.0 * (1.0 - q)))
    t1 = mean * (1.0 + a)
    t2 = mean * (1.0 - b)
    if t2 <= 0:
        raise RuntimeError("Calculated second exponential mean is non-positive")
    return {"q": float(q), "q_max": float(q_max), "t1": float(t1), "t2": float(t2)}


def generate_hyperexp(params: dict, n: int = 300) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    u1 = rng.random(n)
    u2 = rng.random(n)
    scales = np.where(u1 < params["q"], params["t1"], params["t2"])
    return scales * (-np.log1p(-u2))


def main():
    original = load_variant()
    original_table = table_characteristics(original)
    original_acf = acf(original)
    params = choose_hyperexp(original_table["300"]["mean"], original_table["300"]["cv"])
    generated = generate_hyperexp(params)
    generated_table = table_characteristics(generated)
    generated_acf = acf(generated)

    for n in SAMPLE_SIZES:
        a = original_table[str(n)]
        b = generated_table[str(n)]
        b["rel_vs_original_pct"] = {
            key: float((b[key] - a[key]) / a[key] * 100.0)
            for key in ("mean", "variance", "std", "cv")
        }
        b["ci_rel_vs_original_pct"] = {
            p: float((b["ci_half"][p] - a["ci_half"][p]) / a["ci_half"][p] * 100.0)
            for p in b["ci_half"]
        }

    acf_rel = [
        float((g - o) / abs(o) * 100.0) if abs(o) > 1e-12 else None
        for o, g in zip(original_acf, generated_acf)
    ]
    corr = float(np.corrcoef(original, generated)[0, 1])
    ks_stat = ks_two_sample(original, generated)
    ks_critical = float(1.36 * np.sqrt((len(original) + len(generated)) / (len(original) * len(generated))))
    conf = float(1.96 / np.sqrt(300))

    source_bins = np.linspace(float(original.min()), float(original.max()), 19)
    source_freq, source_edges = np.histogram(original, bins=source_bins)

    result = {
        "source": str(SOURCE),
        "variant": 115,
        "rng_seed": RNG_SEED,
        "sample_sizes": SAMPLE_SIZES,
        "normal_quantiles": {str(k): v for k, v in TP.items()},
        "original": original.tolist(),
        "original_stats": original_table,
        "generated": generated.tolist(),
        "generated_stats": generated_table,
        "hyperexponential": params,
        "original_acf": original_acf,
        "generated_acf": generated_acf,
        "acf_relative_difference_pct": acf_rel,
        "acf_95_bound": conf,
        "pair_correlation": corr,
        "ks_two_sample": {"statistic": ks_stat, "critical_0_05": ks_critical, "passes_0_05": ks_stat < ks_critical},
        "histogram": {"edges": source_edges.tolist(), "frequencies": source_freq.tolist()},
    }
    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "variant": 115,
        "source_n": len(original),
        "source_min": float(original.min()),
        "source_max": float(original.max()),
        "source_300": original_table["300"],
        "params": params,
        "generated_300": generated_table["300"],
        "original_acf": original_acf,
        "generated_acf": generated_acf,
        "acf_bound": conf,
        "pair_correlation": corr,
        "ks": result["ks_two_sample"],
        "histogram": result["histogram"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
