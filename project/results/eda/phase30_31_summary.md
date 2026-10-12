# Phases 30–31 — weight 2 and depth 7 versus Phase 14

Both candidates are complete and verified; neither achieves higher pooled F1 with improvement in at least two folds. Keep Phase 14 with weight 1 and depth 5. The same 262,508 development rows and 295 features, including `ALCDAY5`/`HAREHAB1`, use reference seeds/splits, three outer and two inner threshold folds. Nine fresh fits per candidate are compared with exactly replayed historical reference artifacts.

Phase 30 changes only positive weight 1→2 at depth 5. Logistic loss, gradients, Hessians and initial prevalence are weighted; quantiles and the 200-row leaf minimum use original rows. Metrics/F1 threshold selection are unweighted. Phase 31 changes only maximum depth 5→7 at weight 1. Both retain 200 trees, learning rate 0.05, L2 1, 64 bins and 128 feature candidates. Weight 2 plus depth 7 is not tested.

| Metric | Phase 14 | Phase 30, weight 2 | Phase 31, depth 7 |
| --- | ---: | ---: | ---: |
| f1 | 0.442155227 | 0.439118448 | 0.441160950 |
| precision | 0.367632339 | 0.361155162 | 0.364346970 |
| recall | 0.554572908 | 0.560008628 | 0.559016393 |
| average_precision | 0.428609250 | 0.428237932 | 0.428748338 |
| log_loss | 0.215225071 | 0.231722615 | 0.215090233 |

| Fold | F1 Phase 14 | F1 weight 2 | Delta weight 2 | F1 depth 7 | Delta depth 7 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.439026847 | 0.433710992 | -0.005315855 | 0.436892735 | -0.002134113 |
| 2 | 0.444053521 | 0.440990968 | -0.003062553 | 0.444066355 | +0.000012834 |
| 3 | 0.443511646 | 0.442857143 | -0.000654503 | 0.442909091 | -0.000602555 |

| Fold | Phase 14 threshold | Threshold weight 2 | Threshold depth 7 |
| --- | ---: | ---: | ---: |
| 1 | 0.203056689 | 0.331399741 | 0.197111771 |
| 2 | 0.220104637 | 0.338300890 | 0.220880536 |
| 3 | 0.209445973 | 0.351041141 | 0.215307776 |

Inner OOF predictions alone select each threshold. Higher thresholds in the weighted model reflect a different score scale and do not themselves indicate quality; these are not new submission thresholds.

| Outcome | Phase 14 | Weight 2 | Depth 7 |
| --- | ---: | ---: | ---: |
| true_positives | 12855 | 12981 | 12958 |
| false_negatives | 10325 | 10199 | 10222 |
| false_positives | 22112 | 22962 | 22607 |
| true_negatives | 217216 | 216366 | 216721 |

Weight 2 has F1 0.439118448 (−0.003036779) and loses all folds. It recovers 126 additional positives and adds 850 FP. Recall rises 0.554573→0.560009 while precision falls 0.367632→0.361155. AP declines 0.000371; unweighted log loss rises to 0.231723 (+0.016498). Weighted loss changes the probability scale toward positives; raw scores are not population-calibrated probabilities. This log-loss interpretation is distinct from lower F1 after inner threshold reselection.

Depth 7 has F1 0.441160950 (−0.000994277). Fold 2 improves only +0.000012834 while the others lose. It recovers 103 additional positives and adds 495 FP, with recall 0.559016 and precision 0.364347. AP +0.000139 and log loss −0.000135 are small secondary gains without an F1 case for the deeper model.

Conditional paired 95% F1 intervals are [−0.004730150, −0.001318961] and [−0.002978237, +0.001004398], using 20,000 resamples, seed 20260929 and fixed fits/thresholds. Weight 2 is negative in every fold and its interval; depth 7's small uncertain change includes zero. Neither includes retraining/repeated-selection uncertainty or proves that every other weight/depth must lose.

CV times are 48.55/63.89 minutes; coordinator duration including final checks is 64.17 minutes. Both start at 01:11 on 1 October 2026, Europe/Rome; weight 2 ends 02:00 and depth 7 02:15. CV excludes preflight/final checks and overlapping resource sharing prevents a controlled sequential speed comparison.

All 144 pre-training tests passed, including six new weighting tests; weight-1 predictions/scores remain identical. Each preflight replays three reference checkpoints exactly. All nine partitions retain baseline features/order/rows/bins. Six candidate outer checkpoints reproduce OOF scores exactly; weights, depths, initial training prevalence, thresholds and metrics are verified. Both processes exit 0, records publish sequentially and executed sources are preserved.

Keep Phase 14, weight 1, depth 5, 200 trees and learning rate 0.05. Neither combination nor new submission is produced. [Phase 32](phase32_mlp_summary.md) subsequently completes the MLP comparison. `HAREHAB1` stays in the final version; official-runtime execution was pending at this phase. The [final audit](../../docs/FINAL_AUDIT.md) records delivery status.

- [Phase 30 record](../experiments/20261001T000013003849Z_phase30-phase14-positive-weight2-depth5-features128-200trees.json).
- [Phase 30 comparison](../experiments/phase30_comparison.json).
- [Phase 31 record](../experiments/20261001T001533065665Z_phase31-phase14-depth7-depth7-features128-200trees.json).
- [Phase 31 comparison](../experiments/phase31_comparison.json).
