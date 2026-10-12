# Phase 27 — learning rate 0.025 and 400 trees

Only learning rate changes 0.05→0.025 and trees 200→400; preprocessing, 295 features, other parameters, splits and seeds remain Phase 14.

The verified historical Phase 14 control is reused. The same development rows, splits and seeds use three outer and two inner threshold folds, with nine fresh candidate fits.

| Metric | Phase 14 | Candidate | Delta |
| --- | ---: | ---: | ---: |
| accuracy | 0.876434242 | 0.875017142 | -0.001417100 |
| precision | 0.367632339 | 0.364261750 | -0.003370589 |
| recall | 0.554572908 | 0.557377049 | +0.002804142 |
| f1 | 0.442155227 | 0.440587222 | -0.001568005 |
| specificity | 0.907607969 | 0.905782023 | -0.001825946 |
| balanced_accuracy | 0.731090438 | 0.731579536 | +0.000489098 |
| average_precision | 0.428609250 | 0.429352055 | +0.000742805 |
| log_loss | 0.215225071 | 0.215123329 | -0.000101742 |

| Fold | Candidate F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.435906570 | -0.003120278 | 0.206211866 |
| 2 | 0.443457606 | -0.000595915 | 0.210838301 |
| 3 | 0.442440913 | -0.001070733 | 0.208149784 |

| Outcome | Phase 14 | Candidate |
| --- | ---: | ---: |
| false_negatives | 10325 | 10260 |
| false_positives | 22112 | 22549 |
| true_negatives | 217216 | 216779 |
| true_positives | 12855 | 12920 |

The operational criterion is unmet: 0/3 folds improve and final configuration stays unchanged. The conditional paired F1-delta interval [−0.003124704, −0.000038643] uses 20,000 resamples and fixed fits/thresholds; it excludes retraining and repeated-selection uncertainty.

CV takes 111.01 minutes, overlapping another experiment and excluding preflight/final checks, in Python 3.14.3 / NumPy 2.4.2. Nine training partitions are verified; columns/bins are unchanged except for the intended difference. Checkpoints, probabilities, rows, hashes, inner thresholds and metrics replay correctly. The initial 20% partition is excluded here; development folds have already been consulted by multiple experiments.

Record: results/boosting_artifacts/phase27_phase14_lr0025_400trees/records/20260930T221319968519Z_phase27-phase14-lr0025-400trees-depth5-features128-400trees.json. Local artifacts and comparison: results/boosting_artifacts/phase27_phase14_lr0025_400trees/.
