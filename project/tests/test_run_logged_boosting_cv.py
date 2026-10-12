"""Verify that progress reporting does not change the fitted experiment."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

from src.run_boosting_cv import _fit_checkpoint_probabilities
from src import run_boosting_cv as runner
from src.run_logged_boosting_cv import _logged_fit, run_logged_suite
from src.run_preprocessing_cv import _sha256


class TestLoggedBoostingCV(unittest.TestCase):
    def test_progress_checkpoints_preserve_predictions_and_callback_steps(self):
        rng = np.random.default_rng(34)
        x = rng.normal(size=(120, 4)).astype(np.float32)
        y = (x[:, 0] + x[:, 1] > 0).astype(np.int8)
        parameters = {
            "max_depth": 2, "min_samples_leaf": 5, "n_bins": 8,
            "max_features": 2, "random_seed": 91,
        }
        expected, _ = _fit_checkpoint_probabilities(x[:80], y[:80], x[80:],
                                                   parameters, [30])
        profiles = []
        calls = []
        logged = _logged_fit(_fit_checkpoint_probabilities, profiles, 3)
        with contextlib.redirect_stdout(io.StringIO()):
            actual, _ = logged(x[:80], y[:80], x[80:], parameters, [30],
                               lambda step, model: calls.append(step))
        self.assertEqual(list(actual), [30])
        self.assertEqual(calls, [30])
        np.testing.assert_array_equal(actual[30], expected[30])
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["stage"], "outer")

    def test_logged_runner_forwards_selected_source_and_records_its_fingerprint(self):
        """Exercise the real final selector without expensive training or data."""
        root = Path(__file__).resolve().parents[1]
        selected_path = root / "configs/experiments/final_phase14_validation.json"
        selected_suite = json.loads(selected_path.read_text(encoding="utf-8"))
        features = np.array([[0.0], [1.0]], dtype=np.float32)
        labels = np.array([0, 1], dtype=np.int8)
        for selector in ("phase14", "phase34", None):
            with self.subTest(selector=selector), tempfile.TemporaryDirectory(
                    prefix="tmp_logged_source_", dir=root / "tests") as directory:
                suite = dict(selected_suite)
                if selector is None:
                    suite.pop("implementation")
                else:
                    suite["implementation"] = selector
                config_path = selected_path if selector == "phase14" else Path(directory) / "suite.json"
                if selector != "phase14":
                    config_path.write_text(json.dumps(suite), encoding="utf-8")
                forwarded = []

                def fake_fit(train, y, valid, parameters, steps, callback,
                             implementation=None):
                    forwarded.append(implementation)
                    return {step: np.array([0.2, 0.8]) for step in steps}, {"total_seconds": 0.0}

                def simulated_suite(path, project_root, output):
                    loaded = json.loads(path.read_text(encoding="utf-8"))
                    specification = loaded["models"][0]
                    keyword = ({"implementation": loaded["implementation"]}
                               if "implementation" in loaded else {})
                    scores, _ = runner._fit_checkpoint_probabilities(
                        features, labels, features, specification["parameters"],
                        specification["checkpoints"], **keyword)
                    self.assertEqual(list(scores), specification["checkpoints"])
                    return [runner.save_experiment({}, {}, output)]

                with mock.patch.object(runner, "_fit_checkpoint_probabilities", new=fake_fit), \
                     mock.patch.object(runner, "run_suite", side_effect=simulated_suite), \
                     mock.patch.object(runner, "save_experiment", return_value=Path(directory) / "record.json") as save, \
                     contextlib.redirect_stdout(io.StringIO()):
                    run_logged_suite(config_path, root, Path(directory))
                    self.assertIs(runner._fit_checkpoint_probabilities, fake_fit)
                    self.assertIs(runner.save_experiment, save)
                    self.assertEqual(forwarded, [selector])
                    outcome = save.call_args.args[1]
                    source = ("src/numpy_boosting_phase14.py" if selector == "phase14"
                              else "src/numpy_boosting.py")
                    self.assertEqual(outcome["source_sha256"][source], _sha256(root / source))
                    self.assertIn("src/boosting_implementation.py", outcome["source_sha256"])


if __name__ == "__main__":
    unittest.main()
