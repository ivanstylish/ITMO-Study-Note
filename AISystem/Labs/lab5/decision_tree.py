"""Многоветвевое ID3: категории, энтропия и доля класса 1 в узле."""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


def entropy(y):
    p = np.bincount(np.asarray(y, dtype=int), minlength=2) / len(y)
    p = p[p > 0]  # Нулевые доли не входят в логарифм.
    return float(-np.sum(p * np.log2(p)))


@dataclass
class Node:
    probability: float
    samples: int
    feature: str | None = None
    gain: float = 0.0
    children: dict = field(default_factory=dict)


class DecisionTree:
    def fit(self, X, y):
        y = np.asarray(y)
        if (not isinstance(X, pd.DataFrame) or X.empty
                or len(X) != len(y) or y.ndim != 1
                or not np.isin(y, [0, 1]).all()
                or X.isna().any().any() or not X.columns.is_unique):
            raise ValueError("Need nonempty categorical X and matching binary y, no missing values.")
        self.features = list(X.columns)
        self.importances = dict.fromkeys(self.features, 0.0)
        self.root = self._build(X.reset_index(drop=True), y)
        return self

    def _build(self, X, y):
        global best_groups
        node = Node(float(y.mean()), len(y))
        if node.probability in (0, 1) or X.shape[1] == 0:
            return node
        parent_entropy = entropy(y)
        for feature in X.columns:
            groups = [(value, X[feature].to_numpy() == value)
                      for value in sorted(X[feature].unique())]
            gain = parent_entropy - sum(mask.mean() * entropy(y[mask])
                                        for _, mask in groups)
            # 1e-12 устраняет погрешность нулевого выигрыша; равенство сохраняет порядок.
            if gain > node.gain + 1e-12:
                node.feature, node.gain = feature, gain
                best_groups = groups
        if node.feature is not None:
            # По заданию суммируем IG без взвешивания по размеру узла.
            self.importances[node.feature] += node.gain
            for value, mask in best_groups:
                node.children[value] = self._build(
                    X.loc[mask].drop(columns=node.feature), y[mask])
        return node

    def predict_proba(self, X):
        if not hasattr(self, "root"):
            raise ValueError("Call fit before prediction.")
        if not set(self.features).issubset(X.columns) or X[self.features].isna().any().any():
            raise ValueError("Prediction needs the fitted features and explicit missing categories.")
        probabilities = []
        for _, row in X.iterrows():
            node = self.root
            while node.feature is not None:
                child = node.children.get(row[node.feature])
                if child is None:
                    break  # Неизвестная категория: доля класса 1 в текущем узле.
                node = child
            probabilities.append(node.probability)
        return np.asarray(probabilities)

    def predict(self, X, threshold=0.5):
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must lie in [0, 1].")
        return (self.predict_proba(X) >= threshold).astype(int)

    def nodes(self):
        def visit(node, depth):
            yield node, depth
            for child in node.children.values():
                yield from visit(child, depth + 1)
        return list(visit(self.root, 0))

    def statistics(self):
        nodes = self.nodes()
        return {"depth": max(depth for _, depth in nodes),
                "leaves": sum(not node.children for node, _ in nodes),
                "nodes": len(nodes)}

    def text(self, max_depth=None):
        lines = []

        def visit(node, depth, branch):
            label = node.feature if node.feature is not None else "LEAF"
            lines.append(f"{'  ' * depth}{branch}{label}; n={node.samples}; "
                         f"p1={node.probability:.4f}; IG={node.gain:.6f}")
            if max_depth is not None and depth >= max_depth and node.children:
                lines.append(f"{'  ' * (depth + 1)}... subtree omitted")
                return
            for value, child in node.children.items():
                visit(child, depth + 1, f"[{value}] -> ")

        visit(self.root, 0, "")
        return "\n".join(lines)
