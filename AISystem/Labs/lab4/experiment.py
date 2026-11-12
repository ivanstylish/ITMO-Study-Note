"""实验四：数据准备、验证集选参、一次最终测试，以及结果保存。"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.datasets import load_wine, load_diabetes
from sklearn.model_selection import train_test_split

from knn import KNN
from metrics import classification_metrics, regression_metrics, confusion_matrix

ROOT = Path(__file__).resolve().parent
SEED = 42
K_VALUES = (3, 5, 10, 15)
DISTANCES = ("euclidean", "manhattan", "chebyshev")


def prepare_data(x, y, stratified=False):
    indices = np.arange(len(y))
    train, other = train_test_split(indices, test_size=0.4, random_state=SEED,
                                    stratify=y if stratified else None)
    validation, test = train_test_split(other, test_size=0.5, random_state=SEED,
                                        stratify=y[other] if stratified else None)
    # 划分之后只用训练集计算均值和标准差；常数列除以 1。
    mean, scale = x[train].mean(axis=0), x[train].std(axis=0, ddof=0)
    scale[scale == 0] = 1
    parts = (train, validation, test)
    return [(x[i] - mean) / scale for i in parts], [y[i] for i in parts], parts, mean, scale


def run_experiment():
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    datasets = {"wine": load_wine(), "diabetes": load_diabetes(scaled=False)}
    summary = {"seed": SEED, "k_values": K_VALUES, "distances": DISTANCES,
               "refit_train_validation": False, "datasets": {}}
    plot_data = {}
    for name, dataset in datasets.items():
        task = "classification" if name == "wine" else "regression"
        evaluate = classification_metrics if name == "wine" else regression_metrics
        x, y = dataset.data, dataset.target
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("Экспериментальные данные должны быть полными и конечными; в случае изменения данных необходимо прежде всего обработать все отсутствующие значения.")
        frame = pd.DataFrame(x, columns=dataset.feature_names)
        frame["target"] = y
        frame.to_csv(out / f"{name}_data.csv", index=False)
        frame.describe().T.to_csv(out / f"{name}_statistics.csv")
        xs, ys, indices, mean, scale = prepare_data(x, y, name == "wine")
        pd.concat([pd.DataFrame({"row_id": i, "split": part})
                   for part, i in zip(("train", "validation", "test"), indices)]
                  ).sort_values("row_id").to_csv(out / f"{name}_split.csv", index=False)
        rows = []
        for metric in DISTANCES:
            for k in K_VALUES:
                model = KNN(k, task, metric).fit(xs[0], ys[0])
                rows.append({"k": k, "distance": metric,
                             **evaluate(ys[1], model.predict(xs[1]))})
        grid = pd.DataFrame(rows)
        grid.to_csv(out / f"{name}_validation.csv", index=False)
        # 主指标相同，先选较小的 k，再按 DISTANCES 的顺序选距离。
        best = min(rows, key=lambda r: (-r["F1_macro"] if name == "wine" else r["MSE"],
                                       r["k"], DISTANCES.index(r["distance"])))
        model = KNN(best["k"], task, best["distance"]).fit(xs[0], ys[0])
        predicted = model.predict(xs[2])
        scores = evaluate(ys[2], predicted)
        pd.DataFrame({"row_id": indices[2], "actual": ys[2], "predicted": predicted}
                     ).to_csv(out / f"{name}_test_predictions.csv", index=False)
        info = {"task": task, "rows": len(y), "features": x.shape[1],
                "missing_values": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
                "split_sizes": dict(zip(("train", "validation", "test"), map(len, indices))),
                "feature_names": list(dataset.feature_names),
                "mean": mean.tolist(), "scale": scale.tolist(),
                "selection_metric": "F1_macro" if name == "wine" else "MSE",
                "best_validation": best, "test_metrics": scores}
        if name == "wine":
            labels = np.unique(y)
            matrix = confusion_matrix(ys[2], predicted, labels)
            pd.DataFrame(matrix, index=labels, columns=labels).to_csv(out / "wine_confusion_matrix.csv")
            info["class_counts"] = {}
            for part, target in zip(("train", "validation", "test"), ys):
                classes, counts = np.unique(target, return_counts=True)
                info["class_counts"][part] = {int(c): int(n) for c, n in zip(classes, counts)}
            info["confusion_matrix"] = matrix.tolist()
        summary["datasets"][name] = info
        plot_data[name] = {"frame": frame, "grid": grid, "actual": ys[2], "predicted": predicted}
        print(f"{name}: {info['split_sizes']}; k={best['k']}, distance={best['distance']}")
        print("  test:", scores)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2,
                                                 allow_nan=False), encoding="utf-8")
    from graphics import make_figures
    make_figures(out, plot_data, summary)
    return summary


if __name__ == "__main__":
    run_experiment()
