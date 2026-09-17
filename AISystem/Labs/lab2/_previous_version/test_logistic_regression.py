"""Numerical and data-isolation checks; no third-party testing framework."""
import unittest
import numpy as np
import pandas as pd
from logistic_regression import (FEATURES, LogisticRegression, Preprocessor,
                                 log_loss, metrics, sigmoid, stratified_split)


class LogisticTests(unittest.TestCase):
    def test_stability(self):
        with np.errstate(over='raise', invalid='raise'):
            np.testing.assert_allclose(sigmoid([-1000, 0, 1000]), [0, 0.5, 1])
            self.assertEqual(log_loss(np.array([1, 0]), np.array([-1000, 1000])), 1000)

    def test_gradient_and_hessian(self):
        rng = np.random.default_rng(7)
        A = LogisticRegression.design(rng.normal(size=(20, 3)))
        y = rng.integers(0, 2, 20)
        w = rng.normal(size=4)
        eps = 1e-5
        p = sigmoid(A @ w)
        g = A.T @ (p - y) / len(y)
        H = (A.T * (p * (1 - p))) @ A / len(y)
        numeric_g, numeric_H = [], []
        for direction in np.eye(4) * eps:
            numeric_g.append((log_loss(y, A @ (w + direction)) - log_loss(y, A @ (w - direction))) / (2 * eps))
            numeric_H.append(A.T @ (sigmoid(A @ (w + direction)) - sigmoid(A @ (w - direction))) / (len(y) * 2 * eps))
        np.testing.assert_allclose(g, numeric_g, atol=1e-8)
        np.testing.assert_allclose(H, np.array(numeric_H).T, atol=1e-8)

    def test_optimizers_agree(self):
        rng = np.random.default_rng(4)
        X = rng.normal(size=(150, 3))
        y = (rng.random(150) < sigmoid(X @ [0.4, -0.6, 0.8])).astype(int)
        gd = LogisticRegression(0.5, 1500, 'gd').fit(X, y)
        newton = LogisticRegression(1.0, 20, 'newton').fit(X, y)
        np.testing.assert_allclose(gd.weights, newton.weights, atol=1e-6)
        for model in (gd, newton):
            self.assertTrue((np.diff(model.loss_history) <= 1e-10).all())

    def test_metrics(self):
        result = metrics([1, 1, 0, 0], [1, 0, 1, 0])
        for name in ['accuracy', 'precision', 'recall', 'f1']:
            self.assertEqual(result[name], 0.5)
        self.assertEqual(metrics([0, 1], [0, 0])['precision'], 0)

    def test_preprocessor_does_not_fit_test(self):
        frame = pd.DataFrame(np.arange(1, 33).reshape(4, 8), columns=FEATURES)
        frame.loc[0, 'Glucose'] = 0
        frame.loc[0, 'Pregnancies'] = 0
        prep = Preprocessor().fit(frame)
        medians = prep.medians.copy()
        prep.transform(frame * 1000000)
        pd.testing.assert_series_equal(prep.medians, medians)
        self.assertEqual(prep.medians.Glucose, 18)
        self.assertEqual(Preprocessor.clean(frame).iloc[0].Pregnancies, 0)
        np.testing.assert_allclose(prep.transform(frame).mean(axis=0), 0, atol=1e-12)

    def test_split_disjoint_and_reproducible(self):
        y = np.r_[np.zeros(500), np.ones(268)]
        a, b = stratified_split(np.arange(768), y, 0.2, np.random.default_rng(42))
        c, d = stratified_split(np.arange(768), y, 0.2, np.random.default_rng(42))
        self.assertFalse(set(a) & set(b))
        self.assertEqual(len(set(a) | set(b)), 768)
        self.assertEqual(len(b), 154)
        np.testing.assert_array_equal(a, c)
        np.testing.assert_array_equal(b, d)


if __name__ == '__main__':
    unittest.main()
