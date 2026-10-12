# Phase 26 — second seed and uniform two-model mean

Phase 14's 295 features, `HAREHAB1`, codebook cleaning, quantile bins and tree-handled NaNs remain fixed: 200 trees, depth 5, learning rate 0.05, minimum leaf 200, 64 bins, 128 candidates and L2 1. Seeds are 20260920/20260921 and weights 0.5/0.5 are fixed before evaluation. The same 262,508 development rows use three outer and two inner threshold folds. The mean's threshold is optimized on averaged inner probabilities, never averaged individual thresholds.

Three verified Phase 14 outer models are reused. Six inner reference fits recover historical thresholds/metrics exactly; nine new fits train the second seed. Averaging requires no additional fit.

| Metric | Phase 14 | Second seed | Uniform mean |
| --- | ---: | ---: | ---: |
| f1 | 0.442155227 | 0.439923622 | 0.441111283 |
| precision | 0.367632339 | 0.375140761 | 0.366530566 |
| recall | 0.554572908 | 0.531751510 | 0.553796376 |
| average_precision | 0.428609250 | 0.428760111 | 0.429367500 |
| log_loss | 0.215225071 | 0.215221801 | 0.215085280 |

## Second seed

| Fold | F1 | Delta Phase 14 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.435294765 | -0.003732082 | 0.227453233 |
| 2 | 0.442490920 | -0.001562601 | 0.215864448 |
| 3 | 0.441795157 | -0.001716489 | 0.216838285 |

F1 delta is −0.002231605 with zero improved folds. The conditional paired 95% interval is [−0.004167598, −0.000292364].

| Outcome | Phase 14 | Candidate | Difference |
| --- | ---: | ---: | ---: |
| true_positives | 12855 | 12326 | -529 |
| false_negatives | 10325 | 10854 | +529 |
| false_positives | 22112 | 20531 | -1581 |
| true_negatives | 217216 | 218797 | +1581 |

[Record](../experiments/20260930T180910156200Z_phase26-phase14-seed20260921-depth5-features128-200trees.json).

## Uniform mean

| Fold | F1 | Delta Phase 14 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.436783870 | -0.002242977 | 0.197498017 |
| 2 | 0.443951165 | -0.000102356 | 0.217533467 |
| 3 | 0.442919723 | -0.000591922 | 0.216064903 |

F1 delta is −0.001043944 with zero improved folds. The conditional paired 95% interval is [−0.002308415, +0.000213879].

| Outcome | Phase 14 | Candidate | Difference |
| --- | ---: | ---: | ---: |
| true_positives | 12855 | 12837 | -18 |
| false_negatives | 10325 | 10343 | +18 |
| false_positives | 22112 | 22186 | +74 |
| true_negatives | 217216 | 217142 | -74 |

[Record](../experiments/20260930T181509840904Z_phase26-phase14-uniform-mean-two-seeds.json).

The two seeds' probability correlation is 0.995288962 and mean absolute difference 0.006268225. Their own inner-selected decisions disagree on 4,458 rows: 1,037 positives and 3,421 negatives, reflecting both scores and thresholds. Bootstrap uses 20,000 resamples, seed 20260929, and fixed fits/thresholds; it excludes retraining and repeated selection. Nested thresholds protect that selection step; reused development folds are not an untouched final test.

All 15 new fits complete in 273.63 elapsed minutes, excluding preflight/final checks. Checkpoint probabilities replay exactly; training rows, labels, inner folds, hashes and thresholds are checked. Both components and the mean retain outer/inner OOF artifacts. Python 3.14.3 / NumPy 2.4.2 was used; official Python 3.9 / NumPy 1.23.1 execution was pending.

All 120 pre-training tests passed, then 124 after a metadata-check correction. Old Phase 14 checkpoints lack `output_feature_names`; their order is verified through frozen preprocessing/bins and exact probability replay. New checkpoints still require that field. Only verification changed; no extra training was needed. Executed runner/preflight and corrected verifier are separately archived with hashes. The original log retains the initial final-check failure; a subsequent `compare` exits 0, with output in the local ignored `results/boosting_artifacts/phase26_two_seeds/verification_stdout.log`. Distributed verification is in the [comparison JSON](../experiments/phase26_two_seeds_comparison.json).

Keep seed 20260920 and L2 1: both candidates lose every fold. The mean loses 18 TP and adds 74 FP; AP +0.000758 and log loss −0.000140 do not improve nested F1. The mean beats the second seed alone by +0.001187661 F1 in every fold, but its paired interval [−0.000488604, +0.002864304] includes zero. This pair does not justify extending a seed grid.

Recorded training time is 273.63 minutes, about 4 hours 34 minutes, dominated by the second seed's first outer fit at 215.28 minutes. Its log moves from 175 trees at 529.5 seconds to 200 at 12,263.3 seconds; later process CPU time was about 35 minutes. The cause of that elapsed-time gap is unresolved. Remaining fits/preprocessing total 58.35 minutes. This is not typical two-seed ensemble cost, and excludes preparation/final verification.

[Phase 27](phase27_phase14_lr0025_400trees_summary.md) later rejected learning rate 0.025 with 400 trees. Final configuration/threshold were unchanged during this phase. [Full comparison](../experiments/phase26_two_seeds_comparison.json), [preflight](phase26_two_seeds_preflight.json), [second-seed configuration](../../configs/experiments/phase26_phase14_seed20260921.json).
