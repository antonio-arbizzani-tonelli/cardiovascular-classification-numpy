"""Mathematical and behavioral checks for the independent logistic solver."""

import unittest

import numpy as np

from src.numpy_logistic import _objective_gradient, fit_logistic, sigmoid


class TestNumpyLogistic(unittest.TestCase):
    def test_objective_gradient_matches_independent_finite_differences(self):
        rng = np.random.default_rng(17)
        design = np.column_stack((np.ones(13), rng.normal(size=(13, 4))))
        labels = rng.integers(0, 2, size=13)
        weights = rng.normal(size=5)
        l2 = 0.13
        loss, objective, gradient = _objective_gradient(design, labels, weights, l2)

        def independent_objective(candidate):
            scores = design @ candidate
            return (np.mean(np.logaddexp(0.0, scores) - labels * scores)
                    + l2 * np.sum(candidate[1:] ** 2) / 2.0)

        numerical = np.empty(weights.size)
        for index in range(weights.size):
            positive, negative = weights.copy(), weights.copy()
            positive[index] += 1e-6
            negative[index] -= 1e-6
            numerical[index] = (independent_objective(positive) - independent_objective(negative)) / 2e-6
        np.testing.assert_allclose(gradient, numerical, rtol=1e-6, atol=1e-8)
        self.assertAlmostEqual(objective, independent_objective(weights), places=13)
        self.assertAlmostEqual(objective - loss, l2 * np.sum(weights[1:] ** 2) / 2.0, places=13)

    def test_intercept_only_and_constant_channels_recover_prevalence(self):
        labels = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        for width in (1, 5):
            design = np.zeros((labels.size, width), dtype=np.float64)
            design[:, 0] = 1.0
            result = fit_logistic(design, labels, l2=100.0)
            self.assertEqual(result["status"], "converged")
            self.assertAlmostEqual(result["weights"][0], np.log(0.2 / 0.8), places=12)
            np.testing.assert_array_equal(result["weights"][1:], np.zeros(width - 1))
            np.testing.assert_allclose(sigmoid(design @ result["weights"]), 0.2, atol=1e-14)
            self.assertEqual(result["iterations"], 0)
            self.assertLessEqual(result["gradient_inf_norm"], 1e-6)

    def test_separable_regularized_solution_matches_independent_scalar_root(self):
        values = np.array([-2.0, -1.0, 1.0, 2.0])
        design = np.column_stack((np.ones(values.size), values))
        labels = np.array([0, 0, 1, 1])
        l2 = 0.2
        result = fit_logistic(design, labels, l2=l2, gradient_tolerance=1e-9)
        lower, upper = 0.0, 10.0
        for _ in range(100):
            middle = (lower + upper) / 2.0
            probability = 1.0 / (1.0 + np.exp(-values * middle))
            derivative = np.mean(values * (probability - labels)) + l2 * middle
            if derivative > 0.0:
                upper = middle
            else:
                lower = middle
        self.assertEqual(result["status"], "converged")
        self.assertAlmostEqual(result["weights"][0], 0.0, places=8)
        self.assertAlmostEqual(result["weights"][1], (lower + upper) / 2.0, places=7)
        self.assertLessEqual(result["gradient_inf_norm"], 1e-9)
        self.assertLess(result["objective"], np.log(2.0))
        np.testing.assert_array_equal(sigmoid(design @ result["weights"]) >= 0.5, labels)

    def test_backtracking_stays_finite_and_decreases_objective_on_badly_scaled_data(self):
        values = np.repeat([-3.0, -2.0, -1.0, 1.0, 2.0, 3.0], 20) * 1e6
        labels = np.concatenate([np.r_[np.ones(count), np.zeros(20 - count)]
                                 for count in (2, 4, 7, 13, 16, 18)])
        design = np.column_stack((np.ones(values.size), values))
        result = fit_logistic(design, labels, l2=0.1, max_iter=300,
                              gradient_tolerance=1e-4)
        objectives = np.array([entry["objective"] for entry in result["loss_history"]])
        self.assertTrue(np.all(np.isfinite(objectives)))
        self.assertTrue(np.all(np.diff(objectives) <= 1e-14))
        self.assertTrue(np.all(np.isfinite(result["weights"])))
        self.assertEqual(result["status"], "converged")
        self.assertLess(result["objective"], 0.5)
        self.assertGreater(result["evaluations"], result["iterations"] + 1)

    def test_iteration_limit_is_reported_without_false_convergence(self):
        rng = np.random.default_rng(31)
        design = np.column_stack((np.ones(80), rng.normal(size=(80, 5))))
        labels = (design[:, 1] + 0.2 * design[:, 2] > 0.0).astype(np.int8)
        result = fit_logistic(design, labels, max_iter=1, gradient_tolerance=1e-12)
        self.assertEqual(result["status"], "max_iter_reached")
        self.assertEqual(result["iterations"], 1)
        self.assertGreater(result["gradient_inf_norm"], 1e-12)
        _, _, actual_gradient = _objective_gradient(design, labels, result["weights"], 1e-4)
        self.assertEqual(result["gradient_inf_norm"], np.max(np.abs(actual_gradient)))

    def test_extreme_conditioning_reports_line_search_failure_without_false_success(self):
        values = np.repeat([-3.0, -2.0, -1.0, 1.0, 2.0, 3.0], 20) * 1e150
        labels = np.concatenate([np.r_[np.ones(count), np.zeros(20 - count)]
                                 for count in (2, 4, 7, 13, 16, 18)])
        design = np.column_stack((np.ones(values.size), values))
        result = fit_logistic(design, labels, max_iter=100)
        self.assertEqual(result["status"], "line_search_failed")
        self.assertEqual(result["iterations"], 0)
        self.assertGreater(result["gradient_inf_norm"], 1e-6)
        self.assertTrue(np.isfinite(result["objective"]))
        self.assertTrue(np.all(np.isfinite(result["weights"])))

    def test_extreme_logits_are_stable_and_inputs_are_not_modified(self):
        np.testing.assert_allclose(sigmoid(np.array([-1000.0, 0.0, 1000.0])), [0.0, 0.5, 1.0])
        design = np.array([[1.0, -1000.0], [1.0, 1000.0]])
        loss, objective, gradient = _objective_gradient(design, np.array([1.0, 0.0]),
                                                       np.array([0.0, 1.0]), 0.1)
        self.assertAlmostEqual(loss, 1000.0)
        self.assertTrue(np.isfinite(objective))
        self.assertTrue(np.all(np.isfinite(gradient)))
        original = design.copy()
        labels = np.array([0, 1], dtype=np.int8)
        first = fit_logistic(design, labels, l2=0.2)
        second = fit_logistic(design, labels, l2=0.2)
        np.testing.assert_array_equal(design, original)
        np.testing.assert_array_equal(labels, [0, 1])
        np.testing.assert_array_equal(first["weights"], second["weights"])
        self.assertEqual(first["loss_history"], second["loss_history"])

    def test_invalid_inputs_and_settings_are_rejected(self):
        design = np.array([[1.0, -1.0], [1.0, 1.0]])
        labels = np.array([0, 1])
        invalid = (
            (np.empty((0, 2)), np.array([]), {}),
            (design.ravel(), labels, {}),
            (design, labels[:, None], {}),
            (design, np.array([-1, 1]), {}),
            (np.array([[1.0, np.nan], [1.0, 1.0]]), labels, {}),
            (np.array([[1.0, np.inf], [1.0, 1.0]]), labels, {}),
            (np.array([[0.0, -1.0], [0.0, 1.0]]), labels, {}),
            (design, labels, {"l2": -0.1}),
            (design, labels, {"l2": np.nan}),
            (design, labels, {"max_iter": 0}),
            (design, labels, {"max_iter": True}),
            (design, labels, {"gradient_tolerance": 0}),
            (design, labels, {"gradient_tolerance": np.inf}),
            (design, labels, {"history_size": 0}),
        )
        for matrix, target, settings in invalid:
            with self.subTest(settings=settings, shape=matrix.shape):
                with self.assertRaises(ValueError):
                    fit_logistic(matrix, target, **settings)


if __name__ == "__main__":
    unittest.main()
