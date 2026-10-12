"""Exercise persisted error reports, including Python 3.9 text I/O contracts."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

from src.analyze_errors import run_analysis
from src.compare_boosting_logistic_errors import run_comparison
from src.evaluation import classification_metrics


class TestErrorReportOutputs(unittest.TestCase):
    def setUp(self):
        project = Path(__file__).resolve().parents[1]
        temporary = tempfile.TemporaryDirectory(prefix="tmp_error_report_", dir=project / "tests")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.labels = np.tile(np.array([1, 0, 1, 0], dtype=np.int8), 2)
        self.folds = np.repeat([1, 2], 4).astype(np.int8)
        features = np.column_stack((np.arange(8), np.tile([1, 2], 4))).astype(np.float32)
        np.save(self.root / "features.npy", features)
        (self.root / "header.csv").write_text("Id,A,B\n", encoding="utf-8")
        self._json("metadata.json", [{"name": "B", "documented_values": [
            {"code": "1", "label": "yes"}, {"code": "2", "label": "no"}]}])
        self.analysis_config = {
            "experiment_record_path": "record.json", "features_path": "features.npy",
            "x_train_csv_path": "header.csv", "feature_metadata_path": "metadata.json",
            "continuous_features": [{"name": "A", "bins": [-1, 4, 9], "labels": ["low", "high"]}],
            "categorical_features": ["B"], "cross_feature_pairs": [["A", "B"]],
            "minimum_group_rows": 1, "output_json_path": "analysis.json",
            "output_csv_path": "groups.csv", "output_cross_csv_path": "cross.csv",
            "output_report_path": "analysis.md",
        }
        self._json("analysis_config.json", self.analysis_config)
        self._json("comparison_config.json", {
            "boosting_record_path": "record.json", "logistic_record_path": "record.json",
            "group_config_path": "analysis_config.json", "output_json_path": "comparison.json",
            "output_csv_path": "comparison.csv", "output_report_path": "comparison.md",
        })

    def _json(self, name, payload):
        (self.root / name).write_text(json.dumps(payload), encoding="utf-8")

    def _predictions(self, scores):
        np.savez(self.root / "oof.npz", development_indices=np.arange(8),
                 fold_ids=self.folds, labels=self.labels, probabilities=scores)
        counts, metrics = classification_metrics(self.labels, (scores >= 0.5).astype(np.int8))
        self._json("record.json", {
            "config": {"split": {"id": "synthetic"}},
            "outcome": {
                "nested_threshold_evaluation": {
                    "folds": [{"outer_fold": fold, "inner_threshold": 0.5} for fold in (1, 2)],
                    "pooled_metrics": metrics, "pooled_confusion_counts": asdict(counts)},
                "oof_predictions_artifact": {
                    "path": "oof.npz",
                    "sha256": hashlib.sha256((self.root / "oof.npz").read_bytes()).hexdigest()},
            },
        })

    def test_report_entrypoints_support_python39_text_api_and_lf_output(self):
        self._predictions(np.tile([0.9, 0.9, 0.1, 0.1], 2))
        original_write = Path.write_text

        def python39_write(path, data, encoding=None, errors=None):
            return original_write(path, data, encoding=encoding, errors=errors)

        # Python 3.9's write_text has no newline keyword. Exercise the full
        # readers, metrics, group tables and report persistence under that API.
        with mock.patch.object(Path, "write_text", new=python39_write):
            run_analysis(self.root / "analysis_config.json", self.root)
            run_comparison(self.root / "comparison_config.json", self.root)
        for name in ("analysis.md", "comparison.md"):
            report = (self.root / name).read_bytes()
            self.assertTrue(report.startswith(b"# "))
            self.assertIn(b"\n", report)
            self.assertNotIn(b"\r", report)

    def test_absent_error_categories_still_produce_a_complete_report(self):
        self._predictions(np.where(self.labels == 1, 0.9, 0.1))
        result = run_analysis(self.root / "analysis_config.json", self.root)
        self.assertEqual(result["error_counts"]["false_positive"], 0)
        self.assertEqual(result["error_counts"]["false_negative"], 0)
        report = (self.root / "analysis.md").read_text(encoding="utf-8")
        self.assertIn("| false positive | 0 | — | — | — | — |", report)
        self.assertIn("| false negative | 0 | — | — | — | — |", report)


if __name__ == "__main__":
    unittest.main()
