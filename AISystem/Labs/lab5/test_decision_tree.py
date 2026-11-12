"""Малые проверяемые вручную примеры, без библиотечных деревьев и метрик."""
import unittest
from io import StringIO

import numpy as np
import pandas as pd

from decision_tree import DecisionTree, entropy
from experiment import prepare_data
from metrics import binary_metrics, classification_curves, trapezoid_auc


class DecisionTreeTests(unittest.TestCase):
    def test_entropy(self):
        self.assertEqual(entropy([1, 1]), 0)
        self.assertEqual(entropy([0, 1]), 1)
        self.assertAlmostEqual(entropy([0, 0, 0, 1]), 0.8112781244591328)

    def test_multiway_gain_and_importance(self):
        X = pd.DataFrame({"color": ["a", "a", "b", "b", "c", "c"], "constant": ["z"] * 6})
        model = DecisionTree().fit(X, [0, 0, 1, 1, 0, 0])
        self.assertEqual(model.root.feature, "color")
        self.assertEqual(set(model.root.children), {"a", "b", "c"})
        self.assertAlmostEqual(model.importances["color"], entropy([0, 0, 1, 1, 0, 0]))
        self.assertEqual(model.importances["constant"], 0)
        self.assertEqual(model.statistics(), {"depth": 1, "leaves": 3, "nodes": 4})
        np.testing.assert_array_equal(model.predict(X), [0, 0, 1, 1, 0, 0])

    def test_stops_on_zero_gain_and_tie_at_half(self):
        X = pd.DataFrame({"a": ["0", "0", "1", "1"], "b": ["0", "1", "0", "1"]})
        model = DecisionTree().fit(X, [0, 1, 1, 0])
        self.assertIsNone(model.root.feature)  # XOR: оба IG равны нулю.
        np.testing.assert_array_equal(model.predict(X), [1, 1, 1, 1])

    def test_no_features_left_and_fallback_at_current_node(self):
        X = pd.DataFrame({"a": ["a"] * 4 + ["b"] * 3,
                          "b": ["x", "x", "y", "y", "x", "y", "y"]})
        model = DecisionTree().fit(X, [0, 0, 0, 1, 1, 1, 1])
        self.assertEqual(model.root.feature, "a")
        query = pd.DataFrame({"a": ["new", "a", "a"], "b": ["x", "new", "y"]})
        np.testing.assert_allclose(model.predict_proba(query), [4 / 7, 1 / 4, 1 / 2])
        self.assertEqual(model.statistics()["depth"], 2)
        self.assertIn("subtree omitted", model.text(max_depth=1))
        for node, _ in model.nodes():
            if node.children:
                self.assertEqual(sum(n.samples for n in node.children.values()), node.samples)
        for f in model.features:
            self.assertAlmostEqual(model.importances[f], sum(n.gain for n, _ in model.nodes() if n.feature == f))

    def test_validation_and_fit_reset(self):
        X = pd.DataFrame({"a": ["x", "y"]})
        for y in ([0], [0, 2], [np.nan, 1]):
            with self.assertRaises(ValueError):
                DecisionTree().fit(X, y)
        with self.assertRaises(ValueError):
            DecisionTree().fit(pd.DataFrame({"a": [None, "x"]}), [0, 1])
        model = DecisionTree().fit(X, [0, 1]).fit(X, [1, 1])
        self.assertEqual(model.importances, {"a": 0})
        with self.assertRaises(ValueError):
            model.predict(pd.DataFrame({"wrong": ["x"]}))

    def test_data_preparation_missing_and_target_exclusion(self):
        columns = ["STUDENT ID"] + [str(i) for i in range(1, 31)] + ["COURSE ID", "GRADE"]
        frame = pd.DataFrame([["s1"] + ["1"] * 31 + ["2"], ["s2"] + ["2"] * 31 + ["3"]], columns=columns)
        frame.loc[0, "22"] = "?"
        frame.loc[1, "22"] = " "
        _, X, y, missing = prepare_data(StringIO(frame.to_csv(index=False)))
        self.assertEqual(X.shape, (2, 31))
        self.assertNotIn("GRADE", X.columns)
        self.assertNotIn("STUDENT ID", X.columns)
        self.assertEqual(missing["class_attendance"], 2)
        self.assertTrue((X.class_attendance == "<MISSING>").all())
        np.testing.assert_array_equal(y, [0, 1])

    def test_metrics_and_zero_denominators(self):
        m = binary_metrics([1, 1, 1, 0, 0], [1, 0, 0, 1, 0])
        self.assertEqual(m, {"accuracy": 0.4, "precision": 0.5, "recall": 1 / 3,
                             "TP": 1, "FP": 1, "FN": 2, "TN": 1})
        self.assertEqual(binary_metrics([0, 0], [0, 0])["precision"], 0)
        self.assertEqual(binary_metrics([0, 0], [0, 0])["recall"], 0)

    def test_auc_sort_and_ties(self):
        self.assertAlmostEqual(trapezoid_auc([1, 0, 0.5], [1, 0, 0.75]), 0.625)
        for scores, expected_roc, expected_pr in (([0, 1], 1, 1), ([1, 0], 0, 0.25), ([0.5, 0.5], 0.5, 0.75)):
            points, areas = classification_curves([0, 1], scores)
            self.assertAlmostEqual(areas["ROC_AUC"], expected_roc)
            self.assertAlmostEqual(areas["PR_AUC"], expected_pr)
            self.assertEqual((points.FPR.iloc[0], points.TPR.iloc[0]), (0, 0))
            self.assertEqual((points.FPR.iloc[-1], points.TPR.iloc[-1]), (1, 1))
        with self.assertRaises(ValueError):
            classification_curves([1, 1], [0.5, 1])

    def test_roc_auc_against_pairwise_definition(self):
        y = np.array([0, 1, 0, 1, 0, 1])
        scores = np.array([0.1, 0.3, 0.3, 1, 0.6, 0.6])
        points, areas = classification_curves(y, scores, [0, 0.25, 0.75, 1])
        oracle = np.mean([float(p > n) + 0.5 * float(p == n) for p in scores[y == 1] for n in scores[y == 0]])
        self.assertAlmostEqual(areas["ROC_AUC"], oracle)
        self.assertTrue((np.diff(points.recall) >= 0).all())
        self.assertIn(0.25, points.threshold.to_list())


if __name__ == "__main__":
    unittest.main()
