"""手写分类和回归指标，不使用 sklearn.metrics。"""
import numpy as np


def paired_values(actual, predicted):
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    if actual.ndim != 1 or actual.shape != predicted.shape or not actual.size:
        raise ValueError("Фактические и прогнозируемые значения должны представлять собой непустые одномерные массивы одинаковой длины.")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Входные данные индикатора не могут содержать пропущенные значения или бесконечности.")
    return actual, predicted


def confusion_matrix(actual, predicted, labels):
    actual, predicted = paired_values(actual, predicted)
    labels = np.asarray(labels)
    if labels.ndim != 1 or len(np.unique(labels)) != len(labels):
        raise ValueError("Метки категорий должны быть одномерными и уникальными.")
    if not np.isin(actual, labels).all() or not np.isin(predicted, labels).all():
        raise ValueError("Список категорий должен включать все фактические метки и предсказанные метки.")
    return np.array([[np.sum((actual == a) & (predicted == p))
                      for p in labels] for a in labels])


def classification_metrics(actual, predicted):
    actual, predicted = paired_values(actual, predicted)
    matrix = confusion_matrix(actual, predicted, np.union1d(actual, predicted))
    tp = np.diag(matrix)
    # 某类没有预测样本或真实样本时，相应指标取 0。
    precision = tp / np.maximum(matrix.sum(axis=0), 1)
    recall = tp / np.maximum(matrix.sum(axis=1), 1)
    f1 = np.divide(2 * precision * recall, precision + recall,
                   out=np.zeros_like(precision), where=(precision + recall) != 0)
    return {"accuracy": float(tp.sum() / matrix.sum()),
            "precision_macro": float(precision.mean()),
            "recall_macro": float(recall.mean()), "F1_macro": float(f1.mean())}


def regression_metrics(actual, predicted):
    actual, predicted = paired_values(actual, predicted)
    error = actual.astype(float) - predicted
    mse = float(np.mean(error ** 2))
    variance = float(np.mean((actual - actual.mean()) ** 2))
    return {"MAE": float(np.mean(np.abs(error))), "MSE": mse,
            "R2": 1 - mse / variance if variance else float("nan")}
