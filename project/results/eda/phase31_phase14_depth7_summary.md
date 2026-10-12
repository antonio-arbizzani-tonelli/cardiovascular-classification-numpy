# Phase 31 — depth 7

Only maximum depth changes 5→7; positive weight 1, 200 trees, learning rate 0.05, 295 features and all other Phase 14 settings remain fixed.

The verified historical Phase 14 control is reused. The same development rows, splits and seeds use three outer and two inner threshold folds, with nine fresh candidate fits.

| Metric | Phase 14 | Candidate | Delta |
| --- | ---: | ---: | ---: |
| accuracy | 0.876434242 | 0.874940954 | -0.001493288 |
| precision | 0.367632339 | 0.364346970 | -0.003285369 |
| recall | 0.554572908 | 0.559016393 | +0.004443486 |
| f1 | 0.442155227 | 0.441160950 | -0.000994277 |
| specificity | 0.907607969 | 0.905539678 | -0.002068291 |
| balanced_accuracy | 0.731090438 | 0.732278036 | +0.001187597 |
| average_precision | 0.428609250 | 0.428748338 | +0.000139087 |
| log_loss | 0.215225071 | 0.215090233 | -0.000134838 |

| Fold | Candidate F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.436892735 | -0.002134113 | 0.197111771 |
| 2 | 0.444066355 | +0.000012834 | 0.220880536 |
| 3 | 0.442909091 | -0.000602555 | 0.215307776 |

| Outcome | Phase 14 | Candidate |
| --- | ---: | ---: |
| false_negatives | 10325 | 10222 |
| false_positives | 22112 | 22607 |
| true_negatives | 217216 | 216721 |
| true_positives | 12855 | 12958 |

The operational criterion is unmet: 1/3 folds improve and final configuration stays unchanged. The conditional paired F1-delta interval [−0.002978237, +0.001004398] uses 20,000 resamples and fixed fits/thresholds; it excludes retraining and repeated-selection uncertainty.

CV takes 63.89 minutes, overlapping another experiment and excluding preflight/final checks, in Python 3.14.3 / NumPy 2.4.2. Nine training partitions are verified; columns/bins are unchanged except for the intended difference. Checkpoints, probabilities, rows, hashes, inner thresholds and metrics replay correctly. The initial 20% partition is excluded here; development folds have already been consulted by multiple experiments.

Record: results/boosting_artifacts/phase31_phase14_depth7/records/20261001T001533065665Z_phase31-phase14-depth7-depth7-features128-200trees.json. Local artifacts and comparison: results/boosting_artifacts/phase31_phase14_depth7/.
