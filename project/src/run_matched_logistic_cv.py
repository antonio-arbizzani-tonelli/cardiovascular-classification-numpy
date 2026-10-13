"""Evaluate logistic regression with the exact selected Phase 14 cleaning.

The models share source values and partitions. Logistic regression requires a
finite design: train-only fills/scales and missingness flags replace tree-native
NaN routing. This is shared semantic preprocessing, not an identical final matrix.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from src.evaluation import average_precision, best_f1_threshold, binary_log_loss, classification_metrics, labels_from_scores
from src.experiment_logger import save_experiment
from src.feature_preprocessing import load_feature_metadata, tree_feature_matrices
from src.numpy_logistic import fit_logistic
from src.run_preprocessing_cv import _as_binary_labels, _load_feature_names, _sha256, _sigmoid, _stratified_folds

ROOT = Path(__file__).resolve().parents[1]


def logistic_designs(train, validation, names, metadata, missing_indicators=True):
    """Fit finite adaptation only on the already Phase 14-cleaned training rows."""
    train, validation = np.asarray(train), np.asarray(validation)
    if (train.ndim != 2 or validation.ndim != 2 or train.shape[1] != validation.shape[1]
            or train.shape[1] != len(names) or not train.shape[0] or not validation.shape[0]):
        raise ValueError("Cleaned arrays must align with their source names.")
    if np.any(np.isinf(train)) or np.any(np.isinf(validation)):
        raise ValueError("Cleaned arrays must not contain infinity.")
    p = len(names)
    width = 1 + p * (2 if missing_indicators else 1)
    design_train = np.ones((len(train), width), dtype=np.float64)
    design_validation = np.ones((len(validation), width), dtype=np.float64)
    types = {entry['name']: entry['semantic_type'] for entry in metadata}
    fills, means, scales, flag_means, flag_scales = [], [], [], [], []
    for j, name in enumerate(names):
        values = train[:, j].astype(np.float64)
        missing = np.isnan(values)
        observed = values[~missing]
        if not len(observed):
            raise ValueError(f"{name} has no observed training values.")
        if types[name] in {'binary', 'categorical', 'ordinal'}:
            categories, counts = np.unique(observed, return_counts=True)
            fill = float(categories[np.argmax(counts)])
        else:
            fill = float(np.median(observed))
        values[missing] = fill
        mean, scale = float(np.mean(values)), float(np.std(values))
        scale = scale or 1.0
        design_train[:, j + 1] = (values - mean) / scale
        valid_values = validation[:, j].astype(np.float64)
        valid_missing = np.isnan(valid_values)
        valid_values[valid_missing] = fill
        design_validation[:, j + 1] = (valid_values - mean) / scale
        fills.append(fill); means.append(mean); scales.append(scale)
        if missing_indicators:
            flag_mean = float(np.mean(missing))
            flag_scale = float(np.sqrt(flag_mean * (1.0 - flag_mean))) or 1.0
            design_train[:, 1 + p + j] = (missing - flag_mean) / flag_scale
            design_validation[:, 1 + p + j] = (valid_missing - flag_mean) / flag_scale
            flag_means.append(flag_mean); flag_scales.append(flag_scale)
    state = {'fill_values': fills, 'means': means, 'scales': scales,
             'missing_means': flag_means, 'missing_scales': flag_scales}
    return design_train, design_validation, state


def metrics(labels, probabilities, predictions):
    counts, values = classification_metrics(labels, predictions)
    values.update(average_precision=average_precision(labels, probabilities),
                  log_loss=binary_log_loss(labels, probabilities))
    return values, vars(counts)


def verify_input_fingerprints(reference_record, fingerprints):
    """Require the recorded Phase 14 inputs before claiming matched cleaning."""
    expected = reference_record['outcome']['input_sha256']
    fields = {'features_sha256': 'features', 'labels_sha256': 'labels',
              'split_sha256': 'split_indices', 'metadata_sha256': 'feature_metadata',
              'preprocessing_sha256': 'preprocessing_config'}
    for current, historical in fields.items():
        if fingerprints[current] != expected[historical]:
            raise ValueError(f"Matched comparison input differs from Phase 14: {historical}")
    return {'passed': True, 'historical_input_hashes_verified': list(fields.values())}


def nested_cv(features, labels, development_indices, names, metadata, plan, suite, artifact_dir,
              fitter=fit_logistic):
    """Use the exact Phase 14 outer/inner row assignment and inner-F1 thresholds."""
    y = labels[development_indices]
    n = len(y)
    probability = np.full(n, np.nan)
    predicted = np.zeros(n, dtype=np.int8)
    thresholds = np.full(n, np.nan)
    fold_ids = np.zeros(n, dtype=np.int8)
    details, fit_details = [], []
    artifact_dir.mkdir(parents=True, exist_ok=True)

    def fit_pair(train_positions, valid_positions, tag):
        started = time.perf_counter()
        train, valid, clean_names = tree_feature_matrices(
            features[development_indices[train_positions]],
            features[development_indices[valid_positions]], names, metadata, plan)
        if len(clean_names) != suite['source_feature_count']:
            raise ValueError("Shared Phase 14 source-column count changed.")
        train_design, valid_design, state = logistic_designs(
            train, valid, clean_names, metadata, suite['logistic_adapter']['missing_indicators'])
        del train, valid
        fitted = fitter(train_design, y[train_positions], **suite['model'])
        if fitted['status'] != 'converged':
            raise RuntimeError(f"{tag}: logistic fit did not converge: {fitted['status']}, gradient={fitted['gradient_inf_norm']}")
        p = _sigmoid(valid_design @ fitted['weights'])
        elapsed = time.perf_counter() - started
        fit_detail = {key: value for key, value in fitted.items() if key != 'weights'}
        fit_detail.update(fit=tag, training_rows=len(train_positions), validation_rows=len(valid_positions),
                          source_features=len(clean_names), design_columns=train_design.shape[1], seconds=elapsed,
                          training_row_sha256=hashlib.sha256(development_indices[train_positions].tobytes()).hexdigest(),
                          validation_row_sha256=hashlib.sha256(development_indices[valid_positions].tobytes()).hexdigest())
        fit_details.append(fit_detail)
        np.savez_compressed(artifact_dir / (tag + '.npz'),
                            training_indices=development_indices[train_positions],
                            validation_indices=development_indices[valid_positions], probabilities=p,
                            weights=fitted['weights'], source_names=np.asarray(clean_names),
                            **{key: np.asarray(value) for key, value in state.items()})
        print(f"{tag}: {len(train_positions)} training rows, {fitted['iterations']} iterations, "
              f"gradient={fitted['gradient_inf_norm']:.2g}, {elapsed:.1f}s", flush=True)
        del train_design, valid_design
        gc.collect()
        return p

    for outer, (train_pos, valid_pos) in enumerate(
            _stratified_folds(y, suite['fold_count'], suite['outer_seed']), start=1):
        fold_ids[valid_pos] = outer
        probability[valid_pos] = fit_pair(train_pos, valid_pos, f'outer{outer}')
        inner_oof = np.full(len(train_pos), np.nan)
        for inner, (inner_train, inner_valid) in enumerate(_stratified_folds(
                y[train_pos], suite['inner_fold_count'], suite['inner_seed'] + outer), start=1):
            inner_oof[inner_valid] = fit_pair(train_pos[inner_train], train_pos[inner_valid],
                                            f'outer{outer}_inner{inner}')
        choice = best_f1_threshold(y[train_pos], inner_oof)
        thresholds[valid_pos] = choice.threshold
        predicted[valid_pos] = labels_from_scores(probability[valid_pos], choice.threshold)
        values, counts = metrics(y[valid_pos], probability[valid_pos], predicted[valid_pos])
        details.append({'fold': outer, 'inner_seed': suite['inner_seed'] + outer,
                        'threshold': choice.threshold, 'inner_f1': choice.f1,
                        'metrics': values, 'confusion_counts': counts})
        print(f"fold {outer}: threshold={choice.threshold:.6f}, F1={values['f1']:.6f}", flush=True)
    values, counts = metrics(y, probability, predicted)
    np.savez_compressed(artifact_dir / 'nested_oof.npz', development_indices=development_indices,
                        labels=y, fold_ids=fold_ids, probabilities=probability,
                        nested_predictions=predicted, nested_thresholds=thresholds)
    return {'metrics': values, 'confusion_counts': counts, 'folds': details, 'fits': fit_details}, predicted


def paired_comparison(labels, logistic_predictions, booster_predictions, resamples=20000, seed=20261013):
    """Class-stratified paired bootstrap using the four joint decisions per class."""
    rng = np.random.default_rng(seed)
    samples = []
    tables = []
    for actual in (0, 1):
        mask = labels == actual
        codes = 2 * booster_predictions[mask] + logistic_predictions[mask]
        counts = np.bincount(codes, minlength=4)
        tables.append(counts.tolist())
        samples.append(rng.multinomial(int(mask.sum()), counts / mask.sum(), size=resamples))
    neg, pos = samples
    booster_tp, logistic_tp = pos[:, 2] + pos[:, 3], pos[:, 1] + pos[:, 3]
    booster_fp, logistic_fp = neg[:, 2] + neg[:, 3], neg[:, 1] + neg[:, 3]
    positives = int(np.sum(labels))
    delta = 2 * booster_tp / (positives + booster_tp + booster_fp) - 2 * logistic_tp / (positives + logistic_tp + logistic_fp)
    return {'joint_decision_counts_by_actual_class': tables, 'bootstrap_resamples': resamples, 'seed': seed,
            'booster_minus_logistic_f1_interval_95': np.quantile(delta, [0.025, 0.975]).tolist(),
            'scope': 'Conditional on these fitted models, folds and selected thresholds. Does not include retraining or repeated model-selection uncertainty.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/experiments/phase38_phase14_logistic.json')
    parser.add_argument('--data-root', type=Path, default=ROOT)
    parser.add_argument('--reference-oof', type=Path,
                        help='Optional original Phase 14 OOF archive for paired error/interval analysis.')
    args = parser.parse_args()
    suite = json.loads(args.config.read_text(encoding='utf-8'))
    data = {key: args.data_root / value for key, value in suite['data'].items()}
    features = np.load(data['features_path'], mmap_mode='r')
    labels = _as_binary_labels(np.load(data['labels_path']))
    with np.load(data['split_indices_path']) as split:
        development_indices = split['development_indices'].astype(np.int64)
    names = _load_feature_names(data['x_train_csv_path'])
    metadata_path = ROOT / suite['feature_metadata_path']
    plan_path = ROOT / suite['preprocessing_config_path']
    metadata = load_feature_metadata(metadata_path)
    plan = json.loads(plan_path.read_text(encoding='utf-8'))['variants'][0]['preprocessing']
    booster_predictions = booster_probabilities = None
    booster_labels = labels[development_indices]
    if args.reference_oof is not None:
        if _sha256(args.reference_oof) != suite['reference_oof_sha256']:
            raise ValueError('The reference is not the recorded selected Phase 14 OOF archive.')
        with np.load(args.reference_oof) as reference:
            booster_indices = reference['development_indices'].copy()
            reference_labels = reference['labels'].copy()
            booster_fold_ids = reference['fold_ids'].copy()
            booster_predictions = reference['nested_predictions'].copy()
            booster_probabilities = reference['probabilities'].copy()
        if not np.array_equal(booster_indices, development_indices) or not np.array_equal(reference_labels, booster_labels):
            raise ValueError('Reference rows/labels do not match the development split.')
        expected_folds = np.zeros(len(development_indices), dtype=np.int8)
        for fold, (_, validation) in enumerate(_stratified_folds(booster_labels, suite['fold_count'], suite['outer_seed']), start=1):
            expected_folds[validation] = fold
        if not np.array_equal(booster_fold_ids, expected_folds):
            raise ValueError('Reference fold mapping differs from the matched protocol.')
    fingerprint = {'suite_sha256': _sha256(args.config), 'features_sha256': _sha256(data['features_path']),
                   'labels_sha256': _sha256(data['labels_path']), 'split_sha256': _sha256(data['split_indices_path']),
                   'metadata_sha256': _sha256(metadata_path), 'preprocessing_sha256': _sha256(plan_path),
                   'runner_sha256': _sha256(Path(__file__)), 'solver_sha256': _sha256(ROOT / 'src/numpy_logistic.py'),
                   'shared_cleaner_sha256': _sha256(ROOT / 'src/feature_preprocessing.py'),
                   'evaluation_sha256': _sha256(ROOT / 'src/evaluation.py'),
                   'fold_implementation_sha256': _sha256(ROOT / 'src/run_preprocessing_cv.py'),
                   'phase14_oof_sha256': suite['reference_oof_sha256'] if args.reference_oof else None}
    reference_record = json.loads((ROOT / suite['reference_record']).read_text(encoding='utf-8'))
    input_verification = verify_input_fingerprints(reference_record, fingerprint)
    started = time.perf_counter()
    artifact_dir = ROOT / suite['artifact_dir']
    outcome, predictions = nested_cv(features, labels, development_indices, names, metadata, plan, suite, artifact_dir)
    outcome['runtime_seconds'] = time.perf_counter() - started
    outcome['status'] = 'completed'
    outcome['input_and_source_fingerprints'] = fingerprint
    outcome['phase14_input_verification'] = input_verification
    outcome['oof_sha256'] = _sha256(artifact_dir / 'nested_oof.npz')
    if args.reference_oof is not None:
        reference_values, reference_counts = metrics(booster_labels, booster_probabilities, booster_predictions)
        outcome['comparison'] = paired_comparison(booster_labels, predictions, booster_predictions, **suite['bootstrap'])
    else:
        nested_reference = reference_record['outcome']['nested_threshold_evaluation']
        reference_values = nested_reference['pooled_metrics']
        reference_counts = nested_reference['pooled_confusion_counts']
        outcome['comparison'] = {'paired_interval_available': False,
                                 'scope': 'Point comparison with the included Phase 14 record; paired analysis requires the original verified OOF archive.'}
    outcome['phase14_reference'] = {'record': suite['reference_record'], 'metrics': reference_values, 'confusion_counts': reference_counts}
    outcome['comparison']['booster_minus_logistic_f1'] = reference_values['f1'] - outcome['metrics']['f1']
    config = {'experiment_name': suite['experiment_name'], 'hypothesis': suite['hypothesis'], 'data': suite['data'],
              'features': {'source_count': suite['source_feature_count'], 'preprocessing_source': suite['preprocessing_config_path'],
                           'shared_cleaning': 'Exact tree_feature_matrices Phase 14 transformation fitted separately within every training partition.',
                           'finite_logistic_adapter': suite['logistic_adapter']},
              'missing_values': {'fit_partition': 'corresponding training partition only',
                                 'method': 'Shared codebook NaNs followed by train-only fill, scaling and missing indicators for logistic regression; trees retain native NaN routing.'},
              'split': {'id': 'stratified_seed_20260918_development_inner_cv', 'outer_folds': suite['fold_count'],
                        'outer_seed': suite['outer_seed'], 'inner_folds': suite['inner_fold_count'], 'inner_seed': suite['inner_seed']},
              'model': {'name': 'numpy_regularized_logistic', 'parameters': suite['model']},
              'threshold': {'selection_method': 'F1-maximizing threshold on inner OOF scores, frozen for each outer evaluation fold'}}
    record_path = save_experiment(config, outcome, ROOT / suite['record_dir'])
    print(json.dumps({'record': str(record_path.relative_to(ROOT)), 'f1': outcome['metrics']['f1'], 'comparison': outcome['comparison']}, indent=2))


if __name__ == '__main__':
    main()
