from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
TARGET, CATEGORY = "Performance Index", "Extracurricular Activities"
NUMERIC = ["Hours Studied", "Previous Scores", "Sleep Hours", "Sample Question Papers Practiced"]
INTERACTION = "Study Interaction"
MODELS = {"Модель 1": [NUMERIC[0], NUMERIC[2], NUMERIC[3]],
          "Модель 2": [NUMERIC[1], CATEGORY], "Модель 3": NUMERIC + [CATEGORY, INTERACTION]}
VARIANTS = ["Без регуляризации", "L1", "L2", "ElasticNet"]
SEED, RATE, STEPS, NEAR_ZERO = 42, 0.05, 10000, 0.1
LAMBDAS, RATIOS = [0.001, 0.01, 0.1, 1.0, 10.0], [0.2, 0.5, 0.8]
GRID = {VARIANTS[0]: [(0, 0)], "L1": [(a, 1) for a in LAMBDAS],
        "L2": [(a, 0) for a in LAMBDAS], "ElasticNet": [(a, r) for a in LAMBDAS for r in RATIOS]}
CURVES = ["train_MSE", "validation_MSE", "train_R2", "validation_R2"]


def preprocess(frames):
    """Заполнение обучаем только на train. Категории и взаимодействие как в lab1."""
    medians, mode = frames[0][NUMERIC].median(), frames[0][CATEGORY].mode().iloc[0]
    result = []
    for frame in frames:
        frame = frame.copy()
        frame[NUMERIC] = frame[NUMERIC].fillna(medians)
        category = frame[CATEGORY].fillna(mode)
        if not category.isin(["No", "Yes"]).all():
            raise ValueError("Ожидаются категории No/Yes.")
        frame[CATEGORY] = category.map({"No": 0, "Yes": 1})
        frame[INTERACTION] = frame[NUMERIC[0]] * frame[NUMERIC[1]] / 100
        result.append(frame)
    return result, {"medians": medians.to_dict(), "category_mode": mode}


def load_data(path):
    raw = pd.read_csv(path)
    data = raw.drop_duplicates().dropna(subset=[TARGET]).copy()
    data.insert(0, "row_id", data.index)
    order = np.random.default_rng(SEED).permutation(len(data))
    a, b = int(0.6 * len(data)), int(0.8 * len(data))
    frames = [data.iloc[index] for index in (order[:a], order[a:b], order[b:])]
    frames, parameters = preprocess(frames)
    info = {"raw_rows": len(raw), "duplicates": int(raw.duplicated().sum()),
            "clean_rows": len(data), "missing_values": raw.isna().sum().to_dict(),
            "missing_target_removed": int(raw.drop_duplicates()[TARGET].isna().sum()),
            "split_sizes": dict(zip(["train", "validation", "test"], map(len, frames))),
            "preprocessing": parameters}
    return frames, info


def design_matrix(frame, features, mean, scale):
    z = (frame[features].to_numpy(dtype=float) - mean) / scale
    return np.column_stack([np.ones(len(z)), z])


def evaluate(y, prediction):
    error = y - prediction
    mse, variance = float(np.mean(error ** 2)), float(np.var(y))
    return {"MSE": mse, "R2": 1 - mse / variance if variance else float("nan"),
            "RMSE": float(np.sqrt(mse)), "MAE": float(np.mean(np.abs(error)))}


def fit(x, y, strength=0, ratio=0, validation=None, rate=RATE, steps=STEPS):
    """Одна модель. J = MSE + λ[ρ||w||₁ + (1−ρ)||w||₂²/2]."""
    if strength < 0 or not 0 <= ratio <= 1 or rate <= 0 or steps < 1:
        raise ValueError("Нужны λ ≥ 0, 0 ≤ ρ ≤ 1 и положительные шаг и число итераций.")
    w, history = np.zeros(x.shape[1]), []
    # Это тот же градиент 2/n * X.T @ (X @ w - y), но без повторных больших произведений.
    gram, cross = x.T @ x / len(y), x.T @ y / len(y)
    for step in range(steps + 1):
        if validation is not None:
            xv, yv = validation
            train, val = evaluate(y, x @ w), evaluate(yv, xv @ w)
            history.append([train["MSE"], val["MSE"], train["R2"], val["R2"]])
        if step == steps:
            break
        gradient = 2 * (gram @ w - cross)
        gradient[1:] += strength * (1 - ratio) * w[1:]
        w -= rate * gradient
        # 截距位于 w[0]。只对 w[1:] 做 L2 惩罚和 L1 软阈值更新。
        w[1:] = np.sign(w[1:]) * np.maximum(np.abs(w[1:]) - rate * strength * ratio, 0)
    if not np.isfinite(w).all():
        raise ValueError("Расходимость. Уменьшите rate.")
    return w, np.array(history)


def weight_statistics(w):
    slopes = w[1:]
    return {"L1_norm": float(np.abs(slopes).sum()), "L2_norm": float(np.linalg.norm(slopes)),
            "zero_coefficients": int((slopes == 0).sum()),
            "near_zero_coefficients": int((np.abs(slopes) <= NEAR_ZERO).sum())}


