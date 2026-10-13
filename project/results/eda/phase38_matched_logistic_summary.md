# Phase 38 — matched logistic comparison with selected Phase 14

The selected historical Phase 14 booster reaches nested F1 **0.442155227**, compared with **0.434466576** for a new logistic pipeline using the same 295 source columns, exact codebook cleaning and development partitions. The booster gains **0.007688651 absolute F1** and improves every outer fold.

## Shared inputs and model-specific representation

Both pipelines use the same 262,508 development rows, 23,180 positives, initial split seed 20260918 and outer seed 20260919. In each of three outer folds, two inner folds use seed 20260922 plus the outer-fold number to select the F1 threshold. That threshold is frozen before outer evaluation. Cleaning, fill values and scaling are fitted within each training partition; no outer-fold hyperparameter tuning is performed.

Both use exact Phase 14 `tree_feature_matrices` cleaning, including `HAREHAB1`. Trees retain native NaN routing. Logistic regression converts the same cleaned sources into a finite design: training mode for binary/categorical/ordinal fields, training median for numerical fields, training z-scores, and one standardized missingness flag for each source. The design has **295 values + 295 flags + one intercept = 591 columns**, with no one-hot encoding or interactions. The shared semantic cleaning does not make the final model matrices identical.

The NumPy L-BFGS solver minimizes mean binary cross-entropy plus `0.5 × 1e-4 × sum(weights[1:]²)`; the intercept is unpenalized. L2 **1e-4**, maximum 500 updates, history size 10 and gradient tolerance **1e-6** were fixed before the outer results. All nine fits converged in 446–484 updates. Total recorded runtime is 404.6 seconds (6.74 minutes), including preparation and all nine fits; no controlled speed comparison with historical boosting is inferred.

## Nested development results

| Metric | Matched logistic | Selected Phase 14 | Booster − logistic |
| --- | ---: | ---: | ---: |
| f1 | 0.434466576 | 0.442155227 | +0.007688651 |
| precision | 0.367541267 | 0.367632339 | +0.000091072 |
| recall | 0.531190682 | 0.554572908 | +0.023382226 |
| accuracy | 0.877889436 | 0.876434242 | -0.001455194 |
| specificity | 0.911468779 | 0.907607969 | -0.003860810 |
| balanced_accuracy | 0.721329730 | 0.731090438 | +0.009760708 |
| average_precision | 0.420989720 | 0.428609250 | +0.007619531 |
| log_loss | 0.218146955 | 0.215225071 | -0.002921884 |

| Fold | Logistic F1 | Phase 14 F1 | Booster − logistic | Logistic inner threshold | Phase 14 inner threshold |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.434665562 | 0.439026847 | +0.004361285 | 0.199915926 | 0.203056689 |
| 2 | 0.433677959 | 0.444053521 | +0.010375562 | 0.217498790 | 0.220104637 |
| 3 | 0.435013816 | 0.443511646 | +0.008497830 | 0.202263922 | 0.209445973 |

| Outcome | Matched logistic | Phase 14 | Booster − logistic |
| --- | ---: | ---: | ---: |
| true_positives | 12,313 | 12,855 | +542 |
| false_negatives | 10,867 | 10,325 | -542 |
| false_positives | 21,188 | 22,112 | +924 |
| true_negatives | 218,140 | 217,216 | -924 |

Relative to logistic regression, Phase 14 recovers **542 additional positives** and produces **924 additional false positives**. Its precision is almost unchanged while recall increases by 0.023382. Among individual decision changes, it recovers 1,343 positives missed by logistic regression and loses 801 positives found by logistic regression; it introduces 4,144 false positives and removes 3,220. Both miss 9,524 positives. These tradeoffs raise F1; logistic regression has higher accuracy/specificity at its selected threshold.

The class-stratified paired bootstrap gives a conditional 95% interval for booster-minus-logistic F1 of **[+0.004918584, +0.010463250]**, from 20,000 resamples with seed 20261013. It holds fitted models, folds and thresholds fixed and excludes retraining and repeated model-selection uncertainty. Development folds have already supported many choices; this comparison is not an untouched final test. `HAREHAB1` remains post-event target-linked information, so the task is reported-disease classification rather than prospective prediction.

The earlier historical logistic F1 0.425628 used a different solver, regularization, fill policy, missingness representation and age interactions. Its difference from this new result is a combined pipeline change; it does not isolate a cleaning uplift. The present comparison measures these two complete model pipelines under shared semantic preprocessing. It does not establish that every nonlinear model will outperform every logistic configuration.

The booster reference preserves the selected historical split search, including its documented omission of some observed-versus-missing boundary candidates. Corrected Phase 34 is a separate comparison.

## Verification and reproduction

The [experiment record](../experiments/phase38_matched_logistic/20261013T010425774510Z_phase38-phase14-shared-cleaning-logistic.json) retains exact metrics, row hashes, fit convergence, source fingerprints and paired decisions. The executed runner, solver and configuration match committed protocol **`3c00bd3`**. The current runner adds input-fingerprint guards and an optional reference-archive interface; its numerical adaptation, fitting, metrics and paired-bootstrap functions are unchanged. The [replay verification](phase38_matched_logistic_verification.json) checks official-cache/configuration hashes, selected Phase 14 source/reference hashes, all nine fit/evaluation boundaries, training-only adapter states, saved-weight probability/BCE/objective/gradient replay, inner threshold reconstruction and pooled metrics. No model was retrained during verification.

With official local data and prepared caches, run the [configured pipeline](../../configs/experiments/phase38_phase14_logistic.json) from the project root:

```bash
python -m src.run_matched_logistic_cv
```

The default reproduces logistic metrics and the point comparison against the [included historical Phase 14 record](../experiments/20260921T105139261213Z_phase14-boosting-codebook-corrections-only-depth5-features128-200trees.json). Add `--reference-oof` followed by the path to the original verified Phase 14 development OOF archive to reproduce paired error transitions and the conditional confidence interval. The [runner](../../src/run_matched_logistic_cv.py) verifies its hash, rows, labels and folds before using it. Fit states/weights and nested OOF predictions remain local, ignored artifacts under `results/oof_predictions/phase38_phase14_logistic/`. Full-train calibration probabilities are separate from this development evaluation.
