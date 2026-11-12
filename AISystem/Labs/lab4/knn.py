"""手写 kNN：fit 保存训练数据，predict 查找邻居并投票或求平均。"""
import numpy as np


class KNN:
    def __init__(self, k=5, task="classification", metric="euclidean"):
        if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k < 1:
            raise ValueError("k должно быть положительным целым числом.")
        if task not in ("classification", "regression"):
            raise ValueError("task должен быть либо 'classification', либо 'regression'.")
        if metric not in ("euclidean", "manhattan", "chebyshev"):
            raise ValueError("Неподдерживаемая метрика расстояния.")
        self.k, self.task, self.metric = k, task, metric

    def fit(self, x, y):
        x, y = np.asarray(x, dtype=float), np.asarray(y)
        if x.ndim != 2 or x.shape[1] == 0 or y.ndim != 1 or len(x) != len(y):
            raise ValueError("x должно представлять собой двумерную матрицу признаков, а y — одномерный вектор числовых меток той же длины.")
        if self.k > len(x) or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("Количество выборок должно быть не менее k, а данные не должны содержать пропущенных значений или бесконечностей.")
        self.x, self.y = x.copy(), y.copy()
        return self

    def predict(self, x):
        if not hasattr(self, "x"):
            raise ValueError("Пожалуйста, сначала используйте fit")
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[1] != self.x.shape[1] or not np.isfinite(x).all():
            raise ValueError("Размерность признаков для прогнозирования должна совпадать с размерностью данных, использованных при обучении, а все значения должны быть конечными.")
        predictions = []
        for row in x:
            difference = np.abs(self.x - row)
            if self.metric == "euclidean":
                distance = np.sqrt((difference ** 2).sum(axis=1))
            elif self.metric == "manhattan":
                distance = difference.sum(axis=1)
            else:
                distance = difference.max(axis=1)
            # 等距邻居按训练数据顺序选择，保证第 k 个邻居处也可复现。
            nearest = np.argsort(distance, kind="stable")[:self.k]
            values = self.y[nearest]
            if self.task == "regression":
                prediction = values.mean()
            else:
                labels, groups = np.unique(values, return_inverse=True)
                votes = np.bincount(groups)
                totals = np.bincount(groups, weights=distance[nearest])
                # 先比票数，再比本类邻居距离总和，最后选较小标签。
                winner = min(range(len(labels)), key=lambda i: (-votes[i], totals[i], labels[i]))
                prediction = labels[winner]
            predictions.append(prediction)
        return np.asarray(predictions)