def main(no_plots=False):
    path, out = ROOT.parent / "lab1" / "Student_Performance.csv", ROOT / "output"
    out.mkdir(exist_ok=True)
    frames, info = load_data(path)
    y = [frame[TARGET].to_numpy(dtype=float) for frame in frames]
    trials, metrics, coefficients, grid_coefficients = [], [], [], []
    results, normalization, archive = {}, {}, {"variants": np.array(VARIANTS)}
    predictions = pd.DataFrame({"row_id": frames[2].row_id.to_numpy(), "actual": y[2]})
    print("Разбиение:", info["split_sizes"], flush=True)
    for number, (name, features) in enumerate(MODELS.items(), 1):
        mean = frames[0][features].mean().to_numpy()
        scale = frames[0][features].std(ddof=0).to_numpy(copy=True)
        scale[scale == 0] = 1
        x = [design_matrix(frame, features, mean, scale) for frame in frames]
        weights, histories = [], []
        for variant, parameters in GRID.items():
            candidates = []
            for strength, ratio in parameters:
                w, _ = fit(x[0], y[0], strength, ratio)
                row = {"model": name, "variant": variant, "lambda": strength, "l1_ratio": ratio,
                       "learning_rate": RATE, "iterations": STEPS, **weight_statistics(w)}
                for part, matrix, target in zip(["train", "validation"], x[:2], y[:2]):
                    row.update({part + "_" + key: value for key, value in evaluate(target, matrix @ w).items()})
                candidates.append(row)
                grid_coefficients.extend({"model": name, "variant": variant, "lambda": strength,
                                          "l1_ratio": ratio, "feature": f, "weight": float(v)}
                                         for f, v in zip(["Intercept"] + features, w))
            trials.extend(candidates)
            # 验证集只负责选参。这里完全没有测试集指标。
            best = min(candidates, key=lambda row: (row["validation_MSE"], row["lambda"], row["l1_ratio"]))
            w, history = fit(x[0], y[0], best["lambda"], best["l1_ratio"], (x[1], y[1]))
            row = best.copy()
            for part, matrix, target in zip(["train", "validation", "test"], x, y):
                row.update({part + "_" + key: value for key, value in evaluate(target, matrix @ w).items()})
            row["generalization_gap"] = row["validation_MSE"] - row["train_MSE"]
            metrics.append(row)
            original = np.r_[w[0] - np.sum(w[1:] * mean / scale), w[1:] / scale]
            coefficients.extend({"model": name, "variant": variant, "feature": f,
                                 "standardized_weight": float(v), "original_weight": float(o),
                                 "is_zero": bool(v == 0), "is_near_zero": bool(abs(v) <= NEAR_ZERO)}
                                for f, v, o in zip(["Intercept"] + features, w, original))
            predictions[name + "_" + variant] = x[2] @ w
            weights.append(w)
            histories.append(history)
        histories = np.stack(histories, axis=1)
        history_table = {variant + "_" + key: histories[:, i, j]
                         for i, variant in enumerate(VARIANTS) for j, key in enumerate(CURVES)}
        pd.DataFrame({"iteration": np.arange(STEPS + 1), **history_table}).to_csv(out / f"model_{number}_history.csv", index=False)
        results[name] = {"features": features, "weights": np.column_stack(weights),
                         "history": {key: histories[:, :, j] for j, key in enumerate(CURVES)}}
        normalization[name] = {"features": features, "mean": mean.tolist(), "scale": scale.tolist()}
        archive.update({f"model_{number}_weights": np.column_stack(weights), f"model_{number}_mean": mean,
                        f"model_{number}_scale": scale, f"model_{number}_features": np.array(features)})
        print(name + ": четыре варианта обучены", flush=True)
    tables = {"metrics": metrics, "hyperparameter_results": trials, "coefficients": coefficients,
              "grid_coefficients": grid_coefficients, "test_predictions": predictions}
    for filename, rows in tables.items():
        pd.DataFrame(rows).to_csv(out / (filename + ".csv"), index=False, encoding="utf-8-sig")
    pd.concat([pd.DataFrame({"row_id": frame.row_id, "split": part})
               for frame, part in zip(frames, ["train", "validation", "test"])]).sort_values("row_id").to_csv(out / "split.csv", index=False)
    summary = {**info, "dataset": str(path.resolve()), "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "seed": SEED, "learning_rate": RATE, "iterations": STEPS, "initial_weights": "zeros",
               "lambdas": LAMBDAS, "l1_ratios": RATIOS, "near_zero_threshold": NEAR_ZERO,
               "normalization": normalization, "selection_metric": "validation_MSE", "hyperparameter_runs": len(trials),
               "selected_parameters": [{k: row[k] for k in ["model", "variant", "lambda", "l1_ratio"]} for row in metrics],
               "final_metrics": metrics, "refit_train_validation": False,
               "objective": "MSE + lambda * (rho * L1 + (1-rho) * L2_squared / 2)"}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    np.savez(out / "models.npz", **archive)
    if not no_plots:
        from graphics import make_figures
        make_figures(out, results, pd.DataFrame(trials), STEPS)
    print(pd.DataFrame(metrics)[["model", "variant", "lambda", "l1_ratio", "test_MSE", "test_R2"]].to_string(index=False))
    return summary


if __name__ == "__main__":
    main(no_plots="--no-plots" in sys.argv)
