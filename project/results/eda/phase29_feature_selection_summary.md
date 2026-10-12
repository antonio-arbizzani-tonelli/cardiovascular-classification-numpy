# Phase 29 — selecting 100 and 60 features

Historical Phase 14 has nested F1 0.442155227. Both tested reductions lose F1 in all three folds and are rejected.

| Input | F1 | Delta F1 | Precision | Recall | AP | Log loss | Improved folds |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 0.439223556 | -0.002931671 | 0.366645 | 0.547627 | 0.427210 | 0.215535 | 0/3 |
| 60 | 0.437584073 | -0.004571154 | 0.358536 | 0.561346 | 0.423974 | 0.216362 | 0/3 |

## Protocol

Each outer/inner training partition independently selects features. A 200-tree Phase 14 selector and its preprocessing fit on 80% of that partition; a stratified 20% holdout selects one threshold and supplies permutation importance. The threshold is then fixed. Importance uses at most 10,000 class-stratified rows from that holdout and three permutations per feature, including NaNs. Ranking order is fixed before results: mean F1 drop, AP drop, log-loss increase, split count and original order as exact tie-breakers. Three repeats describe instability, not statistical proof. Semantic-group permutations are diagnostic and do not affect rankings/budgets. Missingness percentage alone never drops a feature.

Top 60 is contained in top 100 in every training partition. Reduced boosters refit on all of their training rows, retaining the feature-sampling fraction 128/295: 44 candidates with 100 inputs and 27 with 60. Final thresholds use two inner OOF folds; three outer folds and reference seeds stay fixed. Permutation importance may undervalue redundant fields or fields useful after retraining. The comparison tests this selection pipeline, not the best possible subset.

## Top 100

F1 fold deltas are −0.004166111, −0.002138454 and −0.002742295. Count deltas are TP −161, FP −184, TN +184, FN +161. The conditional paired 95% F1 interval is [−0.004927242814316479, −0.0009424799522040488], holding fits/thresholds fixed and excluding training/repeated-selection uncertainty. Only 37/100 columns occur in all three outer lists; pairwise Jaccard values are 0.3793103448275862, 0.3986013986013986 and 0.3986013986013986. Nine reduced fits/preprocessing take 22.25 minutes; nine shared selectors take 46.89 minutes. The promotion rule fails and final model is not changed automatically.

[Record](../../results/experiments/phase29_feature_selection/20260930T222023662096Z_phase29-phase14-fold-local-top100-permutation-features.json).

## Top 60

F1 fold deltas are −0.001707034, −0.009785136 and −0.002303613. Count deltas are TP +157, FP +1,168, TN −1,168, FN −157. The conditional paired 95% F1 interval is [−0.006783863388137183, −0.0023207463111974587], with the same fixed-fit limitations. Only 19/60 columns occur in all outer lists; Jaccard values are 0.34831460674157305, 0.30434782608695654 and 0.31868131868131866. Nine reduced fits/preprocessing take 13.51 minutes, with the shared 46.89-minute selector cost. The promotion rule fails.

[Record](../../results/experiments/phase29_feature_selection/20260930T222046496842Z_phase29-phase14-fold-local-top60-permutation-features.json).

## Development ranking

A tenth selector uses only the 262,508 development rows and produces diagnostic lists for possible later training. Those global lists do not produce the CV scores above. A future full-data fit must repeat selection on its own training rows.

- [Full ranking](phase29_feature_selection/development/ranking.csv).
- [100-feature list](phase29_feature_selection/development/top100.json).
- [60-feature list](phase29_feature_selection/development/top60.json).
- [Group importance](phase29_feature_selection/development/group_importance.json).

| Rank | Feature | Mean F1 drop | Standard deviation | AP drop | Missing in fit |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | SEX | 0.037302 | 0.007413 | 0.036342 | 0.00% |
| 2 | GENHLTH | 0.020772 | 0.004291 | 0.022476 | 0.26% |
| 3 | _AGE80 | 0.018199 | 0.006575 | 0.014648 | 0.00% |
| 4 | HAREHAB1 | 0.014587 | 0.000564 | 0.068743 | 99.77% |
| 5 | FC60_ | 0.012259 | 0.002375 | 0.000779 | 0.00% |
| 6 | MAXVO2_ | 0.009136 | 0.003564 | 0.001709 | 0.00% |
| 7 | CVDSTRK3 | 0.008628 | 0.001859 | 0.014033 | 0.22% |
| 8 | TOLDHI2 | 0.006945 | 0.000772 | 0.001860 | 14.10% |
| 9 | _AGE_G | 0.006451 | 0.003032 | 0.001907 | 0.00% |
| 10 | _RFCHOL | 0.005971 | 0.002054 | 0.006192 | 14.10% |
| 11 | BPHIGH4 | 0.005410 | 0.001544 | 0.000457 | 0.29% |
| 12 | CVDASPRN | 0.005299 | 0.002462 | 0.005048 | 95.68% |
| 13 | CHOLCHK | 0.005237 | 0.006324 | 0.003073 | 14.63% |
| 14 | _RFHYPE5 | 0.005126 | 0.001419 | 0.001147 | 0.29% |
| 15 | _RFHLTH | 0.004908 | 0.006011 | 0.012113 | 0.26% |
| 16 | DIFFWALK | 0.004741 | 0.001473 | 0.000698 | 3.31% |
| 17 | QLACTLM2 | 0.004534 | 0.002058 | 0.001206 | 2.79% |
| 18 | CHCCOPD1 | 0.004527 | 0.003541 | 0.009234 | 0.47% |
| 19 | BPMEDS | 0.004361 | 0.002044 | 0.011640 | 59.91% |
| 20 | SMOKE100 | 0.003464 | 0.002484 | 0.000113 | 3.99% |
| 21 | INCOME2 | 0.003331 | 0.001508 | 0.000199 | 17.86% |
| 22 | IDAY | 0.002546 | 0.000661 | 0.000174 | 0.00% |
| 23 | DRNK3GE5 | 0.002543 | 0.001619 | -0.000123 | 52.83% |
| 24 | EMPLOY1 | 0.002538 | 0.002985 | -0.000709 | 0.85% |
| 25 | PNEUVAC3 | 0.002380 | 0.004288 | 0.004762 | 17.62% |
| 26 | PERSDOC2 | 0.002158 | 0.003163 | 0.003372 | 0.41% |
| 27 | PHYSHLTH | 0.002092 | 0.002181 | 0.001189 | 2.15% |
| 28 | _SMOKER3 | 0.002075 | 0.003497 | -0.000071 | 4.09% |
| 29 | FLUSHOT6 | 0.002028 | 0.000628 | 0.000175 | 10.07% |
| 30 | ARTHDIS2 | 0.002024 | 0.000120 | -0.000052 | 70.04% |

