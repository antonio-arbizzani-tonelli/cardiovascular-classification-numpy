# Results and interpretation

The selected NumPy histogram booster achieves **nested development F1 0.442155**, an absolute gain of **0.016527** over historical logistic regression on the same development rows and outer folds. The historical academic submission record reports **AIcrowd F1 0.452 and accuracy 0.878**.

Developed for EPFL Machine Learning CS-433, the project combines NumPy model implementation, controlled experiments and result analysis. The experiment records retain the provenance of the academic challenge feedback.

**Ranked 7th on the AIcrowd leaderboard.** Position reported by the author, 12 Oct 2026: [current leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). This records a current position, not a final placing.

## Comparable development results

| Model | F1 | Precision | Recall | Average precision |
| --- | ---: | ---: | ---: | ---: |
| Historical ridge | 0.419508 | 0.33303 | 0.56665 | 0.39028 |
| Historical logistic regression | 0.425628 | 0.35728 | 0.52632 | 0.38775 |
| Selected Phase 14 booster | **0.442155** | 0.367632 | 0.554573 | 0.428609 |
| Corrected Phase 34 booster | 0.440803 | 0.362001 | 0.563460 | 0.428781 |
| MLP 64 → 32 | 0.424451 | 0.360722 | 0.515531 | 0.387782 |
| MLP 128 → 64 | 0.419268 | 0.340005 | 0.546721 | 0.379380 |

The comparisons use 262,508 development rows, three outer folds and thresholds selected using two inner folds. Preprocessing is fitted within the training partition of each fit. Linear-model results use the historical median-fill representation. These are historical pipeline comparisons; they do not isolate model architecture from preprocessing.

![Development comparison](../assets/figures/model_comparison.png)

The selected booster recovers 12,855 of 23,180 development positives and produces 22,112 false positives. Its three fold F1 scores are 0.439027, 0.444054 and 0.443512. These describe performance on this split, not uncertainty over future populations.

## Three score protocols

| Protocol | F1 | Interpretation |
| --- | ---: | --- |
| Nested development evaluation | 0.442155 | Threshold selected in inner folds and evaluated on excluded outer folds |
| Full-train three-fold OOF calibration | 0.442770 | The same OOF labels select and describe the final threshold |
| AIcrowd feedback | 0.452 | Team-reported displayed score preserved in the historical academic submission record; direct submission URL is unavailable |

The final threshold is **0.2106169795070252**. The full-data run generates 109,379 predictions, including 14,746 positives. The [submission record](../project/results/eda/final_phase14_submission.json) records configuration, input hashes, CSV fingerprint and feedback provenance.

## Decisions supported by experiments

The MLPs underperform the selected booster in all three outer folds. Tested representation changes, imputation, class weighting, feature selection and undersampling also fail to exceed the selected nested F1. These are results of the configurations tested, rather than evidence that those methods cannot work on tabular data.

The raw-versus-cleaned benchmark holds the historical booster and folds fixed: F1 moves from 0.441457 to 0.442155. Its paired 95% interval for the difference, **[−0.001226, +0.002635]**, includes zero and is conditional on fixed fits and thresholds. Cleaning improves the meaning of the representation; the measured performance gain is small and uncertain.

## Scope and limitations

`HAREHAB1` records rehabilitation after a heart attack. All 620 development respondents with a recorded code are positive. Removing the feature in the historical ablation reduces F1 to **0.431039**. Its presence is useful for classifying a reported diagnosis but limits interpretation as prediction before an event.

An audit found omitted candidates separating observed values from missing responses. The historical Phase 14 source is frozen for submission reproduction; Phase 34 implements the correction. Under the same nested protocol, corrected F1 is 0.440803 while AP rises slightly to 0.428781. The paired F1 difference interval **[−0.003005, +0.000319]** includes zero. A correction can be appropriate without improving the chosen metric on this dataset.

AIcrowd feedback contributed to the final choice between the two submitted versions. The selected challenge score should therefore be described as competition feedback used in selection. No prospective, clinical, temporal or external-population validation is established.

## Evidence

The [GitHub repository](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy) contains the [machine-readable summary](../evidence/METRICS.json) and [chart data](../assets/chart_data/model_comparison.csv), linked to recorded experiments. The [technical results](../project/docs/FINAL_REPORT.md) provide the full comparison, and the [experiment archive](../project/docs/EXPERIMENTS.md) retains the study history. Numerical outcomes are preserved. Four historical hypothesis annotations and the imputation decision table are translated into English; the [snapshot manifest](../evidence/SNAPSHOT_MANIFEST.json) records original and copied fingerprints, and the ledger hashes identify the copied records.
