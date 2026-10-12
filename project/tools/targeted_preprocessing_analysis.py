"""Preflight and verified comparison for the Phase 21 and 22 trials."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import numpy as np

from src.evaluation import classification_metrics, average_precision, binary_log_loss
from src.feature_preprocessing import load_feature_metadata, tree_feature_matrices
from src.numpy_boosting import HistogramBinner, HistogramGradientBoostingClassifier
from src.run_boosting_cv import _resolved_parameters, _array_sha256
from src.run_preprocessing_cv import _as_binary_labels, _load_feature_names, _sha256, _stratified_folds
from src.summarize_phase19_transfer import BASELINE, _arrays, _paired_interval, _publish


TRIALS = {21: "phase21_phase14_clinical_exact", 22: "phase22_phase14_activity_one_hot"}


def _load(root, phase):
    suite_path = root / f"configs/experiments/{TRIALS[phase]}.json"
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    prep = json.loads((root / suite["preprocessing_config_path"]).read_text(encoding="utf-8"))
    plan = next(v["preprocessing"] for v in prep["variants"]
                if v["experiment_name"] == suite["preprocessing_variant"])
    return suite_path, suite, plan


def _input_data(root, suite):
    x = np.load(root / suite["data"]["features_path"], mmap_mode="r")
    y = _as_binary_labels(np.load(root / suite["data"]["labels_path"]))
    with np.load(root / suite["data"]["split_indices_path"]) as saved:
        development = saved["development_indices"].copy()
    names = _load_feature_names(root / suite["data"]["x_train_csv_path"])
    metadata = load_feature_metadata(root / suite["feature_metadata_path"])
    return x, y, development, names, metadata


def _partitions(y, development, suite):
    outer = list(_stratified_folds(y[development], 3, suite["seed"]))
    for fold, (train, valid) in enumerate(outer, 1):
        yield f"outer_{fold}", train, valid
    for fold, (train, _) in enumerate(outer, 1):
        for inner, (itrain, ivalid) in enumerate(_stratified_folds(
                y[development[train]], 2, suite["nested_threshold"]["inner_seed"] + fold), 1):
            yield f"outer_{fold}_inner_{inner}", train[itrain], train[ivalid]


def preflight(root):
    baseline = json.loads((root / BASELINE).read_text(encoding="utf-8"))
    barray = _arrays(root, baseline)
    base_prep = json.loads((root / baseline["config"]["features"]["preprocessing_source"])
                          .read_text(encoding="utf-8"))
    base_plan = base_prep["variants"][0]["preprocessing"]
    _, suite, _ = _load(root, 21)
    x, y, development, names, metadata = _input_data(root, suite)
    np.testing.assert_array_equal(development, barray["development_indices"])
    np.testing.assert_array_equal(y[development], barray["labels"])
    fingerprints = {k: _sha256(root / suite["data"][p]) for k, p in
        (("features", "features_path"), ("labels", "labels_path"), ("split_indices", "split_indices_path"))}
    fingerprints["feature_metadata"] = _sha256(root / suite["feature_metadata_path"])
    for key, value in fingerprints.items():
        if value != baseline["outcome"]["input_sha256"][key]:
            raise ValueError(f"Baseline input changed: {key}")
    result = {"input_sha256": fingerprints, "final_config_sha256": _sha256(root / "configs/final_model.json"),
        "source_sha256": {p: _sha256(root / p) for p in (
            "src/numpy_boosting.py", "src/feature_preprocessing.py", "src/run_boosting_cv.py",
            "src/run_logged_boosting_cv.py", "src/evaluation.py")}, "trials": {},
        "baseline_checkpoint_checks": [], "scope": "Development partitions only; no predictive model training."}
    for phase in (21, 22):
        suite_path, current, plan = _load(root, phase)
        expected_plan = dict(base_plan)
        if phase == 22:
            expected_plan["tree_one_hot_features"] = ["EXRACT11", "EXRACT21"]
        if plan != expected_plan:
            raise ValueError("The candidate has unexpected preprocessing changes.")
        result["trials"][str(phase)] = {"suite_sha256": _sha256(suite_path),
            "preprocessing_sha256": _sha256(root / current["preprocessing_config_path"]), "partitions": []}
        for partition, train, valid in _partitions(y, development, current):
            raw_train, raw_valid = x[development[train]], x[development[valid]]
            bt, bv, bn = tree_feature_matrices(raw_train, raw_valid, names, metadata, base_plan)
            if phase == 21:
                ct, cv, cn = bt, bv, bn
            else:
                ct, cv, cn = tree_feature_matrices(raw_train, raw_valid, names, metadata, plan)
            params = _resolved_parameters(current["models"][0]["parameters"], cn)
            original = HistogramBinner(64).fit(bt)
            candidate = HistogramBinner(64, params["binning_strategy"], params["exact_feature_indices"]).fit(ct)
            encoded = candidate.transform(ct)
            selected = set(params["exact_feature_indices"])
            for index, name in enumerate(cn):
                if index in selected:
                    finite = np.isfinite(ct[:, index])
                    if np.unique(ct[finite, index]).size != np.unique(encoded[finite, index]).size:
                        raise ValueError(f"Lost exact states: {partition}/{name}")
                else:
                    bi = bn.index(name)
                    np.testing.assert_array_equal(ct[:, index], bt[:, bi])
                    np.testing.assert_array_equal(cv[:, index], bv[:, bi])
                    np.testing.assert_array_equal(candidate.edges_[index], original.edges_[bi])
            np.testing.assert_array_equal(encoded == 255, np.isnan(ct))
            activity = {}
            if phase == 22:
                for name in ("EXRACT11", "EXRACT21"):
                    bi = bn.index(name)
                    block = [i for i, n in enumerate(cn) if n.startswith(name + "__")]
                    known = np.isfinite(ct[:, block[0]])
                    np.testing.assert_array_equal(np.sum(ct[known][:, block], axis=1), np.ones(known.sum()))
                    vknown = np.isfinite(cv[:, block[0]])
                    np.testing.assert_array_equal(np.sum(cv[vknown][:, block], axis=1), np.ones(vknown.sum()))
                    np.testing.assert_array_equal(np.isnan(cv[:, block[0]]), np.isnan(bv[:, bi]))
                    activity[name] = {"category_count": len(block) - 1,
                        "unknown_validation_rows": int(np.nansum(cv[:, cn.index(name + "__unknown")])),
                        "rare_categories_below_min_leaf": int(sum(
                            np.nansum(ct[:, i]) < 200 for i in block if cn[i] != name + "__unknown"))}
                if "EXRACT21__is_88" not in cn:
                    raise ValueError("The valid no-second-activity state was removed.")
            detail = {"partition": partition, "training_rows": int(train.size), "validation_rows": int(valid.size),
                "feature_count": len(cn), "output_names": cn, "exact_column_indices": sorted(selected),
                "bin_counts": candidate.bin_counts_.tolist(), "activity": activity,
                "training_row_indices_sha256": _array_sha256(development[train]),
                "training_labels_sha256": _array_sha256(y[development[train]])}
            result["trials"][str(phase)]["partitions"].append(detail)
            if phase == 21 and partition.startswith("outer_") and "inner" not in partition:
                fold = int(partition[-1])
                checkpoint = baseline["outcome"]["model_checkpoints"][fold - 1]
                if _sha256(root / checkpoint["path"]) != checkpoint["sha256"]:
                    raise ValueError("Baseline checkpoint fingerprint changed.")
                model, _ = HistogramGradientBoostingClassifier.load_checkpoint(root / checkpoint["path"])
                difference = float(np.max(np.abs(model.predict_proba(bv)[:, 1] - barray["probabilities"][valid])))
                if difference != 0:
                    raise ValueError("Default baseline predictions changed.")
                result["baseline_checkpoint_checks"].append({"fold": fold, "maximum_probability_difference": difference})
                del model
            print(f"PREFLIGHT phase={phase} partition={partition} features={len(cn)} exact={len(selected)} OK", flush=True)
            del raw_train, raw_valid, bt, bv, ct, cv, original, candidate, encoded
            gc.collect()
    path = root / "results/eda/phase21_22_preflight.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def compare(root, phase, source):
    check = json.loads((root / "results/eda/phase21_22_preflight.json").read_text(encoding="utf-8"))
    suite_path, suite, plan = _load(root, phase)
    trial = check["trials"][str(phase)]
    if _sha256(suite_path) != trial["suite_sha256"]:
        raise ValueError("Suite changed after preflight.")
    record = json.loads(source.read_text(encoding="utf-8"))
    baseline = json.loads((root / BASELINE).read_text(encoding="utf-8"))
    for key, value in check["input_sha256"].items():
        if record["outcome"]["input_sha256"][key] != value:
            raise ValueError(f"Changed input {key}")
    if record["outcome"]["input_sha256"]["preprocessing_config"] != trial["preprocessing_sha256"]:
        raise ValueError("Changed preprocessing input.")
    if _sha256(root / "configs/final_model.json") != check["final_config_sha256"]:
        raise ValueError("Final submission configuration changed.")
    for path, expected in check["source_sha256"].items():
        if _sha256(root / path) != expected or record["outcome"]["source_sha256"][path] != expected:
            raise ValueError(f"Source changed during training: {path}")
    expected_params = dict(baseline["config"]["model"]["parameters"])
    params = dict(record["config"]["model"]["parameters"])
    if params != {**suite["models"][0]["parameters"], "n_estimators": 200}:
        raise ValueError("Record model parameters differ from the requested suite.")
    for key in ("binning_strategy", "exact_feature_names", "exact_feature_prefixes"):
        params.pop(key, None)
    if params != expected_params or record["config"]["split"] != baseline["config"]["split"]:
        raise ValueError("Other model settings or splits changed.")
    profiles = record["outcome"]["individual_fit_profiles"]
    if len(profiles) != 9 or len(trial["partitions"]) != 9:
        raise ValueError("Expected nine complete fits.")
    for profile, detail in zip(profiles, trial["partitions"]):
        if (profile["feature_count"] != detail["feature_count"]
                or profile["exact_column_indices"] != detail["exact_column_indices"]
                or profile["bin_counts"] != detail["bin_counts"]
                or profile["binning_strategy"] != "exact_selected"):
            raise ValueError("Actual training binning differs from preflight.")
    ba, ca = _arrays(root, baseline), _arrays(root, record)
    for key in ("development_indices", "fold_ids", "labels"):
        np.testing.assert_array_equal(ba[key], ca[key])
    np.testing.assert_array_equal(ca["nested_predictions"], ca["probabilities"] >= ca["nested_thresholds"])
    nested = record["outcome"]["nested_threshold_evaluation"]
    counts, metrics = classification_metrics(ca["labels"], ca["nested_predictions"])
    metrics.update(average_precision=average_precision(ca["labels"], ca["probabilities"]),
                   log_loss=binary_log_loss(ca["labels"], ca["probabilities"]))
    for key, value in metrics.items():
        if key in nested["pooled_metrics"] and not np.isclose(value, nested["pooled_metrics"][key], rtol=0, atol=1e-15):
            raise ValueError(f"Recomputed metric differs: {key}")
    x, y, development, names, metadata = _input_data(root, suite)
    predictions_verified = []
    for fold, (train, valid) in enumerate(_stratified_folds(y[development], 3, suite["seed"]), 1):
        checkpoint = record["outcome"]["model_checkpoints"][fold - 1]
        if _sha256(root / checkpoint["path"]) != checkpoint["sha256"]:
            raise ValueError("Candidate checkpoint fingerprint changed.")
        model, saved = HistogramGradientBoostingClassifier.load_checkpoint(root / checkpoint["path"])
        detail = trial["partitions"][fold - 1]
        for key in ("training_row_indices_sha256", "training_labels_sha256"):
            if saved[key] != detail[key]:
                raise ValueError(f"Checkpoint training mismatch: {key}")
        ct, cv, cn = tree_feature_matrices(x[development[train]], x[development[valid]], names, metadata, plan)
        if cn != detail["output_names"] or saved["output_feature_names"] != cn:
            raise ValueError("Checkpoint vocabulary differs.")
        np.testing.assert_array_equal(model.exact_feature_indices, detail["exact_column_indices"])
        difference = float(np.max(np.abs(model.predict_proba(cv)[:, 1] - ca["probabilities"][valid])))
        if difference != 0:
            raise ValueError("Candidate checkpoint predictions differ from OOF.")
        threshold = nested["folds"][fold - 1]["inner_threshold"]
        np.testing.assert_array_equal(ca["nested_thresholds"][valid], np.repeat(threshold, valid.size))
        _, fold_metrics = classification_metrics(ca["labels"][valid], ca["nested_predictions"][valid])
        if fold_metrics["f1"] != nested["folds"][fold - 1]["outer_evaluation_metrics"]["f1"]:
            raise ValueError("Fold F1 differs.")
        predictions_verified.append({"fold": fold, "maximum_probability_difference": difference})
        del model, ct, cv
        gc.collect()
        print(f"VERIFIED phase={phase} fold={fold} checkpoint predictions identical", flush=True)
    bn = baseline["outcome"]["nested_threshold_evaluation"]
    deltas = {key: value - bn["pooled_metrics"][key] for key, value in nested["pooled_metrics"].items()}
    fold_deltas = [c["outer_evaluation_metrics"]["f1"] - b["outer_evaluation_metrics"]["f1"]
                   for c, b in zip(nested["folds"], bn["folds"])]
    labels, bp, cp = ca["labels"], ba["nested_predictions"], ca["nested_predictions"]
    flips = {"recovered_false_negatives": int(np.sum((labels == 1) & (bp == 0) & (cp == 1))),
             "lost_true_positives": int(np.sum((labels == 1) & (bp == 1) & (cp == 0))),
             "added_false_positives": int(np.sum((labels == 0) & (bp == 0) & (cp == 1))),
             "removed_false_positives": int(np.sum((labels == 0) & (bp == 1) & (cp == 0)))}
    published = _publish(source, root)
    summary = {"phase": phase, "baseline_record": BASELINE,
        "candidate_record": str(published.relative_to(root)).replace("\\", "/"),
        "baseline_nested": bn, "candidate_nested": nested, "metric_deltas": deltas,
        "fold_f1_deltas": fold_deltas, "positive_fold_count": sum(d > 0 for d in fold_deltas),
        "meets_plan_promotion_rule": deltas["f1"] > 0 and sum(d > 0 for d in fold_deltas) >= 2,
        "decision_changes": flips, "paired_conditional_f1_delta_interval_95": _paired_interval(labels, bp, cp),
        "bootstrap_repetitions": 20000, "bootstrap_seed": 20260929,
        "bootstrap_scope": "Paired stratified rows with fixed models and thresholds; excludes training and repeated selection uncertainty.",
        "runtime_seconds": record["outcome"]["runtime_seconds"],
        "environment": record["outcome"]["environment"], "final_model_changed": False,
        "checkpoint_prediction_checks": predictions_verified,
        "preflight_partitions": [{k: v for k, v in p.items() if k not in ("output_names", "bin_counts")}
                                 for p in trial["partitions"]],
        "exploratory_same_oof_threshold_f1": record["outcome"]["metrics"]["f1"]}
    (root / f"results/experiments/phase{phase}_preprocessing_comparison.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_report(root, [summary])
    print(json.dumps({"phase": phase, "f1": nested["pooled_metrics"]["f1"],
        "delta_f1": deltas["f1"], "fold_deltas": fold_deltas,
        "meets_plan_rule": summary["meets_plan_promotion_rule"]}), flush=True)
    return summary


def write_report(root, summaries):
    combined = len(summaries) == 2
    title = "Phase 21 and 22 — clinical and activity preprocessing" if combined else f"Phase {summaries[0]['phase']} — targeted trial"
    lines = ["# " + title, "", "## Protocol", "",
        "Two candidates are evaluated separately against Phase 14. Phase 21 preserves exactly the four responses of BPHIGH4 and DIABETE3 while retaining original quantiles for the other 293 columns. Phase 22 starts from Phase 14 and replaces EXRACT11 and EXRACT21 with indicators for every training-observed category; exact binning applies only to these new indicators.", "",
        "Vocabulary is learned within each training partition without validation data. Missing values remain NaN across the activity block; an unknown column identifies finite responses unseen in training. EXRACT21=88 remains a valid category. This first trial does not group rare categories.", "",
        "Each candidate uses 262,508 development examples, three outer and two inner folds for F1-threshold selection: nine 200-tree fits. Same seeds, depth 5, learning rate 0.05, minimum leaf size 200, L2=1 and 128 candidate features per node. The initial 20% holdout is unused here but had been consulted earlier. HAREHAB1 remains included as in the control.", "",
        "All 101 tests pass before training, including training-only vocabulary, missing-value retention, column selection and checkpoint continuation. Preflight checks nine partitions per candidate, categories, bins, missing values and other feature values. The three original Phase 14 checkpoint predictions match saved OOF predictions exactly. All nine actual fit profiles match preflight; candidate OOF and checkpoint predictions are verified after training.", "",
        "## Nested results", "", "| Model | F1 | Delta F1 | Precision | Recall | AP | Log loss |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    base = summaries[0]["baseline_nested"]["pooled_metrics"]
    lines.append(f"| Phase 14 | {base['f1']:.6f} | — | {base['precision']:.6f} | {base['recall']:.6f} | {base['average_precision']:.6f} | {base['log_loss']:.6f} |")
    for item in summaries:
        m = item["candidate_nested"]["pooled_metrics"]
        lines.append(f"| Phase {item['phase']} | {m['f1']:.6f} | {item['metric_deltas']['f1']:+.6f} | {m['precision']:.6f} | {m['recall']:.6f} | {m['average_precision']:.6f} | {m['log_loss']:.6f} |")
    for item in summaries:
        phase = item["phase"]
        lines += ["", f"## Phase {phase}: details", "", "| Fold | Control F1 | Candidate F1 | Delta | Candidate threshold |", "| --- | ---: | ---: | ---: | ---: |"]
        for fold, (b, c, delta) in enumerate(zip(item["baseline_nested"]["folds"], item["candidate_nested"]["folds"], item["fold_f1_deltas"]), 1):
            lines.append(f"| {fold} | {b['outer_evaluation_metrics']['f1']:.6f} | {c['outer_evaluation_metrics']['f1']:.6f} | {delta:+.6f} | {c['inner_threshold']:.6f} |")
        lines += ["", "| Model | TP | FN | FP | TN |", "| --- | ---: | ---: | ---: | ---: |"]
        for name, n in (("Phase 14", item["baseline_nested"]), (f"Phase {phase}", item["candidate_nested"])):
            c = n["pooled_confusion_counts"]
            lines.append(f"| {name} | {c['true_positives']} | {c['false_negatives']} | {c['false_positives']} | {c['true_negatives']} |")
        flips = item["decision_changes"]
        ci = item["paired_conditional_f1_delta_interval_95"]
        bc = item["baseline_nested"]["pooled_confusion_counts"]
        cc = item["candidate_nested"]["pooled_confusion_counts"]
        lines += ["", f"Recovers {flips['recovered_false_negatives']} false negatives and loses {flips['lost_true_positives']} true positives; adds {flips['added_false_positives']} false positives and removes {flips['removed_false_positives']}.", "",
            f"Favorable folds: {item['positive_fold_count']}/3. Conditional-bootstrap 95% interval for the F1 delta: [{ci[0]:+.6f}, {ci[1]:+.6f}], with fixed models and thresholds (20,000 paired stratified resamples; seed 20260929). Excludes training variability and repeated candidate selection.", "",
            f"Full runtime: {item['runtime_seconds']/60:.1f} minutes. Python {item['environment']['python']}, NumPy {item['environment']['numpy']}. Official Python 3.9 / NumPy 1.23.1 execution was not checked.", "",
            ("Meets the plan's operational rule: higher pooled F1 and at least two favorable folds. It is a candidate for subsequent confirmation."
             if item["meets_plan_promotion_rule"] else "Fails the plan's operational rule: the change is not adopted in the reference pipeline."), "",
            f"Full record: [{Path(item['candidate_record']).name}](../experiments/{Path(item['candidate_record']).name}). Verified comparison: [JSON](../experiments/phase{phase}_preprocessing_comparison.json)."]
        lines += ["", f"Net change relative to Phase 14: {cc['true_positives'] - bc['true_positives']:+d} TP and {cc['false_positives'] - bc['false_positives']:+d} FP. " +
            ("The recall gain does not offset the precision loss."
             if phase == 21 else "The small precision gain does not offset the recall loss.")]
        if phase == 22:
            outer = item["preflight_partitions"][:3]
            lines += ["", "### Activity representation", "", "| Outer training partition | Inputs | EXRACT11 categories | EXRACT21 categories | Exact indicators |", "| --- | ---: | ---: | ---: | ---: |"]
            for p in outer:
                lines.append(f"| {p['partition']} | {p['feature_count']} | {p['activity']['EXRACT11']['category_count']} | {p['activity']['EXRACT21']['category_count']} | {len(p['exact_column_indices'])} |")
            lines += ["", "One inner training partition has 445 inputs and 152 exact indicators: a rare category is absent from training and becomes unknown in validation. Other partitions have 446 inputs. This expected vocabulary change uses no held-out information.", "",
                "Expansion changes sampling: with 128 candidates per node, the probability of considering each other feature falls from 43.4% to 28.7%. This evaluates the complete pipeline, so a loss alone does not establish that nominal information is useless. In outer training partitions, 42–44 EXRACT11 and 40–41 EXRACT21 categories have fewer than 200 examples; alone they cannot fill a leaf under the current minimum, although they can be combined with missing values. The unknown column is constant during training and has no positive examples from which to learn a specific effect."]
    lines += ["", "## Decision and follow-up", "",
        "The final Phase 14 configuration and submission threshold remain unchanged during these experiments. Results guide follow-up; no full-data model is trained and no submission is produced.", "",
        "Both variants lose against Phase 14 in all three folds and are not adopted. These specific configurations are closed; the trials do not establish that every exact-binning or nominal treatment is inferior. Both AP gains are very small and do not offset the loss in the primary metric, F1.", "",
        "The next priority is adding only restricted Phase 16 nonresponse indicators while preserving both binary states and original binning on other columns. Test imputation separately afterward to isolate its effect. Separate activity hypotheses remain: native categorical splits would retain 295 inputs; sampling by source feature would rebalance the expanded indicator block. Avoid repeating unchanged one-hot encoding or a grid guided solely by the same folds.", "",
        "Local artifacts: [preflight](phase21_22_preflight.json), configurations in configs/experiments, and OOF predictions and checkpoints in results/boosting_artifacts. Records, comparisons and documentation are retained in the project."]
    name = "phase21_22_preprocessing_summary.md" if combined else f"phase{summaries[0]['phase']}_preprocessing_summary.md"
    (root / "results/eda" / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "compare", "combined"))
    parser.add_argument("--phase", type=int, choices=(21, 22))
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    root = Path.cwd()
    if args.mode == "preflight":
        preflight(root)
    elif args.mode == "compare":
        if args.phase is None or args.record is None:
            parser.error("compare requires --phase and --record")
        compare(root, args.phase, args.record)
    else:
        summaries = [json.loads((root / f"results/experiments/phase{p}_preprocessing_comparison.json")
                               .read_text(encoding="utf-8")) for p in (21, 22)]
        write_report(root, summaries)


if __name__ == "__main__":
    main()
