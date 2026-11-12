"""用可手算样例验证算法、指标和数据划分，不调用现成算法或指标。"""
import unittest
import numpy as np
from knn import KNN
from metrics import classification_metrics, regression_metrics, confusion_matrix
from experiment import prepare_data


class KNNTests(unittest.TestCase):
    def test_three_distances(self):
        x, y = [[3, 0], [2, 2], [1.6, 1.6]], [10, 20, 30]
        expected = {"euclidean": 30, "manhattan": 10, "chebyshev": 30}
        for metric, label in expected.items():
            self.assertEqual(KNN(1, metric=metric).fit(x, y).predict([[0, 0]])[0], label)
        # 这个样例单独区分 L2 与 L∞。
        for metric, label in {"euclidean": 10, "chebyshev": 20}.items():
            self.assertEqual(KNN(1, metric=metric).fit([[3, 0], [2.2, 2.2]], [10, 20])
                             .predict([[0, 0]])[0], label)

    def test_voting_and_ties(self):
        # 票数优先于距离；票数相同时比较距离和，仍相同则选小标签。
        self.assertEqual(KNN(3).fit([[1], [2], [3]], [0, 1, 1]).predict([[0]])[0], 1)
        self.assertEqual(KNN(4).fit([[1], [2], [3], [10]], [2, 2, 1, 1]).predict([[0]])[0], 2)
        self.assertEqual(KNN(2).fit([[-1], [1]], [2, 1]).predict([[0]])[0], 1)
        self.assertEqual(KNN(1).fit([[-1], [1]], [2, 1]).predict([[0]])[0], 2)

    def test_regression_mean(self):
        model = KNN(2, "regression").fit([[0], [2], [8]], [2, 6, 100])
        np.testing.assert_allclose(model.predict([[1], [7]]), [4, 53])

    def test_invalid_inputs(self):
        for k in [0, -1, 1.5, True]:
            with self.assertRaises(ValueError):
                KNN(k)
        for kwargs in [{"task": "other"}, {"metric": "other"}]:
            with self.assertRaises(ValueError):
                KNN(**kwargs)
        with self.assertRaises(ValueError):
            KNN(1).predict([[0]])
        for x, y in [([[0]], [1]), ([[float("nan")], [1]], [1, 2]), ([[0], [1]], [1])]:
            with self.assertRaises(ValueError):
                KNN(2).fit(x, y)
        with self.assertRaises(ValueError):
            KNN(1).fit([[0]], [1]).predict([[0, 1]])

    def test_classification_metrics(self):
        actual, predicted = [0, 0, 1, 1, 2, 2], [0, 1, 1, 1, 1, 2]
        expected = np.array([[1, 1, 0], [0, 2, 0], [0, 1, 1]])
        np.testing.assert_array_equal(confusion_matrix(actual, predicted, [0, 1, 2]), expected)
        result = classification_metrics(actual, predicted)
        self.assertAlmostEqual(result["accuracy"], 2 / 3)
        self.assertAlmostEqual(result["precision_macro"], 5 / 6)
        self.assertAlmostEqual(result["recall_macro"], 2 / 3)
        self.assertAlmostEqual(result["F1_macro"], 2 / 3)
        missing = classification_metrics([0, 1], [0, 0])
        self.assertAlmostEqual(missing["F1_macro"], 1 / 3)
        with self.assertRaises(ValueError):
            confusion_matrix([0, 1], [0, 0], [0])

    def test_regression_metrics(self):
        scores = regression_metrics([1, 2, 3], [1, 2, 4])
        self.assertAlmostEqual(scores["MAE"], 1 / 3)
        self.assertAlmostEqual(scores["MSE"], 1 / 3)
        self.assertAlmostEqual(scores["R2"], 0.5)
        self.assertLess(regression_metrics([1, 2, 3], [10, 10, 10])["R2"], 0)
        self.assertTrue(np.isnan(regression_metrics([1, 1], [1, 1])["R2"]))
        for actual, predicted in [([], []), ([1], [1, 2]), ([1], [float("inf")])]:
            with self.assertRaises(ValueError):
                regression_metrics(actual, predicted)

    def test_split_and_train_only_scaling(self):
        x = np.column_stack([np.arange(60) ** 2, np.ones(60)])
        y = np.repeat([0, 1, 2], 20)
        xs, ys, indices, mean, scale = prepare_data(x, y, True)
        self.assertEqual([len(i) for i in indices], [36, 12, 12])
        np.testing.assert_array_equal(np.sort(np.concatenate(indices)), np.arange(60))
        for target in ys:
            self.assertEqual(len(set(np.unique(target, return_counts=True)[1])), 1)
        np.testing.assert_allclose(xs[0].mean(axis=0), [0, 0], atol=1e-14)
        changed = x.copy()
        changed[np.concatenate(indices[1:]), 0] += 100000
        _, _, repeated, other_mean, other_scale = prepare_data(changed, y, True)
        np.testing.assert_array_equal(indices[0], repeated[0])
        np.testing.assert_array_equal(mean, other_mean)
        np.testing.assert_array_equal(scale, other_scale)


if __name__ == "__main__":
    unittest.main()
