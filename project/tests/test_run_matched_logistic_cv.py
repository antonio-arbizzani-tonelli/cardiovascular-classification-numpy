"""Check shared cleaning and nested evaluation boundaries for Phase 38."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.run_matched_logistic_cv import logistic_designs, nested_cv, paired_comparison
from src.run_preprocessing_cv import _stratified_folds


class TestMatchedLogistic(unittest.TestCase):
    def test_finite_adapter_uses_training_statistics_and_preserves_missingness(self):
        metadata = [{'name': 'amount', 'semantic_type': 'continuous'},
                    {'name': 'category', 'semantic_type': 'categorical'}]
        train = np.array([[1., 1.], [3., 1.], [np.nan, 2.], [5., np.nan]])
        validation = np.array([[np.nan, np.nan], [1000., 3.]])
        a, b, state = logistic_designs(train, validation, ['amount', 'category'], metadata)
        a2, _, state2 = logistic_designs(train, validation * 1000, ['amount', 'category'], metadata)
        np.testing.assert_array_equal(a, a2)
        self.assertEqual(state, state2)
        self.assertEqual(state['fill_values'], [3., 1.])
        self.assertEqual(a.shape, (4, 5))
        self.assertAlmostEqual(b[0, 1], 0.0)
        self.assertAlmostEqual(b[0, 3], (1 - 0.25) / np.sqrt(0.25 * 0.75))
        self.assertTrue(np.all(np.isfinite(b)))
        self.assertTrue(np.isnan(train[2, 0]))

    def test_nested_fit_artifacts_prove_no_outer_validation_rows_enter_inner_fits(self):
        x = np.column_stack([np.arange(120), np.tile([888., 101., 777., 201.], 30), np.ones(120)])
        y = np.tile([0, 1], 60).astype(np.int8)
        development = np.arange(100, dtype=np.int64)
        names = ['row', 'ALCDAY5', '_AGEG5YR']
        metadata = [{'name': name, 'semantic_type': 'count'} for name in names]
        plan = {'exclude_features': ['_AGEG5YR'], 'auxiliary_missing_features': ['_AGEG5YR'],
                'missing_code_overrides': {'ALCDAY5': [{'code': 777, 'reason': 'unknown'}]},
                'zero_code_overrides': {'ALCDAY5': [888]}}
        suite = {'fold_count': 3, 'outer_seed': 20260919, 'inner_fold_count': 2,
                 'inner_seed': 20260922, 'source_feature_count': 2,
                 'logistic_adapter': {'missing_indicators': True}, 'model': {}}

        def fitted(design, labels):
            weights = np.array([-1., 0.2, 0.1, 0., 0.1])
            return {'weights': weights, 'status': 'converged', 'iterations': 1, 'gradient_inf_norm': 0.}

        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            folder = Path(directory)
            outcome, predictions = nested_cv(x, y, development, names, metadata, plan, suite, folder, fitted)
            self.assertEqual(len(outcome['fits']), 9)
            self.assertEqual(predictions.shape, (100,))
            for outer, (train, valid) in enumerate(_stratified_folds(y[development], 3, 20260919), 1):
                with np.load(folder / f'outer{outer}.npz') as fit:
                    np.testing.assert_array_equal(fit['training_indices'], development[train])
                    self.assertEqual(fit['source_names'].tolist(), ['row', 'ALCDAY5'])
                    self.assertEqual(fit['weights'].size, 5)
                inner_evaluations = []
                for inner in (1, 2):
                    with np.load(folder / f'outer{outer}_inner{inner}.npz') as fit:
                        training = fit['training_indices']
                        evaluation = fit['validation_indices']
                        self.assertEqual(np.intersect1d(training, development[valid]).size, 0)
                        self.assertEqual(np.intersect1d(evaluation, development[valid]).size, 0)
                        self.assertEqual(np.intersect1d(training, evaluation).size, 0)
                        inner_evaluations.extend(evaluation.tolist())
                self.assertEqual(sorted(inner_evaluations), sorted(development[train].tolist()))

    def test_nonconverged_fit_is_rejected_before_result_publication(self):
        suite = {'fold_count': 3, 'outer_seed': 1, 'inner_fold_count': 2, 'inner_seed': 2,
                 'source_feature_count': 1, 'logistic_adapter': {'missing_indicators': False}, 'model': {}}
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            with self.assertRaisesRegex(RuntimeError, 'did not converge'):
                nested_cv(np.arange(30).reshape(-1, 1), np.tile([0, 1], 15), np.arange(30), ['x'],
                          [{'name': 'x', 'semantic_type': 'count'}], {}, suite, Path(directory),
                          lambda *args, **kwargs: {'status': 'max_iter_reached', 'gradient_inf_norm': 1.})
            self.assertFalse(list(Path(directory).glob('*.npz')))

    def test_paired_bootstrap_matches_known_perfect_and_zero_f1_difference(self):
        y = np.array([0, 0, 1, 1])
        zero = np.zeros(4, dtype=np.int8)
        result = paired_comparison(y, zero, y, resamples=100)
        self.assertEqual(result['booster_minus_logistic_f1_interval_95'], [1., 1.])
        result = paired_comparison(y, y, y, resamples=100)
        self.assertEqual(result['booster_minus_logistic_f1_interval_95'], [0., 0.])


if __name__ == '__main__':
    unittest.main()
