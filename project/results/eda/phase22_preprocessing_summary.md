# Phase 22 — activity one-hot

Two independent candidates use Phase 14 as control. Phase 21 preserves all four responses of `BPHIGH4` and `DIABETE3` with exact bins, retaining original quantiles on the other 293 columns. Phase 22 starts directly from Phase 14 and replaces `EXRACT11`/`EXRACT21` with training-observed category indicators; exact bins apply only to those new indicators. Vocabulary uses training rows only. Missing responses stay NaN across the activity block, and an unknown indicator distinguishes finite unseen responses. `EXRACT21=88` remains valid; rare categories are not grouped.

Each candidate uses 262,508 development rows, three outer and two inner threshold folds: nine 200-tree fits. Seeds and model parameters stay fixed: depth 5, learning rate 0.05, minimum leaf 200, L2 1, 128 candidates per node. `HAREHAB1` remains included. The initial 20% partition is excluded here but was consulted historically.

All 101 pre-training tests passed, covering training-only vocabulary, NaNs, column selection and checkpoint continuation. Preflight checks all nine partitions per candidate, categories, bins, NaNs and unchanged feature values. Three reference checkpoints replay saved OOF scores exactly; actual fit profiles match preflight. Candidate OOF/checkpoint outputs are checked after training.

| Model | F1 | Delta F1 | Precision | Recall | AP | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155 | — | 0.367632 | 0.554573 | 0.428609 | 0.215225 |
| Phase 22 | 0.440570 | -0.001585 | 0.368683 | 0.547282 | 0.428746 | 0.215292 |

| Fold | Control F1 | Candidate F1 | Delta | Candidate threshold |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.439027 | 0.436086 | -0.002941 | 0.210091 |
| 2 | 0.444054 | 0.442800 | -0.001253 | 0.221063 |
| 3 | 0.443512 | 0.442878 | -0.000633 | 0.208282 |

| Model | TP | FN | FP | TN |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 12855 | 10325 | 22112 | 217216 |
| Phase 22 | 12686 | 10494 | 21723 | 217605 |

Phase 22 recovers 370 false negatives, loses 539 true positives, introduces 1,416 false positives and removes 1,805: net −169 TP and −389 FP. The small precision gain does not offset lost recall. It loses F1 in all three folds. The conditional paired 95% F1 interval [−0.003396, +0.000201] uses 20,000 class-stratified resamples, seed 20260929, and fixed models/thresholds; it excludes retraining and repeated-selection uncertainty. Full runtime is 46.9 minutes. The candidate fails the operational criterion and is not adopted.

[Complete record](../experiments/20260930T024920071303Z_phase22-phase14-activity-one-hot-depth5-features128-200trees.json). [Verified comparison](../experiments/phase22_preprocessing_comparison.json).

| Outer training | Input | Categories EXRACT11 | Categories EXRACT21 | Exact indicators |
| --- | ---: | ---: | ---: | ---: |
| outer_1 | 446 | 75 | 76 | 153 |
| outer_2 | 446 | 75 | 76 | 153 |
| outer_3 | 446 | 75 | 76 | 153 |

One inner training partition has 445 inputs and 152 exact indicators because a rare category is absent and becomes unknown in validation; the others have 446 inputs. This expected vocabulary change uses no excluded-fold information. At 128 candidates per node, the expansion lowers the chance of considering each other feature from 43.4% to 28.7%. The score measures the complete pipeline; a decrease alone does not prove nominal information useless. In outer training folds, 42–44 `EXRACT11` and 40–41 `EXRACT21` categories have fewer than 200 examples. They cannot alone fill a leaf under the current minimum, though they may share it with missing responses. The unknown indicator is constant in training; it distinguishes an input state without training examples for its specific effect.

Both exact configurations worsen every fold and are rejected. Tiny AP gains do not offset the primary F1 decrease. This does not establish that every exact-binning or nominal method is worse. [Phase 23](phase23_missing_reason_flags_summary.md) later tested nonresponse flags alone and [Phase 24](phase24_original_restricted_imputation_summary.md) restricted imputation; neither was adopted. Native categorical splits and sampling by source feature remain untested ideas. The [final report](../../docs/FINAL_REPORT.md) records final selection.

The experiments left final configuration and threshold unchanged and produced no full-data model or submission. Python 3.14.3 / NumPy 2.4.2 was used; official Python 3.9 / NumPy 1.23.1 execution was not checked here. [Preflight](phase21_22_preflight.json), configurations, records, comparisons and notes are retained; OOF/checkpoint artifacts stay local under results/boosting_artifacts.
