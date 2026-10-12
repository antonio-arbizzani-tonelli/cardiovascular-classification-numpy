"""Verify and report the controlled Phase 20 binning experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from src.evaluation import classification_metrics
from src.feature_preprocessing import load_feature_metadata, tree_feature_matrices
from src.numpy_boosting import HistogramGradientBoostingClassifier
from src.run_preprocessing_cv import _as_binary_labels, _load_feature_names, _sha256, _stratified_folds
from src.summarize_phase19_transfer import BASELINE, _arrays, _paired_interval, _publish


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    root = Path.cwd()
    baseline = json.loads((root / BASELINE).read_text(encoding="utf-8"))
    record = json.loads(args.record.read_text(encoding="utf-8"))
    preflight = json.loads((root / "results/eda/phase20_binning_preflight.json").read_text(encoding="utf-8"))
    for key in ("features", "labels", "split_indices", "feature_metadata", "preprocessing_config"):
        if record["outcome"]["input_sha256"][key] != baseline["outcome"]["input_sha256"][key]:
            raise ValueError(f"Candidate changed baseline input {key}.")
    for key in ("features", "split"):
        if record["config"][key] != baseline["config"][key]:
            raise ValueError(f"Candidate changed {key}.")
    bparams = baseline["config"]["model"]["parameters"]
    cparams = dict(record["config"]["model"]["parameters"])
    if cparams.pop("binning_strategy", None) != "exact_low_cardinality" or cparams != bparams:
        raise ValueError("Candidate does not isolate the binning policy.")
    for path, expected in record["outcome"]["source_sha256"].items():
        if _sha256(root / path) != expected:
            raise ValueError(f"Source changed while fitting: {path}.")
    if _sha256(root / "configs/final_model.json") != preflight["final_config_sha256"]:
        raise ValueError("The configured final model changed during the experiment.")
    profiles = record["outcome"]["individual_fit_profiles"]
    if len(profiles) != 9:
        raise ValueError("Expected nine completed predictive fits.")
    partitions = {p["partition"]: p for p in preflight["partitions"]}
    for number, profile in enumerate(profiles, 1):
        partition = (f"outer_{number}" if number <= 3
                     else f"outer_{(number - 4) // 2 + 1}_inner_{(number - 4) % 2 + 1}")
        expected = partitions[partition]
        if profile["binning_strategy"] != "exact_low_cardinality":
            raise ValueError("A fit did not use the requested policy.")
        if profile["bin_counts"] != expected["bin_counts"]:
            raise ValueError(f"Actual bin counts differ from preflight: {partition}.")
        if len(profile["exact_column_indices"]) != expected["exact_columns"]:
            raise ValueError(f"Actual exact columns differ: {partition}.")
    barray, carray = _arrays(root, baseline), _arrays(root, record)
    for key in ("development_indices", "fold_ids", "labels"):
        if not np.array_equal(barray[key], carray[key]):
            raise ValueError(f"Candidate OOF alignment differs: {key}.")
    for arrays, rec in ((barray, baseline), (carray, record)):
        if not np.array_equal(arrays["nested_predictions"], arrays["probabilities"] >= arrays["nested_thresholds"]):
            raise ValueError("Nested predictions differ from their thresholds.")
        _, checked = classification_metrics(arrays["labels"], arrays["nested_predictions"])
        for key, value in checked.items():
            saved = rec["outcome"]["nested_threshold_evaluation"]["pooled_metrics"].get(key)
            if saved is not None and not np.isclose(value, saved, rtol=0, atol=1e-15):
                raise ValueError(f"Recomputed nested metric differs: {key}.")
    for checkpoint in record["outcome"]["model_checkpoints"]:
        if _sha256(root / checkpoint["path"]) != checkpoint["sha256"]:
            raise ValueError("Candidate checkpoint hash differs.")
    suite = json.loads((root / "configs/experiments/phase20_phase14_exact_low_cardinality.json").read_text(encoding="utf-8"))
    preprocessing = json.loads((root / suite["preprocessing_config_path"]).read_text(encoding="utf-8"))
    plan = next(v["preprocessing"] for v in preprocessing["variants"] if v["experiment_name"] == suite["preprocessing_variant"])
    x = np.load(root / suite["data"]["features_path"], mmap_mode="r")
    y = _as_binary_labels(np.load(root / suite["data"]["labels_path"]))
    names = _load_feature_names(root / suite["data"]["x_train_csv_path"])
    metadata = load_feature_metadata(root / suite["feature_metadata_path"])
    development = carray["development_indices"]
    prediction_checks = []
    folds = _stratified_folds(y[development], 3, suite["seed"])
    for fold, (checkpoint, reference, (train, valid)) in enumerate(zip(
            record["outcome"]["model_checkpoints"], baseline["outcome"]["model_checkpoints"], folds), 1):
        model, checkpoint_metadata = HistogramGradientBoostingClassifier.load_checkpoint(root / checkpoint["path"])
        if _sha256(root / reference["path"]) != reference["sha256"]:
            raise ValueError("Reference checkpoint hash differs.")
        reference_model, reference_metadata = HistogramGradientBoostingClassifier.load_checkpoint(root / reference["path"])
        for key in ("training_row_indices_sha256", "training_labels_sha256"):
            if checkpoint_metadata[key] != reference_metadata[key]:
                raise ValueError(f"Checkpoint training inputs differ: {key}.")
        del reference_model
        clean_train, clean_valid, _ = tree_feature_matrices(np.asarray(x[development[train]], dtype=np.float32),
            np.asarray(x[development[valid]], dtype=np.float32), names, metadata, plan)
        if model.binning_strategy != "exact_low_cardinality":
            raise ValueError("Checkpoint lacks the new binning policy.")
        difference = float(np.max(np.abs(model.predict_proba(clean_valid)[:, 1] - carray["probabilities"][valid])))
        if difference != 0.0:
            raise ValueError("Checkpoint predictions differ from the OOF artifact.")
        prediction_checks.append({"fold": fold, "maximum_probability_difference": difference})
        print(f"Verified checkpoint fold={fold}: probability difference={difference}", flush=True)
        del model, clean_train, clean_valid
    bnest = baseline["outcome"]["nested_threshold_evaluation"]
    cnest = record["outcome"]["nested_threshold_evaluation"]
    if len(cnest["folds"]) != 3:
        raise ValueError("Candidate lacks three completed outer folds.")
    deltas = {key: value - bnest["pooled_metrics"][key] for key, value in cnest["pooled_metrics"].items()}
    fold_deltas = [c["outer_evaluation_metrics"]["f1"] - b["outer_evaluation_metrics"]["f1"]
                   for b, c in zip(bnest["folds"], cnest["folds"])]
    labels, bp, cp = carray["labels"], barray["nested_predictions"], carray["nested_predictions"]
    flips = {
        "recovered_false_negatives": int(np.sum((labels == 1) & (bp == 0) & (cp == 1))),
        "lost_true_positives": int(np.sum((labels == 1) & (bp == 1) & (cp == 0))),
        "added_false_positives": int(np.sum((labels == 0) & (bp == 0) & (cp == 1))),
        "removed_false_positives": int(np.sum((labels == 0) & (bp == 1) & (cp == 0))),
    }
    promote = deltas["f1"] > 0 and sum(d > 0 for d in fold_deltas) >= 2
    published = _publish(args.record, root)
    summary = {
        "baseline_record": BASELINE, "candidate_record": str(published.relative_to(root)).replace("\\", "/"),
        "baseline_nested": bnest, "candidate_nested": cnest, "metric_deltas": deltas,
        "fold_f1_deltas": fold_deltas, "positive_fold_count": sum(d > 0 for d in fold_deltas),
        "meets_plan_promotion_rule": promote, "decision_changes": flips,
        "paired_conditional_f1_delta_interval_95": _paired_interval(labels, bp, cp),
        "bootstrap_seed": 20260929, "bootstrap_repetitions": 20000,
        "bootstrap_scope": "Paired stratified rows, fixed fitted models and thresholds; excludes training and model-selection uncertainty.",
        "probability_correlation": float(np.corrcoef(barray["probabilities"], carray["probabilities"])[0, 1]),
        "mean_absolute_probability_difference": float(np.mean(np.abs(barray["probabilities"] - carray["probabilities"]))),
        "runtime_seconds": record["outcome"]["runtime_seconds"], "individual_fit_profiles": profiles,
        "checkpoint_prediction_checks": prediction_checks,
        "exploratory_same_oof_threshold_f1": {
            "baseline": baseline["outcome"]["metrics"]["f1"],
            "candidate": record["outcome"]["metrics"]["f1"],
            "scope": "Optimistic diagnostic: threshold chosen on the labels being scored; not used for promotion.",
        },
        "environment": record["outcome"]["environment"], "final_model_changed": False,
    }
    out = root / "results/experiments/phase20_binning_comparison.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# Phase 20 — exact binning for low-cardinality columns", "",
             "## Protocol and checks", "",
             "Isolated comparison with Phase 14: the same 295 features, code cleaning, booster parameters and splits. The only addition is `binning_strategy=exact_low_cardinality`. Up to 64 distinct finite training values are retained exactly; higher-cardinality columns use the original quantile binning. NaNs remain in bin 255.", "",
             "Exact columns also consider an observed-versus-missing split: without this boundary, removing empty bins could reduce existing model capacity. Quantile columns retain the original boundary search.", "",
             "Validation uses 262,508 development examples, three outer folds and two inner folds for each threshold. Nine complete 200-tree fits; Phase 14 is reused without retraining. Unit tests train small synthetic models. An earlier CV attempt stopped after a logging failure before its first fit completed; it contributes neither results nor recorded runtime.", "",
             "All 95 tests passed before training. Preflight checks of nine partitions confirm exact categories, unchanged quantile fallback and preserved missing values. The three Phase 14 checkpoints reproduce saved predictions with zero maximum difference. All nine actual fit profiles match the preflight bin counts.", "",
             "Input hashes, rows, labels and OOF folds were verified; nested predictions and metrics were recomputed. All three candidate checkpoints reproduce OOF predictions with zero maximum difference. Training-row and label hashes match Phase 14. The initial 20% holdout is unused here but had been consulted earlier.", "",
             "## Pooled nested metrics", "",
             "| Model | F1 | Precision | Recall | AP | Log loss |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name, nested in (("Phase 14", bnest), ("Exact binning", cnest)):
        m = nested["pooled_metrics"]
        lines.append(f"| {name} | {m['f1']:.6f} | {m['precision']:.6f} | {m['recall']:.6f} | {m['average_precision']:.6f} | {m['log_loss']:.6f} |")
    lines += ["", f"Absolute F1 difference: **{deltas['f1']:+.6f}**. Favorable folds: **{sum(d > 0 for d in fold_deltas)}/3**.", "",
              "## Results by fold", "", "| Fold | F1 Phase 14 | Candidate F1 | Difference | Phase 14 threshold | Candidate threshold |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for number, (b, c, delta) in enumerate(zip(bnest["folds"], cnest["folds"], fold_deltas), 1):
        lines.append(f"| {number} | {b['outer_evaluation_metrics']['f1']:.6f} | {c['outer_evaluation_metrics']['f1']:.6f} | {delta:+.6f} | {b['inner_threshold']:.6f} | {c['inner_threshold']:.6f} |")
    lines += ["", "## Confusion matrices", "", "| Model | TP | FN | FP | TN |", "| --- | ---: | ---: | ---: | ---: |"]
    for name, nested in (("Phase 14", bnest), ("Exact binning", cnest)):
        c = nested["pooled_confusion_counts"]
        lines.append(f"| {name} | {c['true_positives']} | {c['false_negatives']} | {c['false_positives']} | {c['true_negatives']} |")
    interval = summary["paired_conditional_f1_delta_interval_95"]
    lines += ["", "## Decision changes", "",
              f"The candidate recovers {flips['recovered_false_negatives']} false negatives and loses {flips['lost_true_positives']} true positives. It adds {flips['added_false_positives']} new false positives and removes {flips['removed_false_positives']}.", "",
              f"Conditional paired-bootstrap 95% interval for the F1 difference: [{interval[0]:+.6f}, {interval[1]:+.6f}]. Uses 20,000 class-stratified resamples with seed 20260929 and fixed models and thresholds. It excludes training variability and repeated candidate selection; it is a diagnostic rather than independent confirmation.", "",
              "## Cost and environment", "",
              f"Completed CV runtime: {summary['runtime_seconds']:.1f} seconds ({summary['runtime_seconds']/60:.1f} minutes). Executed environment: Python {summary['environment']['python']}, NumPy {summary['environment']['numpy']}. Execution in the official Python 3.9 / NumPy 1.23.1 environment was not checked.", "",
              "The three outer fits use 250, 251 and 250 exact columns, including constants. Respectively 79, 82 and 79 columns recover distinctions; inner fits use 251 exact columns. The matrix remains uint8, while additional boundaries can increase split-search cost.", "",
              "## Decision", "",
              ("The candidate meets the plan's operational rule: higher pooled F1 and at least two favorable folds. It is recommended for follow-up, subject to official-environment verification and controlled evaluation of later transformations."
               if promote else "The candidate fails the plan's operational rule. Retain Phase 14 as the control; this comparison does not support adopting exact binning across the board."), "",
              f"The AP change is {deltas['average_precision']:+.6f} and the log-loss change is {deltas['log_loss']:+.6f}: both differences are very small. Probability correlation is {summary['probability_correlation']:.6f}. Even with exploratory threshold selection on the same OOF labels, candidate F1 is {record['outcome']['metrics']['f1']:.6f}, compared with {baseline['outcome']['metrics']['f1']:.6f}. These last scores are optimistic and are excluded from the decision.", "",
              "Category loss is real, but increasing resolution across all affected columns does not improve F1 in this trial. This neither establishes overfitting as the cause nor rules out benefits for a specific feature family. Follow-up should limit exact retention to binary and low-cardinality categorical columns, retain original numerical binning, and preserve both states of future one-hot and missing indicators. The conditional interval includes zero, so the small difference is not conclusive evidence against the approach in general.", "",
              "This study implements and evaluates the candidate while preserving the submission configuration. It trains no new full-data model and generates no submission.", "",
              "## Artifacts", "",
              f"- [Candidate record](../experiments/{published.name}).",
              "- [Full comparison](../experiments/phase20_binning_comparison.json).",
              "- [Preflight](phase20_binning_preflight.json).",
              "- [Initial audit](discrete_binning_audit.md).",
              "- [Configuration](../../configs/experiments/phase20_phase14_exact_low_cardinality.json)."]
    (root / "results/eda/phase20_binning_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"f1": cnest["pooled_metrics"]["f1"], "delta_f1": deltas["f1"],
                      "fold_deltas": fold_deltas, "meets_plan_rule": promote, "record": str(published)}, indent=2))


if __name__ == "__main__":
    main()
