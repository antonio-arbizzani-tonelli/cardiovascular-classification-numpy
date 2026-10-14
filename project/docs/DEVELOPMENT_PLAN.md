# Selected model and completed studies

The completed release selects **Combined Phase 18 + Phase 24 (L2=1)**,
with author-reported **AIcrowd F1 0.455 / accuracy 0.882** and reported
**rank 3 on 14 October 2026**. It combines the diet representation and
restricted conditional imputation using the historical Phase 14 booster.
The [final configuration](../configs/final_model.json) uses 297 transformed
features, 200 trees, depth 5, learning rate 0.05, minimum leaf 200,
64 bins, 128 candidate features per node, leaf L2 1, seed 20260920,
and threshold **0.21811010373987366**. Calibration covers every labeled row.

The combined pipeline has no completed nested-development estimate.
The historical Phase 14 reference is retained through
[historical_phase14_model.json](../configs/historical_phase14_model.json).
`HAREHAB1` remains in the selected pipeline and limits prospective interpretation.

## Completed studies

| Study family | Main result | Evidence |
| --- | --- | --- |
| Linear models and representations | Historical nested logistic F1 0.425628; best ridge 0.419508 | [Phase 7](../results/eda/phase7_nested_and_ridge_summary.md) |
| Booster grid and semantic corrections | Selected 200 trees/depth 5; Phase 14 improves 0.441741 to 0.442155 | [Phase 14](../results/eda/phase14_codebook_corrections_summary.md) |
| HAREHAB1 ablation | 0.431039, delta −0.011116; feature retained | [Phase 15 record](../results/experiments/20260921T154905753681Z_phase15-boosting-ablate-harehab1-depth5-features128-200trees.json) |
| Frequencies, activities and ALCDAY5 | Historical best 0.441862; diet representation adopted later via AIcrowd feedback | [History](EXPERIMENTS.md#completed-comparisons-against-phase-14) |
| General and clinical binning | 0.440783 and 0.439731; Phase 14 quantiles retained | [Phase 20](../results/eda/phase20_binning_summary.md), [Phase 21–22](../results/eda/phase21_22_preprocessing_summary.md) |
| Indicators and imputation | Indicators 0.440322; restricted-imputation nested confirmation 0.441791 | [Phase 23](../results/eda/phase23_missing_reason_flags_summary.md), [Phase 24](../results/eda/phase24_original_restricted_imputation_summary.md) |
| Parameters, depth and positive weighting | Best family candidate 0.441393; Phase 14 configuration retained | [History](EXPERIMENTS.md#completed-comparisons-against-phase-14) |
| Second seed and averaging | 0.439924 and 0.441111; both lower in all three folds | [Phase 26](../results/eda/phase26_two_seeds_summary.md) |
| Selection of 100/60 features | 0.439224 and 0.437584; both lower in all three folds | [Phase 29](../results/eda/phase29_feature_selection_summary.md) |
| MLP with dedicated preprocessing | 64 → 32: 0.424451; 128 → 64: 0.419268; both lower in all three folds | [Phase 32](../results/eda/phase32_mlp_summary.md) |
| Raw preprocessing | 321 raw inputs: 0.441457 versus cleaned control 0.442155 under the same earlier implementation | [Phase 33](../results/eda/phase33_raw_preprocessing_summary.md) |
| Observed-versus-missing correction | F1 0.440803, delta −0.001352; +206 true positives and +907 false positives versus Phase 14 | [Phase 34](../results/eda/phase34_missing_only_split_summary.md) |
| Logistic baseline with shared Phase 14 cleaning | F1 0.434467 versus 0.442155; booster gain +0.007689 and higher in all three outer folds | [Phase 38](../results/eda/phase38_matched_logistic_summary.md) |

All F1 values above use nested threshold selection. Comparisons through Phase 33 use the booster before the split correction; comparing Phase 33 raw inputs directly with Phase 34 would also change the implementation. Grouped families report their best measured candidate, rather than a common result for every variant.

The conditional paired interval for the Phase 34 F1 delta is [−0.003005, +0.000319] and includes zero. It holds models and thresholds fixed and excludes retraining and repeated-selection uncertainty. The earlier choice retained Phase 14 after AIcrowd feedback; the current release combines Phase 18 and restricted Phase 24 with the same booster parameters.

Phase 16 imputation screening reached exploratory F1 0.442674 by selecting and evaluating a threshold on the same OOF labels. Phase 24 confirmation with inner thresholds did not reproduce that advantage. Interactions listed in the Phase 16 tree configuration were not applied by tree preprocessing, so that result does not measure their effect. Historical linear results precede the correction from median to mode for categorical fills.

Phase 38 shares the exact Phase 14 cleaner, source variables and nested partitions, with model-specific train-fitted finite adaptation for logistic regression. Its paired 95% interval for the booster F1 gain, [+0.004919, +0.010463], conditions on fixed models and thresholds. The comparison does not isolate architecture, and changes from the historical logistic score cannot be attributed solely to cleaning.

## Deferred ideas

These remain hypotheses beyond the completed release:

- Combine restricted imputation with binning that preserves every indicator state.
- Test exercise-frequency or activity representations beyond the measured variants.
- Implement explicit tree-path interactions or a booster–logistic ensemble, selecting all choices within inner training folds.

The completed studies retain 114 records across five experiment ledgers. Future studies would be separate NumPy and standard-library comparisons. Development folds have supported many choices, and early baselines consulted the original 20% validation partition; current results are development evidence after selection.
