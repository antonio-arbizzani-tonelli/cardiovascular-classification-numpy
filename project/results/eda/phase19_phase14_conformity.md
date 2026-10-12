# Phase 14 conformity check

All 35 checks passed on 29 September 2026 without training any model. The [complete JSON](phase19_phase14_conformity.json) records hashes, checks and feature names by fold.

The dataset/cache hashes match Phase 14: 328,135 rows and 321 raw columns. Development has 262,508 rows and 23,180 positives; rows, order, labels and fold assignments match. Model parameters and tree preprocessing match, retaining 295 features and `HAREHAB1`, without imputation. As of this dated check, booster, evaluation and runner were unchanged from the initial commit; local preprocessing extensions were inactive in Phase 14.

Checkpoint/OOF hashes are correct. Replayed predictions differ by exactly zero in every fold; nested metrics reconstructed from predictions match the record. The historical threshold 0.21086909970855153 equals the mean of three inner-selected thresholds. Code 777 maps to NaN for six food-frequency and four exercise frequency/duration fields, as specified by the codebook.

Seeds are 20260918 for the initial split, 20260919 for outer folds, 20260920 for boosting and 20260922 plus outer-fold number for inner folds. Replay checks Python 3.14.3 / NumPy 2.4.2, not a new execution under official Python 3.9 / NumPy 1.23.1.

This verifies the saved reference at the stated date; later source extensions are separate. The [final audit](../../docs/FINAL_AUDIT.md) again reproduced all three Phase 14 checkpoints with updated sources. The final model retains `HAREHAB1`; later frequency/activity tests are covered in the [report](../../docs/FINAL_REPORT.md). Current full-train OOF calibration supersedes the historical threshold above.

The separate minimum-leaf-150 and learning-rate-0.07 tests both used inner-selected thresholds. [Phase 19 results](phase19_transfer_summary.md) did not support adoption; their combination was not run.
