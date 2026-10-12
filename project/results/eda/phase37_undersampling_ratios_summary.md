# Phase 37 — random 5:1 and 7:1 undersampling on Phase 14

The matched control is historical Phase 14 (nested F1 0.442155227), using the historical numerical snapshot verified for Phase 35. All positives remain in training. A shared random permutation selects negatives in each fit, so 5:1 rows are contained in 7:1. Every validation row remains; preprocessing/bins use selected training rows only. Inner OOF selects thresholds, without holdout/test evaluation.

The same 295 predictors, parameters, seeds and partitions use nine fits per candidate: three outer and six inner. Phase 36's 3:1 result uses corrected Phase 34 and is not a comparable historical control.

| Historical pipeline | F1 | Precision | Recall | AP | False positives | Delta F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All rows — Phase 14 | 0.442155227 | 0.367632339 | 0.554572908 | 0.428609250 | 22112 | +0.000000000 |
| Random 5:1 | 0.438225776 | 0.365893131 | 0.546203624 | 0.426827450 | 21942 | -0.003929452 |
| Random 7:1 | 0.439819715 | 0.363931740 | 0.555694564 | 0.427890611 | 22513 | -0.002335512 |

## Ratio 5:1

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.435351040 | -0.003675808 | 0.353960287 |
| 2 | 0.438983318 | -0.005070203 | 0.366027358 |
| 3 | 0.440367921 | -0.003143725 | 0.357943822 |

No fold improves. The conditional paired F1-delta interval is [−0.005761870, −0.002082791]. Outer fits keep 92,718/92,718/92,724 rows, including every positive. Full runner time is 37.4 minutes; no checkpoint resumes (0/9). Record: `results/experiments/20261007T135726798413Z_phase37-phase14-random-ratio5-depth5-features128-200trees.json`.

## Ratio 7:1

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.436101368 | -0.002925479 | 0.267288788 |
| 2 | 0.440231866 | -0.003821655 | 0.287927505 |
| 3 | 0.443332291 | -0.000179355 | 0.286280142 |

No fold improves. The conditional paired F1-delta interval is [−0.004093154, −0.000610538]. Outer fits keep 123,624/123,624/123,632 rows, including every positive. Full runner time is 47.2 minutes; no checkpoint resumes (0/9). Record: `results/experiments/20261007T140713077912Z_phase37-phase14-random-ratio7-depth5-features128-200trees.json`.

Candidates run concurrently. Three reference and all 18 candidate models replay; every inner OOF probability set, retained-row bin thresholds, inner decision thresholds and metrics are reconstructed. All positives are retained, validation rows excluded from training and 5:1 is contained in 7:1 in all nine fits. Sources and 25-tree checkpoints remain local.

Ratios are fixed before results and only one sampling seed is tested. Development folds were already consulted; bootstrap conditions on fixed fits, samples and thresholds and excludes new sampling, retraining and repeated selection. Raw probabilities reflect sampled prevalence. These historical tests change neither corrected Phase 34 configuration nor submission.

Reproduce with `python -m tools.phase37_undersampling_ratios prepare`, `python -m tools.phase37_undersampling_ratios run` and `python -m tools.phase37_undersampling_ratios report --publish`. Local official data and the Phase 35 historical snapshot are required.

Retain all training rows for the historical implementation. Ratio 7:1 reduces the 5:1 loss, but both lose F1 in every fold. Conditional intervals are entirely negative with the stated limits; historical best remains 0.442155227.

All 20 selected unit tests pass. Each ratio passes full synthetic workflow, saved-result replay and exact 25-tree resume with eight completed checkpoints reused. All 18 real models and 18 bin sets are verified; the 18 real fits were fresh without resumes.
