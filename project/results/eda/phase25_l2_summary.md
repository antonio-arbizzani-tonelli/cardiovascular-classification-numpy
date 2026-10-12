# Phase 25 — leaf L2 from 1 to 5

Only `l2_regularization` changes from 1 to 5. Phase 14 retains 295 features including `HAREHAB1`, codebook cleaning, quantile bins and tree-handled NaNs. Parameters stay 200 trees, depth 5, learning rate 0.05, minimum leaf 200, 64 bins, 128 candidates and seed 20260920. All 262,508 development rows use outer seed 20260919 and two inner folds per outer fold, seeded 20260922 plus fold. Nine new candidate fits select thresholds only from inner OOF scores; verified Phase 14 artifacts are reused without retraining.

| Metric | Phase 14 | L2=5 | Difference |
| --- | ---: | ---: | ---: |
| f1 | 0.442155227 | 0.441393484 | -0.000761743 |
| precision | 0.367632339 | 0.362086120 | -0.005546219 |
| recall | 0.554572908 | 0.565185505 | +0.010612597 |
| average_precision | 0.428609250 | 0.429316126 | +0.000706876 |
| log_loss | 0.215225071 | 0.215175679 | -0.000049392 |

| Fold | F1 Phase 14 | F1 L2=5 | Delta | Phase 14 threshold | L2=5 threshold |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.439026847 | 0.437774746 | -0.001252101 | 0.203056689 | 0.203773579 |
| 2 | 0.444053521 | 0.441669145 | -0.002384376 | 0.220104637 | 0.199948567 |
| 3 | 0.443511646 | 0.444799670 | +0.001288024 | 0.209445973 | 0.210708616 |

| Outcome | Phase 14 | L2=5 | Difference |
| --- | ---: | ---: | ---: |
| true_positives | 12855 | 13101 | +246 |
| false_negatives | 10325 | 10079 | -246 |
| false_positives | 22112 | 23081 | +969 |
| true_negatives | 217216 | 216247 | -969 |

Pooled F1 changes −0.000761743; only one of three folds improves, failing the higher-F1/two-fold rule. L2 5 is rejected. The historical reference at this phase remains L2 1 with submission threshold 0.2108690997; current full-train OOF calibration later supersedes that threshold.

The candidate recovers 246 additional positives and adds 969 false positives: recall rises 0.010613, precision falls 0.005546 and net F1 declines. AP/log loss improve slightly without an F1 benefit. The conditional paired 95% F1 interval [−0.002479661, +0.000965945] uses 20,000 resamples and seed 20260929, holding fits/thresholds fixed and excluding retraining/repeated selection. It includes zero, so the observed decrease is not proof of certain population inferiority.

Exploratory outer-OOF threshold selection gives F1 0.442325175 versus 0.442077861, a +0.000247 advantage that disappears under inner threshold selection. The decision uses nested scores.

All 113 pre-training tests passed, including rejection of additional preprocessing, seed, threshold or parameter changes. Nine-partition preflight verifies input hashes and exact reference replay. Candidate L2 values, feature order and training rows/labels are checked; three candidate checkpoints reproduce outer OOF predictions exactly. Inner OOF row/fold/hash artifacts reproduce thresholds and metrics. Sources/configurations are frozen during testing.

Nine fits take 49.40 minutes excluding preflight/final checks, under Python 3.14.3 / NumPy 2.4.2; official Python 3.9 / NumPy 1.23.1 execution was pending. Initial 20% validation is excluded here but was used historically; repeated development selection also limits estimates. No new submission was generated.

- [Record](../experiments/20260930T130145988120Z_phase25-phase14-l2-5-depth5-features128-200trees.json).
- [Comparison](../experiments/phase25_l2_comparison.json).
- [Preflight](phase25_l2_preflight.json).
- Checkpoints, outer/inner OOF, helper version and logs: results/boosting_artifacts/phase25_phase14_l2_5/.

[Phase 26](phase26_two_seeds_summary.md) later rejected both a second seed and uniform two-seed averaging on L2 1. This phase's L2 5 inner OOF predictions do not replace missing historical L2 1 artifacts. Earlier artifacts remain preserved; no commit/push occurred in this activity.
