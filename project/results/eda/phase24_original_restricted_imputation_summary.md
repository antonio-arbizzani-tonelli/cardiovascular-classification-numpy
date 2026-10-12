# Phase 24 — nested confirmation of original restricted imputation

This reproduces original Phase 16: 303 inputs, eight quantile-binned indicators, restricted imputation of `INCOME2`, `PNEUVAC3`, `EMPLOY1`, height/weight and derivable BMI. The two rare indicators remain merged by original bins; this is distinct from exact-bin Phase 23. It uses Phase 14 development rows and three outer folds: 200 trees, depth 5, learning rate 0.05, minimum leaf 200, 64 bins, 128 candidates, L2 1, model seed 20260920. Two inner folds use seed 20260922 plus outer fold. Imputers are refitted on each training partition without disease labels.

Three historical outer models are reused after hash, training row/label, parameter and bin checks. Outer predictions and training scores replay exactly. Six new inner models save row/fold/hash-linked OOF predictions; thresholds/results are reconstructed. New inner CV, including imputers, takes 22.24 minutes, excluding historical outer fits and preflight. Runtime is Python 3.14.3 / NumPy 2.4.2.

| Metric | Phase 14 | Original imputation | Difference |
| --- | ---: | ---: | ---: |
| f1 | 0.442155227 | 0.441790736 | -0.000364491 |
| precision | 0.367632339 | 0.367812464 | +0.000180125 |
| recall | 0.554572908 | 0.553019845 | -0.001553063 |
| average_precision | 0.428609250 | 0.428610705 | +0.000001455 |
| log_loss | 0.215225071 | 0.215230306 | +0.000005235 |

| Fold | F1 Phase 14 | Imputation F1 | Difference | Inner threshold |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.439026847 | 0.437723315 | -0.001303532 | 0.203563099 |
| 2 | 0.444053521 | 0.442716815 | -0.001336706 | 0.215518614 |
| 3 | 0.443511646 | 0.445095168 | +0.001583523 | 0.213873795 |

| Outcome | Phase 14 | Original imputation | Difference |
| --- | ---: | ---: | ---: |
| True positives | 12,855 | 12,819 | −36 |
| False negatives | 10,325 | 10,361 | +36 |
| False positives | 22,112 | 22,033 | −79 |
| True negatives | 217,216 | 217,295 | +79 |

Earlier exploratory F1 0.442673703 selected/evaluated its threshold on the same OOF labels. Nested evaluation separates threshold selection from outer scoring; reused, previously consulted predictions and repeated candidate selection still limit interpretation. Only one fold improves; the rule requires higher pooled F1 and at least two improved folds. Original imputation is rejected and Phase 14 stays selected. AP/log loss are essentially identical; the exploratory advantage is not confirmed.

The conditional paired 95% F1 interval [−0.002125, +0.001351] uses 20,000 resamples, seed 20260929, and fixed fits/thresholds. It includes zero, excluding retraining and selection uncertainty: no established useful gain or certain loss. [Record](../experiments/20260930T114012414713Z_phase24-original-restricted-imputation-depth5-features128-200trees.json). [Full comparison](../experiments/phase24_original_restricted_imputation_comparison.json).

Combining imputation with all eight indicators preserved through exact bins remains unrun. Phase 24 and Phase 23 also differ in binning, so comparing them does not isolate imputation. [Phase 25](phase25_l2_summary.md) subsequently tested leaf L2 1→5 and rejected it.

All 109 pre-training tests passed; 110 passed after correcting an occupied-bin diagnostic. Only the report changed: merged flags are `EMPLOY1__was_refused` and `PNEUVAC3__was_refused`. Three checkpoint checks were repeated with zero differences; no additional disease model was trained. The record retains original helper/preflight hashes and updated diagnostics; numerical sources, predictions, thresholds and metrics remain identical. Configurations, comparisons and OOF records are saved, previous artifacts retained, with no commit/push in this activity. Official Python 3.9 / NumPy 1.23.1 execution was still pending at this phase.
