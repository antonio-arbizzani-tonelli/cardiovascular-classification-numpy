# Phase 28 — remove ALCDAY5 only

Only ALCDAY5 is removed; DROCDY3_ and all other Phase 14 inputs/parameters remain, leaving 294 features.

The verified historical Phase 14 control is reused. The same development rows, splits and seeds use three outer and two inner threshold folds, with nine fresh candidate fits.

| Metric | Phase 14 | Candidate | Delta |
| --- | ---: | ---: | ---: |
| accuracy | 0.876434242 | 0.873036250 | -0.003397992 |
| precision | 0.367632339 | 0.360563845 | -0.007068494 |
| recall | 0.554572908 | 0.566091458 | +0.011518550 |
| f1 | 0.442155227 | 0.440535142 | -0.001620086 |
| specificity | 0.907607969 | 0.902765243 | -0.004842726 |
| balanced_accuracy | 0.731090438 | 0.734428350 | +0.003337912 |
| average_precision | 0.428609250 | 0.429039626 | +0.000430376 |
| log_loss | 0.215225071 | 0.215250685 | +0.000025614 |

| Fold | Candidate F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.435323752 | -0.003703096 | 0.198075855 |
| 2 | 0.441648634 | -0.002404887 | 0.205198772 |
| 3 | 0.444821383 | +0.001309737 | 0.209596383 |

| Outcome | Phase 14 | Candidate |
| --- | ---: | ---: |
| false_negatives | 10325 | 10058 |
| false_positives | 22112 | 23271 |
| true_negatives | 217216 | 216057 |
| true_positives | 12855 | 13122 |

The operational criterion is unmet: 1/3 folds improve and final configuration stays unchanged. The conditional paired F1-delta interval [−0.003295025, +0.000067219] uses 20,000 resamples and fixed fits/thresholds; it excludes retraining and repeated-selection uncertainty.

CV takes 57.84 minutes, overlapping another experiment and excluding preflight/final checks, in Python 3.14.3 / NumPy 2.4.2. Nine training partitions are verified; columns/bins are unchanged except for the intended difference. Checkpoints, probabilities, rows, hashes, inner thresholds and metrics replay correctly. The initial 20% partition is excluded here; development folds have already been consulted by multiple experiments.

Record: results/boosting_artifacts/phase28_phase14_ablate_alcday5/records/20260930T212010451103Z_phase28-phase14-ablate-alcday5-depth5-features128-200trees.json. Local artifacts and comparison: results/boosting_artifacts/phase28_phase14_ablate_alcday5/.