Selection does not settle `HAREHAB1` admissibility. The historical external 20% partition is excluded here, but development folds have been reused many times; these are not independent final-test results.

Total runtime is 93.96 minutes: ten selectors and 18 candidate fits run sequentially with one NumPy thread and lower Windows priority. `results/boosting_artifacts/phase29_phase14_feature_selection` holds numerical artifacts and checkpoints. Each selector saves fit/holdout/permutation/excluded rows; each candidate saves list, training rows/labels, probabilities and checkpoint. All 18 checkpoints replay probabilities exactly. Outer/inner OOF, executed source, preflight and hashes are preserved.

Protected Phase 27/28 sources/configurations/inputs are verified before/after; their directories and shared registries are untouched. Two new records use the dedicated `results/experiments/phase29_feature_selection/` registry. No new submission, final-model change, commit or push occurred.

## Stability and rare features

[Selection frequency for 295 columns](phase29_feature_selection/selection_frequency.csv) diagnoses training-specific lists; it is not a new global list for the same folds. Shared support is only 37/100 and 19/60. The development top-100 boundary is `CPDEMO1` (F1 drop 0.000347, SD 0.000120); top-60 boundary is `PDIABTST` (0.000828, SD 0.000711). Near-cutoff importance is small relative to variability.

`HAREHAB1` ranks fourth on development and appears in both outer lists in every fold. The six inner selectors have fewer than 200 known responses and do not use it, below minimum leaf size. Full inner training can have different support. This explains ranking differences without identifying the cause of F1 loss. Counts below refer to the cleaned selector representation; they do not replace the raw recorded-response count used in the temporal-proxy audit.

| Partition | Observed responses in full training | Observed responses in selector fit | Split HAREHAB1 | Rank |
| --- | ---: | ---: | ---: | ---: |
| development | 607 | 488 | 106 | 4 |
| outer_1 | 384 | 302 | 90 | 3 |
| outer_1_inner_1 | 188 | 153 | 0 | 170 |
| outer_1_inner_2 | 196 | 163 | 0 | 165 |
| outer_2 | 405 | 331 | 94 | 3 |
| outer_2_inner_1 | 196 | 154 | 0 | 197 |
| outer_2_inner_2 | 209 | 165 | 0 | 193 |
| outer_3 | 425 | 334 | 92 | 3 |
| outer_3_inner_1 | 206 | 163 | 0 | 160 |
| outer_3_inner_2 | 219 | 167 | 0 | 191 |

## Diagnostic semantic groups

Group columns are shuffled together. F1 drops depend on group size and relationships; they are not causal effects or estimated gains from removing the group. Groups do not determine top-100/top-60 lists.

| Group | Mean F1 drop | Standard deviation |
| --- | ---: | ---: |
| age | 0.021107 | 0.007160 |
| hypertension | 0.007624 | 0.001154 |
| diabetes | 0.005926 | 0.001235 |
| smoking | 0.005869 | 0.001588 |
| body_size | 0.001511 | 0.000567 |
| exercise_frequency_1 | 0.001226 | 0.001500 |
| exercise_summary | 0.000385 | 0.000803 |
| exercise_frequency_2 | 0.000310 | 0.000371 |
| alcohol | 0.000054 | 0.003137 |
| diet | -0.000312 | 0.003662 |

Both conditional intervals are negative but exclude retraining and repeated experiment selection. The evidence does not prove every 100- or 60-column subset worse. The 30-column variant was conditional on useful earlier reductions and was not started. All 137 pre-training tests passed and 138 passed afterwards. Twenty public top-100/top-60 lists match the private selections actually used. Records in both registries have unique IDs/correct hashes, report links exist, and protected inputs, sources and final configuration are unchanged. Planning/history were updated only after all three executions finished.
