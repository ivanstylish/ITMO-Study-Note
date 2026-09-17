"""Проверка формул, устойчивости вычислений и разделения данных."""
import unittest
import numpy as np
import pandas as pd
from logistic_regression import FEATURES, sigmoid, log_loss, fit, metrics, prepare, split


class Tests(unittest.TestCase):
    def test_sigmoid(self):
        with np.errstate(over='raise', invalid='raise'):
            np.testing.assert_allclose(sigmoid([-1000, 0, 1000]), [0, 0.5, 1])
            self.assertEqual(log_loss(np.array([1, 0]), np.array([-1000, 1000])), 1000)

    def test_derivatives(self):
        rng = np.random.default_rng(7)
        X, y, w = rng.normal(size=(20, 4)), rng.integers(0, 2, 20), rng.normal(size=4)
        p = sigmoid(X @ w)
        g, H = X.T @ (p-y) / 20, (X.T * (p*(1-p))) @ X / 20
        delta = np.eye(4) * 1e-5
        numeric_g = [(log_loss(y, X@(w+d))-log_loss(y, X@(w-d)))/2e-5 for d in delta]
        numeric_H = [X.T@(sigmoid(X@(w+d))-sigmoid(X@(w-d)))/(20*2e-5) for d in delta]
        np.testing.assert_allclose(g, numeric_g, atol=1e-8)
        np.testing.assert_allclose(H, np.array(numeric_H).T, atol=1e-8)

    def test_optimizers(self):
        rng = np.random.default_rng(4)
        X = np.column_stack([np.ones(150), rng.normal(size=(150, 3))])
        y = (rng.random(150) < sigmoid(X @ [0, .4, -.6, .8])).astype(int)
        a, losses = fit(X, y, .5, 1500, 'gd')
        b, _ = fit(X, y, 1, 20, 'newton')
        np.testing.assert_allclose(a, b, atol=1e-6)
        self.assertTrue((np.diff(losses) <= 1e-10).all())
        _, safeguarded = fit(X, y, 100, 20, 'newton')
        self.assertTrue((np.diff(safeguarded) <= 1e-10).all())

    def test_metrics(self):
        m = metrics(np.array([1, 1, 0, 0]), np.array([1, 0, 1, 0]))
        self.assertTrue(all(m[k] == .5 for k in ['accuracy', 'precision', 'recall', 'f1']))
        self.assertEqual(metrics(np.array([0, 1]), np.array([0, 0]))['precision'], 0)

    def test_preprocessing(self):
        data = pd.DataFrame(np.arange(1, 33).reshape(4, 8), columns=FEATURES)
        data.loc[0, 'Glucose'] = 0
        X, parameters = prepare(data)
        copies = [p.copy() for p in parameters]
        prepare(data * 100000, parameters)
        for a, b in zip(parameters, copies):
            pd.testing.assert_series_equal(a, b)
        self.assertEqual(parameters[0].Glucose, 18)
        np.testing.assert_allclose(X[:, 1:].mean(axis=0), 0, atol=1e-12)

    def test_partition(self):
        y = np.r_[np.zeros(500), np.ones(268)]
        a, b = split(np.arange(768), y, .2, np.random.default_rng(42))
        c, d = split(np.arange(768), y, .2, np.random.default_rng(42))
        self.assertFalse(set(a) & set(b))
        self.assertEqual(len(set(a) | set(b)), 768)
        self.assertEqual(len(b), 154)
        np.testing.assert_array_equal(a, c)
        np.testing.assert_array_equal(b, d)


if __name__ == '__main__':
    unittest.main()
