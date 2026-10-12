# Phase 19 — transferring tuning to Phase 14

The conformity audit passed 35 checks of data, labels, splits, configurations, preprocessing and all three Phase 14 checkpoint outputs, with exact prediction replay and no training during the audit. The two candidates each change one parameter while retaining 295 features, `HAREHAB1` and original seeds. Each uses 262,508 development rows, three outer folds and two inner threshold folds: nine fits per candidate.

| Model | F1 | Precision | Recall | AP | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155 | 0.367632 | 0.554573 | 0.428609 | 0.215225 |
| Min leaf 150 | 0.439991 | 0.361279 | 0.562554 | 0.429144 | 0.215229 |
| Learning rate 0.07 | 0.440700 | 0.368610 | 0.547843 | 0.429091 | 0.215133 |

| Model | Fold 1 | Fold 2 | Fold 3 | Fold mean |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 0.439027 | 0.444054 | 0.443512 | 0.442197 |
| Min leaf 150 | 0.435083 | 0.441410 | 0.443472 | 0.439988 |
| Learning rate 0.07 | 0.437423 | 0.442220 | 0.442727 | 0.440790 |

| Model | Fold 1 | Fold 2 | Fold 3 | Mean |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 0.203057 | 0.220105 | 0.209446 | 0.210869 |
| Min leaf 150 | 0.205464 | 0.203839 | 0.206650 | 0.205318 |
| Learning rate 0.07 | 0.198371 | 0.219143 | 0.221450 | 0.212988 |

| Model | TP | FN | FP | TN |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 12855 | 10325 | 22112 | 217216 |
| Min leaf 150 | 13040 | 10140 | 23054 | 216274 |
| Learning rate 0.07 | 12699 | 10481 | 21752 | 217576 |

Minimum leaf 150 changes F1 by −0.002165 and loses all three folds (deltas −0.003944, −0.002644, −0.000040). It adds 185 true positives and 942 false positives. Among changing decisions, 483 false negatives are recovered, 298 true positives lost, 1,926 false positives introduced and 984 removed. AP rises 0.000535; log loss rises 0.000004. The conditional paired 95% F1 interval is [−0.003801, −0.000494]. Validation takes 59.20 minutes. [Record](../experiments/20260929T224222134395Z_phase19-phase14-leaf150-depth5-features128-200trees.json).

Learning rate 0.07 changes F1 by −0.001455 and loses all three folds (−0.001604, −0.001834, −0.000785). It loses 156 true positives while avoiding 360 false positives. Decision transitions recover 393 false negatives, lose 549 true positives, introduce 1,590 false positives and remove 1,950. AP rises 0.000481; log loss falls 0.000092. The conditional paired 95% F1 interval is [−0.003297, +0.000415]. Validation takes 59.45 minutes. [Record](../experiments/20260929T224236985386Z_phase19-phase14-lr07-depth5-features128-200trees.json).

Both intervals hold fits and thresholds fixed, excluding retraining and repeated selection. Neither candidate meets the rule of higher pooled F1 and improvement in at least two folds. Keep minimum leaf 200 and learning rate 0.05. Small AP gains do not replace the primary F1 criterion. The Phase 17 advantage on its branch without `HAREHAB1` does not transfer to these isolated Phase 14 tests; other preprocessing choices also differ, so the change cannot be attributed to that feature alone. No additive benefit or combined test is established. The later isolated `ALCDAY5` ablation retains `DROCDY3_` and other inputs; [Phase 28](phase28_phase14_ablate_alcday5_summary.md) did not support adoption.

Candidates ran in parallel under Python 3.14.3 / NumPy 2.4.2. Recorded durations are not controlled speed comparisons with historical Phase 14. All 86 local tests passed and reference checkpoints replay exactly; this is not official Python 3.9 / NumPy 1.23.1 validation.

The remote Phase 16 configuration lists five interactions, but versioned tree preprocessing does not read `interactions`; retained source and reported output both have 295 columns. Its score therefore does not demonstrate a test of those interactions. This documentation correction does not affect the verified Phase 19 candidates. JSON records/comparisons are distributable; checkpoint, log and row-level OOF artifacts stay local. The experiment did not change final configuration.
