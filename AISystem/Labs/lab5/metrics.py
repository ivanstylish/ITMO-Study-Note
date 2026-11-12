"""Собственные бинарные метрики, ROC/PR и интегрирование трапециями."""
import numpy as np
import pandas as pd


def binary_metrics(y, prediction):
    y, prediction = np.asarray(y), np.asarray(prediction)
    if (y.ndim != 1 or y.shape != prediction.shape or not y.size
            or not np.isin(y, [0, 1]).all()
            or not np.isin(prediction, [0, 1]).all()):
        raise ValueError("Need equally sized nonempty binary vectors.")
    tp = int(np.sum((y == 1) & (prediction == 1)))
    fp = int(np.sum((y == 0) & (prediction == 1)))
    fn = int(np.sum((y == 1) & (prediction == 0)))
    tn = int(np.sum((y == 0) & (prediction == 0)))
    return {"accuracy": (tp + tn) / len(y),
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
            "TP": tp, "FP": fp, "FN": fn, "TN": tn}


def trapezoid_auc(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if (x.ndim != 1 or x.shape != y.shape or len(x) < 2
            or not np.isfinite(x).all() or not np.isfinite(y).all()):
        raise ValueError("Need matching finite curve coordinates with at least two points.")
    # Стабильность сохраняет порядок порогов при одинаковых x.
    order = np.argsort(x, kind="stable")
    x, y = x[order], y[order]
    return float(np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2))


def classification_curves(y, scores, leaf_probabilities=()):
    y, scores = np.asarray(y), np.asarray(scores, dtype=float)
    if (y.ndim != 1 or y.shape != scores.shape or set(y) != {0, 1}
            or not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1))):
        raise ValueError("Curves need both classes and finite scores in [0, 1].")
    # Кроме листьев учитываем оценки отката при неизвестной категории.
    thresholds = sorted(set(scores) | set(leaf_probabilities) | {0.0, 1.0}, reverse=True)
    rows = []
    # +inf даёт опорную точку без положительных прогнозов даже при score=1.
    for threshold in [np.inf] + thresholds:
        m = binary_metrics(y, scores >= threshold)
        rows.append({"threshold": threshold, **m,
                     "FPR": m["FP"] / (m["FP"] + m["TN"]),
                     "TPR": m["recall"],
                     "curve_precision": m["precision"] if m["TP"] + m["FP"] else 1.0})
    points = pd.DataFrame(rows)
    areas = {"ROC_AUC": trapezoid_auc(points.FPR, points.TPR),
             "PR_AUC": trapezoid_auc(points.recall, points.curve_precision)}
    return points, areas
