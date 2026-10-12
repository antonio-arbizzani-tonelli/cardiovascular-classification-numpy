# Phase 20 — exact bins for low-cardinality fields

The isolated candidate holds Phase 14's 295 features, response cleaning, model and splits fixed, adding only `binning_strategy=exact_low_cardinality`. Up to 64 training-observed finite values remain distinct; higher-cardinality fields retain quantile bins. NaNs stay in bin 255. Exact fields also test the all-observed/all-missing boundary so removing empty bins does not lose a previously possible partition; quantile fields keep the historical search.

Evaluation uses 262,508 development rows, three outer and two inner threshold folds. Nine fresh 200-tree fits are compared with verified Phase 14 artifacts. A first run stopped because of logging before its first fit finished; it contributes neither results nor recorded runtime. All 95 pre-training tests passed. Preflight checks all nine training partitions for exact values, unchanged quantile fallback and NaN states; reference replay has maximum difference zero. Real fit bin profiles match preflight; hashes, training rows/labels, OOF fold mappings, nested metrics and three candidate checkpoint outputs are verified. The initial 20% partition is excluded here but was consulted historically.

| Model | F1 | Precision | Recall | AP | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155 | 0.367632 | 0.554573 | 0.428609 | 0.215225 |
| Exact bins | 0.440783 | 0.368551 | 0.548231 | 0.428874 | 0.215222 |

Pooled F1 changes by −0.001372; one of three folds improves.

| Fold | F1 Phase 14 | Candidate F1 | Difference | Phase 14 threshold | Candidate threshold |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.439027 | 0.437242 | -0.001785 | 0.203057 | 0.217115 |
| 2 | 0.444054 | 0.440956 | -0.003097 | 0.220105 | 0.211153 |
| 3 | 0.443512 | 0.444055 | +0.000544 | 0.209446 | 0.210802 |

| Model | TP | FN | FP | TN |
| --- | ---: | ---: | ---: | ---: |
| Phase 14 | 12855 | 10325 | 22112 | 217216 |
| Exact bins | 12708 | 10472 | 21773 | 217555 |

The candidate recovers 327 false negatives, loses 474 true positives, introduces 1,187 false positives and removes 1,526. Its conditional paired 95% F1 interval [−0.003058, +0.000288] uses 20,000 class-stratified resamples, seed 20260929, and fixed fits/thresholds. It excludes training and repeated-selection uncertainty and includes zero.

Completed CV takes 2,523.0 seconds (42.0 minutes), under Python 3.14.3 / NumPy 2.4.2; official Python 3.9 / NumPy 1.23.1 execution is not checked here. Outer fits have 250/251/250 exact columns including constants, recovering distinctions in 79/82/79 columns; inner fits each have 251 exact columns. The matrix remains uint8, but extra boundaries can increase search cost.

Keep Phase 14: the operational criterion is unmet. AP changes +0.000265, log loss −0.000003 and probability correlation is 0.996414. Exploratory thresholds selected on the same outer OOF labels give F1 0.441492 versus control 0.442078; these optimistic figures do not guide the decision. Lost resolution is real, but preserving every eligible field does not improve F1 here. This neither proves overfitting nor rules out targeted gains. A narrower test could preserve binary/few-category fields while retaining original numerical bins. Future indicators must keep both states. No full-data model or submission was produced by this experiment.

- [Candidate record](../experiments/20260930T005323542120Z_phase20-phase14-exact-low-cardinality-depth5-features128-200trees.json).
- [Full comparison](../experiments/phase20_binning_comparison.json).
- [Preflight](phase20_binning_preflight.json).
- [Initial audit](discrete_binning_audit.md).
- [Configuration](../../configs/experiments/phase20_phase14_exact_low_cardinality.json).
