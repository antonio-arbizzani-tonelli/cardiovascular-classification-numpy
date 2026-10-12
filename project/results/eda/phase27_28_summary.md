# Phases 27–28 — matched comparisons with Phase 14

Both candidates are complete and verified. Neither achieves higher pooled F1 and improvement in at least two folds. Phase 27 changes only learning rate 0.05→0.025 and trees 200→400, keeping 295 features. Phase 28 removes only `ALCDAY5`, retaining `DROCDY3_` and all original parameters, with 294 features. Their combination is not tested.

The same 262,508 development rows, splits and seeds use three outer and two inner threshold folds: 18 fresh fits in total, against reused verified reference artifacts.

| Metric | Phase 14 | Phase 27 | Phase 28 |
| --- | ---: | ---: | ---: |
| f1 | 0.442155227 | 0.440587222 | 0.440535142 |
| precision | 0.367632339 | 0.364261750 | 0.360563845 |
| recall | 0.554572908 | 0.557377049 | 0.566091458 |
| average_precision | 0.428609250 | 0.429352055 | 0.429039626 |
| log_loss | 0.215225071 | 0.215123329 | 0.215250685 |

| Fold | F1 Phase 14 | F1 Phase 27 | Delta 27 | F1 Phase 28 | Delta 28 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.439026847 | 0.435906570 | -0.003120278 | 0.435323752 | -0.003703096 |
| 2 | 0.444053521 | 0.443457606 | -0.000595915 | 0.441648634 | -0.002404887 |
| 3 | 0.443511646 | 0.442440913 | -0.001070733 | 0.444821383 | +0.001309737 |

| Fold | Phase 14 threshold | Threshold Phase 27 | Threshold Phase 28 |
| --- | ---: | ---: | ---: |
| 1 | 0.203056689 | 0.206211866 | 0.198075855 |
| 2 | 0.220104637 | 0.210838301 | 0.205198772 |
| 3 | 0.209445973 | 0.208149784 | 0.209596383 |

Thresholds are selected only on inner OOF predictions. Each outer fold uses its own selected threshold; these are not new submission thresholds.

Phase 27 has F1 0.440587222 (−0.001568005) and no improved folds. It adds 65 TP and 437 FP. Slight recall/AP gains and lower log loss do not improve F1; 400 trees are unsupported by this comparison. Phase 28 has F1 0.440535142 (−0.001620086) and one improved fold, adding 267 TP and 1,159 FP. Recall rises but precision falls enough to worsen F1. Retain `ALCDAY5`; this is a full-pipeline ablation including feature sampling and new thresholds, not proof of causal feature value.

Conditional paired F1 intervals are [−0.003124704, −0.000038643] for Phase 27 and [−0.003295025, +0.000067219] for Phase 28, using 20,000 resamples, seed 20260929 and fixed fits/thresholds. Phase 27's upper bound is close to zero; Phase 28 includes zero. Neither interval covers retraining or repeated development selection. These tests support keeping the reference, not claiming that every nearby variant must lose.

CV takes 111.01/57.84 minutes; coordinator time including final verification is 111.50 minutes, excluding CV preflights. Both start at 22:22 on 30 September 2026; Phase 28 finishes at 23:20 that day and Phase 27 at 00:13 on 1 October, Europe/Rome. Resource sharing during the overlap prevents a controlled sequential speed comparison.

All 124 existing tests passed before training; configuration checks reject eight unintended changes. Preflight covers nine partitions per candidate. Three candidate checkpoints each replay OOF probabilities exactly; rows/hashes match and inner OOF artifacts reconstruct thresholds/metrics. Both runners exit 0; records are published sequentially to the shared registry. No retraining is needed for verification.

Keep Phase 14, learning rate 0.05, 200 trees, L2 1, seed 20260920 and `ALCDAY5`. No new submission or combined variant was produced. Official-runtime compatibility was pending at this phase.

- [Phase 27 record](../experiments/20260930T221319968519Z_phase27-phase14-lr0025-400trees-depth5-features128-400trees.json).
- [Phase 27 comparison](../experiments/phase27_comparison.json).
- [Phase 28 record](../experiments/20260930T212010451103Z_phase28-phase14-ablate-alcday5-depth5-features128-200trees.json).
- [Phase 28 comparison](../experiments/phase28_comparison.json).
