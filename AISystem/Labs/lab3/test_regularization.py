"""Независимые численные проверки оптимизатора и сохранённого эксперимента."""
import json
import unittest

import numpy as np
import pandas as pd

from regularization import (ROOT, TARGET, CATEGORY, NUMERIC, MODELS, VARIANTS,
                            design_matrix, evaluate, fit, preprocess)


class OptimizerTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(17)
        features = rng.normal(size=(200, 3))
        self.x = np.column_stack([np.ones(200), features])
        self.y = self.x @ np.array([5.0, 2.0, -1.0, 0.3]) + rng.normal(0, 0.1, 200)

    def fit(self, variant, strength, ratio):
        return fit(self.x, self.y, strength, ratio, steps=1000)[0]

    def test_unregularized_matches_independent_least_squares(self):
        expected = np.linalg.lstsq(self.x, self.y, rcond=None)[0]
        np.testing.assert_allclose(self.fit("Без регуляризации", 0, 0), expected, atol=1e-9)

    def test_ridge_matches_linear_system_without_intercept_penalty(self):
        strength = 0.7
        gram = self.x.T @ self.x / len(self.y)
        penalty = np.diag([0, strength, strength, strength])
        expected = np.linalg.solve(2*gram + penalty, 2*self.x.T @ self.y / len(self.y))
        np.testing.assert_allclose(self.fit("L2", strength, 0), expected, atol=1e-9)

    def test_l1_and_elasticnet_match_exact_orthogonal_solution(self):
        x = np.array([[1,-1,-1], [1,-1,1], [1,1,-1], [1,1,1]], dtype=float)
        beta = np.array([5, 2, 0.1])
        for ratio in [1.0, 0.5]:
            strength = 0.4
            actual, _ = fit(x, x@beta, strength, ratio, rate=0.1, steps=500)
            expected = np.r_[beta[0], np.sign(beta[1:]) * np.maximum(2*np.abs(beta[1:]) - strength*ratio, 0)
                             / (2 + strength*(1-ratio))]
            np.testing.assert_allclose(actual, expected, atol=1e-10)
            self.assertEqual(actual[2], 0.0)

    def test_l1_elasticnet_optima_satisfy_subgradient_conditions(self):
        strength = 0.8
        for ratio in [0.2, 0.8, 1.0]:
            w, _ = fit(self.x, self.y, strength, ratio, steps=1000)
            gradient = 2*self.x.T@(self.x@w-self.y)/len(self.y)
            gradient[1:] += strength*(1-ratio)*w[1:]
            self.assertAlmostEqual(gradient[0], 0, places=9)
            active = w[1:] != 0
            np.testing.assert_allclose(gradient[1:][active] + strength*ratio*np.sign(w[1:][active]), 0, atol=1e-9)
            self.assertTrue((np.abs(gradient[1:][~active]) <= strength*ratio+1e-9).all())

    def test_history_has_all_iterations_and_identical_initial_weights(self):
        initial_losses = []
        for strength, ratio in [(0, 0), (0.1, 1)]:
            weights, history = fit(self.x, self.y, strength, ratio,
                                  steps=50, validation=(self.x, self.y))
            self.assertEqual(history.shape, (51, 4))
            initial_losses.append(history[0, 0])
            self.assertAlmostEqual(history[-1, 0], evaluate(self.y, self.x@weights)["MSE"], places=10)
        self.assertEqual(initial_losses[0], initial_losses[1])

    def test_constant_target_intercept_is_never_regularized(self):
        for strength, ratio in [(10, 1), (10, 0), (10, 0.5)]:
            x = np.column_stack([np.ones(20), np.tile([-1, 1], 10)])
            weights, _ = fit(x, np.full(20, 7.0), strength, ratio, steps=1000)
            np.testing.assert_allclose(weights, [7, 0], atol=1e-10)

    def test_imputation_parameters_use_only_training_values(self):
        train = pd.DataFrame({c: [1.0, 3.0, np.nan] for c in NUMERIC})
        train[CATEGORY] = ["Yes", "Yes", "No"]
        holdout = pd.DataFrame({c: [10000.0, np.nan] for c in NUMERIC})
        holdout[CATEGORY] = ["No", None]
        frames, parameters = preprocess([train, holdout])
        result = frames[1]
        self.assertEqual(result[NUMERIC[0]].iloc[1], 2.0)
        self.assertEqual(result[CATEGORY].iloc[1], 1)
        self.assertEqual(parameters, preprocess([train])[1])


class SavedExperimentTests(unittest.TestCase):
    def test_saved_predictions_metrics_normalization_and_split(self):
        out = ROOT / "output"
        if not (out / "summary.json").exists():
            self.skipTest("Сначала запустите regularization.py")
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        raw = pd.read_csv(summary["dataset"])
        split = pd.read_csv(out / "split.csv")
        self.assertTrue(split.row_id.is_unique)
        self.assertEqual(len(split), summary["clean_rows"])
        counts = split.split.value_counts().to_dict()
        self.assertEqual(counts, summary["split_sizes"])
        predictions = pd.read_csv(out / "test_predictions.csv")
        self.assertEqual(set(predictions.row_id), set(split[split.split == "test"].row_id))
        raw_train = raw.iloc[split[split.split == "train"].row_id].copy()
        raw_test = raw.iloc[predictions.row_id].copy()
        (train, test), preprocessing = preprocess([raw_train, raw_test])
        self.assertEqual(preprocessing, summary["preprocessing"])
        metrics = pd.read_csv(out / "metrics.csv")
        archive = np.load(out / "models.npz")
        for number, (name, features) in enumerate(MODELS.items(), 1):
            parameters = summary["normalization"][name]
            np.testing.assert_allclose(parameters["mean"], train[features].mean(), atol=1e-12)
            np.testing.assert_allclose(parameters["scale"], train[features].std(ddof=0), atol=1e-12)
            matrix = design_matrix(test, features, np.array(parameters["mean"]), np.array(parameters["scale"]))
            history = pd.read_csv(out / f"model_{number}_history.csv")
            self.assertEqual(len(history), summary["iterations"] + 1)
            for i, variant in enumerate(VARIANTS):
                predicted = matrix @ archive[f"model_{number}_weights"][:, i]
                np.testing.assert_allclose(predicted, predictions[name + "_" + variant], atol=1e-10)
                actual_scores = evaluate(test[TARGET].to_numpy(), predicted)
                row = metrics[(metrics.model == name) & (metrics.variant == variant)].iloc[0]
                for key, value in actual_scores.items():
                    self.assertAlmostEqual(row["test_" + key], value, places=9)
                self.assertAlmostEqual(history[variant+"_train_MSE"].iloc[-1], row.train_MSE, places=8)
                self.assertAlmostEqual(history[variant+"_validation_MSE"].iloc[-1], row.validation_MSE, places=8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
