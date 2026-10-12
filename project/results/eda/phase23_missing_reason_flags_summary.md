# Phase 23 — eight missing-reason indicators only

The candidate adds the eight restricted Phase 16 flags to Phase 14: unknown/refused `INCOME2`/`PNEUVAC3`, refused `EMPLOY1`, and blank `HTM4`, `WTKG3`/`_BMI5`. No values are imputed. The 295 source columns and their quantiles remain unchanged; only eight flags get exact bins, yielding 303 inputs. Parameters/seeds remain Phase 14's: 200 trees, depth 5, learning rate 0.05, minimum leaf 200, L2 1, 64 bins, 128 candidates per node; `HAREHAB1` stays included.

Evaluation uses 262,508 development rows, three outer and two inner folds: nine fits, with thresholds chosen only on inner OOF predictions and evaluated on excluded outer folds. The verified control is reused. Audit checks nine training partitions, source-column identity and indicator bins; candidate checkpoint replay and thresholds reconstructed from saved inner OOF predictions are exact.

| Model | F1 | Precision | Recall | AP | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155 | 0.367632 | 0.554573 | 0.428609 | 0.215225 |
| Phase 23: indicators only | 0.440322 | 0.363606 | 0.558067 | 0.428833 | 0.215258 |

| Fold | F1 Phase 14 | Indicator F1 | Delta F1 | Indicator threshold |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.439027 | 0.436573 | -0.002454 | 0.211290 |
| 2 | 0.444054 | 0.441280 | -0.002774 | 0.199453 |
| 3 | 0.443512 | 0.443071 | -0.000441 | 0.212347 |

| Model | TP | FN | FP | TN |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 12855 | 10325 | 22112 | 217216 |
| Phase 23 | 12936 | 10244 | 22641 | 216687 |

F1 changes −0.001833 and loses all three folds; CV takes 72.0 minutes. Net changes are +81 TP and +529 FP. Transitions recover 517 false negatives, lose 436 true positives, introduce 1,924 false positives and remove 1,395. AP rises 0.000224 and log loss rises 0.000033; higher recall does not offset lower precision. Exploratory F1 with a global threshold selected on the same outer OOF labels is 0.441249, also below its matched control 0.442078. The conditional paired 95% F1 interval [−0.003648, −0.000013] holds fits/thresholds fixed, excluding retraining and repeated selection.

Keep Phase 14: the operational criterion fails. This test does not exclude a benefit from adding imputation. The historical exploratory 0.442674 combined flags and imputation, selected/evaluated its threshold on the same OOF labels and collapsed two flags through quantile binning; this is not confirmation of that combination. The original restricted-imputation confirmation was subsequently completed in [Phase 24](phase24_original_restricted_imputation_summary.md).

| Indicator | Minimum % | Maximum % |
| --- | ---: | ---: |
| EMPLOY1__was_refused | 0.843 | 0.867 |
| INCOME2__was_unknown | 7.857 | 7.947 |
| INCOME2__was_refused | 9.224 | 9.343 |
| PNEUVAC3__was_unknown | 7.641 | 7.691 |
| PNEUVAC3__was_refused | 0.455 | 0.489 |
| HTM4__was_blank | 3.451 | 3.492 |
| WTKG3__was_blank | 6.957 | 7.023 |
| _BMI5__was_blank | 8.227 | 8.290 |

Flag prevalence does not measure predictive utility. Eight extra columns also change feature sampling while retaining 128 candidates per node, so the result concerns the full pipeline. All 104 pre-training tests passed, including inner OOF persistence, fold boundaries and identical results with/without saving. Three candidate checkpoint outputs and inner thresholds exactly match recorded artifacts. Python 3.14.3 / NumPy 2.4.2 was used; official Python 3.9 / NumPy 1.23.1 execution remains unchecked here. The initial 20% partition is excluded in this test but was used historically. No full-data fit or submission was generated; final configuration and threshold were unchanged.

- [Complete record](../experiments/20260930T103147105876Z_phase23-phase14-missing-reason-flags-depth5-features128-200trees.json).
- [Verified comparison](../experiments/phase23_missing_reason_flags_comparison.json).
- [Pre-training audit](phase23_missing_reason_flags_preflight.json).
- Outer predictions, three checkpoints and three inner OOF artifacts: results/boosting_artifacts/phase23_phase14_missing_reason_flags/.
