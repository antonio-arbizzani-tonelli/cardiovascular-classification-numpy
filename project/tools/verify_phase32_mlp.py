"""Replay all MLP OOF checkpoints and compare nested F1 with Phase 14."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.evaluation import average_precision, best_f1_threshold, binary_log_loss, classification_metrics
from src.run_mlp_cv import load_pipeline, predict_pipeline
from src.run_preprocessing_cv import _as_binary_labels, _sha256


def load_arrays(path):
    """Read compressed arrays and immediately close their Windows file handles."""
    with np.load(path) as saved:
        return {key: saved[key] for key in saved.files}


def verify():
    """Require complete fold coverage, independent selection and reproducible inference."""
    artifact = ROOT / "results/mlp_artifacts/phase32"
    preflight = json.loads((artifact / "preflight.json").read_text())
    status = json.loads((artifact / "status.json").read_text())
    if status["status"] != "completed":
        raise RuntimeError("The MLP evaluation is not complete.")
    for configured, fingerprint in preflight["protected_files"].items():
        assert _sha256(ROOT / configured) == fingerprint, configured
    suite = json.loads((ROOT / "configs/experiments/phase32_mlp.json").read_text())
    source = np.load(ROOT / suite["data"]["features_path"], mmap_mode="r")
    labels = _as_binary_labels(np.load(ROOT / suite["data"]["labels_path"]))
    baseline = json.loads((ROOT / preflight["baseline_record"]).read_text())
    base_oof = load_arrays(ROOT / baseline["outcome"]["oof_predictions_artifact"]["path"])
    base_evaluation = baseline["outcome"]["nested_threshold_evaluation"]
    baseline_f1 = classification_metrics(base_oof["labels"], base_oof["nested_predictions"])[1]["f1"]
    assert baseline_f1 == preflight["baseline_f1"]
    candidates = []
    for configured_record in status["records"]:
        record_path = Path(configured_record)
        record = json.loads(record_path.read_text())
        name = record["config"]["experiment_name"].removeprefix("phase32_mlp_")
        outcome = record["outcome"]
        oof_path = ROOT / outcome["oof_predictions_artifact"]["path"]
        assert _sha256(oof_path) == outcome["oof_predictions_artifact"]["sha256"]
        oof = load_arrays(oof_path)
        for key in ("development_indices", "fold_ids", "labels"):
            np.testing.assert_array_equal(oof[key], base_oof[key])
        counts, metrics = classification_metrics(oof["labels"], oof["nested_predictions"])
        metrics["average_precision"] = average_precision(oof["labels"], oof["probabilities"])
        metrics["log_loss"] = binary_log_loss(oof["labels"], oof["probabilities"])
        assert metrics == outcome["metrics"]
        folds = []
        maximum_replay_error = 0.0
        checkpoint_count = 0
        for fold in outcome["nested_threshold_evaluation"]["folds"]:
            number = fold["outer_fold"]
            inner = load_arrays(fold["inner_oof_predictions_artifact"]["path"])
            assert _sha256(Path(fold["inner_oof_predictions_artifact"]["path"])) == fold["inner_oof_predictions_artifact"]["sha256"]
            choice = best_f1_threshold(inner["labels"], inner["probabilities"])
            assert choice.threshold == fold["inner_threshold"]
            positions = oof["fold_ids"] == number
            np.testing.assert_array_equal(oof["nested_thresholds"][positions], choice.threshold)
            for tag, target_rows, target_probabilities, model_details in [
                (f"outer{number}", oof["development_indices"][positions], oof["probabilities"][positions], fold["outer_fit"]),
                *[(inner_fit["tag"], inner["training_row_indices"][inner["fold_ids"] == inner_number],
                   inner["probabilities"][inner["fold_ids"] == inner_number], inner_fit["models"][name])
                  for inner_number, inner_fit in enumerate(fold["inner_fits"], 1)]
            ]:
                boundaries = load_arrays(artifact / f"{tag}_boundaries.npz")
                for part in ("gradient_fit_rows", "early_stopping_rows"):
                    assert np.intersect1d(boundaries[part], boundaries["evaluation_rows"]).size == 0
                np.testing.assert_array_equal(np.sort(np.r_[boundaries["gradient_fit_rows"], boundaries["early_stopping_rows"]]),
                                              np.sort(boundaries["training_rows"]))
                np.testing.assert_array_equal(boundaries["evaluation_rows"], target_rows)
                np.testing.assert_array_equal(labels[target_rows],
                    oof["labels"][positions] if tag == f"outer{number}" else inner["labels"][inner["fold_ids"] == int(tag[-1])])
                checkpoint = Path(model_details["checkpoint"]["path"])
                assert _sha256(checkpoint) == model_details["checkpoint"]["sha256"]
                payload = load_pipeline(checkpoint)
                assert payload["model"].epochs_trained_ == model_details["selected_epochs"]
                replay = predict_pipeline(payload, source[target_rows])
                maximum_replay_error = max(maximum_replay_error, float(np.max(np.abs(replay - target_probabilities))))
                np.testing.assert_allclose(replay, target_probabilities, atol=1e-7, rtol=1e-6)
                np.testing.assert_array_equal(replay >= choice.threshold, target_probabilities >= choice.threshold)
                checkpoint_count += 1
            base_fold = base_evaluation["folds"][number - 1]
            folds.append({"fold": number, "f1": fold["outer_evaluation_metrics"]["f1"],
                          "delta_f1": fold["outer_evaluation_metrics"]["f1"] - base_fold["outer_evaluation_metrics"]["f1"],
                          "threshold": choice.threshold, "selected_epochs": fold["outer_fit"]["selected_epochs"],
                          "output_features": fold["output_features"]})
        candidates.append({"name": name, "record": str(record_path.relative_to(ROOT)),
                           "metrics": metrics, "delta_f1": metrics["f1"] - baseline_f1,
                           "folds": folds, "favorable_folds": sum(f["delta_f1"] > 0 for f in folds),
                           "checkpoints_replayed": checkpoint_count,
                           "maximum_replay_error": maximum_replay_error,
                           "operational_promotion_criterion_met": metrics["f1"] > baseline_f1 and sum(f["delta_f1"] > 0 for f in folds) >= 2})
    comparison = {"baseline": {"name": "Phase 14", "metrics": base_evaluation["pooled_metrics"]},
                  "candidates": candidates, "development_rows": len(base_oof["labels"]),
                  "runtime_seconds": status["runtime_seconds"], "protected_files_unchanged": True,
                  "verification": "All nine refit checkpoints per candidate, inner thresholds and every OOF label/classification replayed.",
                  "limitations": "Development CV after repeated model selection; one initialization seed. No untouched test result or automatic promotion."}
    destination = ROOT / "results/experiments/mlp/phase32_comparison.json"
    destination.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase 32 — MLP with dedicated preprocessing", "",
             f"Complete evaluation: {comparison['development_rows']:,} development rows, three outer and two inner folds. "
             "F1 thresholds selected on inner OOF predictions. Epoch selection uses a 10% training holdout, followed by full-partition refitting.", "",
             "| Model | F1 | Delta Phase 14 | Precision | Recall | AP | Log loss | Favorable folds |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
             f"| Phase 14 | {baseline_f1:.9f} | — | {base_evaluation['pooled_metrics']['precision']:.6f} | "
             f"{base_evaluation['pooled_metrics']['recall']:.6f} | {base_evaluation['pooled_metrics']['average_precision']:.6f} | "
             f"{base_evaluation['pooled_metrics']['log_loss']:.6f} | — |"]
    for candidate in candidates:
        m = candidate["metrics"]
        lines.append(f"| {candidate['name']} | {m['f1']:.9f} | {candidate['delta_f1']:+.9f} | {m['precision']:.6f} | "
                     f"{m['recall']:.6f} | {m['average_precision']:.6f} | {m['log_loss']:.6f} | {candidate['favorable_folds']}/3 |")
    lines += ["", "| Model / fold | F1 | Delta Phase 14 | Inner threshold | Refit epochs | Input |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for candidate in candidates:
        for fold in candidate["folds"]:
            lines.append(f"| {candidate['name']} / {fold['fold']} | {fold['f1']:.9f} | {fold['delta_f1']:+.9f} | "
                         f"{fold['threshold']:.9f} | {fold['selected_epochs']} | {fold['output_features']} |")
    lines += ["", f"Shared suite runtime: {status['runtime_seconds'] / 60:.2f} minutes. "
              "Includes preprocessing, 18 epoch-selection runs and 18 refits; this is not each candidate's individual runtime.", "",
              "Data, labels, metadata and splits match the baseline; historical F1 is recomputed from OOF predictions. "
              "All 18 refit checkpoints reproduce saved scores and classifications. "
              "Gradient-fit, early-stopping and evaluation boundaries, thresholds, metrics and hashes verified. "
              "Seven protected booster files retain their preflight hashes.", "",
              "The MLP uses 295 source features plus the plan's auxiliary age flag. Codebook cleaning is shared; "
              "imputation, scaling, one-hot encoding, missing/unseen flags and converted frequencies are MLP-specific. "
              "The comparison evaluates complete pipelines rather than model family alone.", "",
              "Both MLPs have lower F1 than Phase 14 in all three folds. HAREHAB1 is included; "
              "its target relationship is described in the [final report](../../docs/FINAL_REPORT.md#harehab1). "
              "Executed environment: Python 3.14.3 / NumPy 2.4.2, OpenBLAS with one thread; official-environment execution unverified.", "",
              "Phase 14 remains the selected model. "
              "Details: [MLP pipeline](../../docs/MLP.md), "
              "[full comparison](../experiments/mlp/phase32_comparison.json). "
              "Local checkpoints are in `results/mlp_artifacts/phase32/`."]
    (ROOT / "results/eda/phase32_mlp_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": str(destination), "candidates": candidates}, indent=2), flush=True)


if __name__ == "__main__":
    verify()
