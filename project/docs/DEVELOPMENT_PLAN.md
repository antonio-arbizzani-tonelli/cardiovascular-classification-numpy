# Final model and completed studies

The recorded model-development sequence is **complete**. This repository preserves the experiments of the EPFL Machine Learning CS-433 project without starting new training. The selected model is historical Phase 14, chosen after submitting both versions to AIcrowd, with author-reported **F1 0.452 and accuracy 0.878**. Phase 34 corrects the observed-versus-missing split search and remains a documented comparison. [EXPERIMENTS.md](EXPERIMENTS.md) records the study history; the [technical results](FINAL_REPORT.md) explain the choice.

## Frozen configuration

| Component | Selected value |
| --- | --- |
| Model | Histogram gradient boosting implemented in NumPy |
| Split search | Included historical Phase 14 source, verified by SHA-256 |
| Input | 295 Phase 14 features, including HAREHAB1 and ALCDAY5 |
| Preprocessing | Documented nonresponses → NaN; documented zero quantities → 0; quantile bins fitted on training rows |
| Parameters | 200 trees, depth 5, learning rate 0.05, minimum leaf size 200, 64 bins, 128 candidate features per node |
| Regularization / weighting | Leaf L2 1; positive-class weight 1 |
| Model seed | 20260920 |
| Nested development F1 | 0.442155227 |
| Precision / recall | 0.367632 / 0.554573 |
| Final threshold | 0.2106169795070252, maximizing F1 on three-fold OOF predictions over all training rows |
| AIcrowd feedback | F1 0.452, accuracy 0.878; author-reported |

The [final configuration](../configs/final_model.json) and [preprocessing plan](../configs/experiments/phase14_codebook_corrections_only.json) define the `run.py` pipeline. The new full-data Phase 14 fit uses 328,135 labeled rows and produces 109,379 test predictions, including 14,746 positives. The [final record](../results/eda/final_phase14_submission.json) retains calibration details and the selected submission fingerprint.

HAREHAB1 remains included. It asks about rehabilitation after a heart attack, so response eligibility can reveal information about the outcome. Removing it alone reduced historical F1 to 0.431039. This limits interpretation as prediction before an event.

## Completed studies

| Study family | Main result | Evidence |
| --- | --- | --- |
| Linear models and representations | Historical nested logistic F1 0.425628; best ridge 0.419508 | [Phase 7](../results/eda/phase7_nested_and_ridge_summary.md) |
| Booster grid and semantic corrections | Selected 200 trees/depth 5; Phase 14 improves 0.441741 to 0.442155 | [Phase 14](../results/eda/phase14_codebook_corrections_summary.md) |
| HAREHAB1 ablation | 0.431039, delta −0.011116; feature retained | [Phase 15 record](../results/experiments/20260921T154905753681Z_phase15-boosting-ablate-harehab1-depth5-features128-200trees.json) |
| Frequencies, activities and ALCDAY5 | Best family candidate 0.441862; none adopted | [History](EXPERIMENTS.md#completed-comparisons-against-phase-14) |
| General and clinical binning | 0.440783 and 0.439731; Phase 14 quantiles retained | [Phase 20](../results/eda/phase20_binning_summary.md), [Phase 21–22](../results/eda/phase21_22_preprocessing_summary.md) |
| Indicators and imputation | Indicators 0.440322; restricted-imputation nested confirmation 0.441791 | [Phase 23](../results/eda/phase23_missing_reason_flags_summary.md), [Phase 24](../results/eda/phase24_original_restricted_imputation_summary.md) |
| Parameters, depth and positive weighting | Best family candidate 0.441393; Phase 14 configuration retained | [History](EXPERIMENTS.md#completed-comparisons-against-phase-14) |
| Second seed and averaging | 0.439924 and 0.441111; both lower in all three folds | [Phase 26](../results/eda/phase26_two_seeds_summary.md) |
| Selection of 100/60 features | 0.439224 and 0.437584; both lower in all three folds | [Phase 29](../results/eda/phase29_feature_selection_summary.md) |
| MLP with dedicated preprocessing | 64 → 32: 0.424451; 128 → 64: 0.419268; both lower in all three folds | [Phase 32](../results/eda/phase32_mlp_summary.md) |
| Raw preprocessing | 321 raw inputs: 0.441457 versus cleaned control 0.442155 under the same earlier implementation | [Phase 33](../results/eda/phase33_raw_preprocessing_summary.md) |
| Observed-versus-missing correction | F1 0.440803, delta −0.001352; +206 true positives and +907 false positives versus Phase 14 | [Phase 34](../results/eda/phase34_missing_only_split_summary.md) |

All F1 values above use nested threshold selection. Comparisons through Phase 33 use the booster before the split correction; comparing Phase 33 raw inputs directly with Phase 34 would also change the implementation. Grouped families report their best measured candidate, rather than a common result for every variant.

The conditional paired interval for the Phase 34 F1 delta is [−0.003005, +0.000319] and includes zero. It holds models and thresholds fixed and excludes retraining and repeated-selection uncertainty. The final choice retained Phase 14 after AIcrowd feedback, with the same model parameters.

Phase 16 imputation screening reached exploratory F1 0.442674 by selecting and evaluating a threshold on the same OOF labels. Phase 24 confirmation with inner thresholds did not reproduce that advantage. Interactions listed in the Phase 16 tree configuration were not applied by tree preprocessing, so that result does not measure their effect. Historical linear results precede the correction from median to mode for categorical fills.

## Deferred ideas

These remain hypotheses for a future study; no training queue is active:

- Combine restricted imputation with binning that preserves every indicator state.
- Test exercise-frequency or activity representations beyond the measured variants.
- Implement explicit tree-path interactions or a booster–logistic ensemble, selecting all choices within inner training folds.

The completed studies retain 114 records across five experiment ledgers. Future studies would be separate NumPy and standard-library comparisons. Development folds have supported many choices, and early baselines consulted the original 20% validation partition; current results are development evidence after selection.
