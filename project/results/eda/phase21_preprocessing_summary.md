# Phase 21 — targeted clinical bins

Two independent candidates use Phase 14 as control. Phase 21 preserves all four responses of `BPHIGH4` and `DIABETE3` with exact bins, retaining original quantiles on the other 293 columns. Phase 22 starts directly from Phase 14 and replaces `EXRACT11`/`EXRACT21` with training-observed category indicators; exact bins apply only to those new indicators. Vocabulary uses training rows only. Missing responses stay NaN across the activity block, and an unknown indicator distinguishes finite unseen responses. `EXRACT21=88` remains valid; rare categories are not grouped.

Each candidate uses 262,508 development rows, three outer and two inner threshold folds: nine 200-tree fits. Seeds and model parameters stay fixed: depth 5, learning rate 0.05, minimum leaf 200, L2 1, 128 candidates per node. `HAREHAB1` remains included. The initial 20% partition is excluded here but was consulted historically.

All 101 pre-training tests passed, covering training-only vocabulary, NaNs, column selection and checkpoint continuation. Preflight checks all nine partitions per candidate, categories, bins, NaNs and unchanged feature values. Three reference checkpoints replay saved OOF scores exactly; actual fit profiles match preflight. Candidate OOF/checkpoint outputs are checked after training.

| Model | F1 | Delta F1 | Precision | Recall | AP | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155 | — | 0.367632 | 0.554573 | 0.428609 | 0.215225 |
| Phase 21 | 0.439731 | -0.002424 | 0.361644 | 0.560828 | 0.428817 | 0.215263 |

| Fold | Control F1 | Candidate F1 | Delta | Candidate threshold |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.439027 | 0.435271 | -0.003756 | 0.194159 |
| 2 | 0.444054 | 0.441299 | -0.002754 | 0.210856 |
| 3 | 0.443512 | 0.442973 | -0.000538 | 0.215149 |

| Model | TP | FN | FP | TN |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 12855 | 10325 | 22112 | 217216 |
| Phase 21 | 13000 | 10180 | 22947 | 216381 |

Phase 21 recovers 436 false negatives, loses 291 true positives, introduces 1,744 false positives and removes 909: net +145 TP and +835 FP. Added recall does not offset lower precision. It loses F1 in all three folds. The conditional paired 95% F1 interval [−0.004001, −0.000848] uses 20,000 class-stratified resamples, seed 20260929, and fixed models/thresholds; it excludes retraining and repeated-selection uncertainty. Full runtime is 42.1 minutes. The candidate fails the operational criterion and is not adopted.

[Complete record](../experiments/20260930T020213451046Z_phase21-phase14-clinical-exact-depth5-features128-200trees.json). [Verified comparison](../experiments/phase21_preprocessing_comparison.json).

Both exact configurations worsen every fold and are rejected. Tiny AP gains do not offset the primary F1 decrease. This does not establish that every exact-binning or nominal method is worse. [Phase 23](phase23_missing_reason_flags_summary.md) later tested nonresponse flags alone and [Phase 24](phase24_original_restricted_imputation_summary.md) restricted imputation; neither was adopted. Native categorical splits and sampling by source feature remain untested ideas. The [final report](../../docs/FINAL_REPORT.md) records final selection.

The experiments left final configuration and threshold unchanged and produced no full-data model or submission. Python 3.14.3 / NumPy 2.4.2 was used; official Python 3.9 / NumPy 1.23.1 execution was not checked here. [Preflight](phase21_22_preflight.json), configurations, records, comparisons and notes are retained; OOF/checkpoint artifacts stay local under results/boosting_artifacts.
