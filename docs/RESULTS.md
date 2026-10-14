# Results and interpretation

The final pipeline classifies myocardial infarction or coronary heart disease reported in the BRFSS 2015 survey. It combines codebook-based cleaning, derived dietary frequencies and restricted conditional imputation with a NumPy histogram gradient booster. Recorded AIcrowd feedback is **F1 0.455 and accuracy 0.882**, reported by the author on **13 October 2026** and displayed to three decimal places.

The pipeline was selected because it had the highest displayed F1 among completed candidates with recorded challenge feedback at the **14 October 2026 release**. It is identified in the experiment records as `combined18_24_l2_1` (Combined Phase 18 + Phase 24, leaf L2 = 1). **No completed nested development evaluation is recorded for this exact combination.**

## How the scores were obtained

| Pipeline and protocol | F1 | Interpretation |
| --- | ---: | --- |
| Final combination: three-fold OOF threshold calibration on all labeled rows | 0.443882 | The same pooled labels select the threshold and describe its F1 |
| Final combination: AIcrowd feedback | 0.455 | Author-reported challenge score used in model selection |
| Final combination: nested development evaluation | Unavailable | No completed estimate for this exact pipeline |
| Historical Phase 14: nested development evaluation | 0.442155 | Outer-fold evaluation after inner-fold threshold selection |
| Historical Phase 14: full-training OOF threshold calibration | 0.442770 | Calibration of the earlier pipeline's threshold |
| Historical Phase 14: AIcrowd feedback | 0.452 | Earlier author-reported challenge score |

For the final pipeline, three stratified folds produce out-of-fold (OOF) probabilities for all **328,135 labeled rows**. Each row is predicted by a model fitted without that row; preprocessing, including conditional imputation, is learned within the corresponding training fold. The threshold **0.21811010373987366** maximizes F1 on the pooled OOF probabilities, with accuracy breaking F1 ties. The final model is then fitted on all labeled rows and uses this fixed threshold for test predictions.

This is **decision-threshold calibration**, not a separate probability-calibration step or an independent test. Although each OOF probability comes from a fit that excluded its row, the pooled labels are reused to select and score the threshold. Historical nested scores therefore cannot be assigned to the final combination.

## Challenge feedback and model selection

| Completed pipeline | Displayed F1 | Displayed accuracy |
| --- | ---: | ---: |
| Historical reference (Phase 14) | 0.452 | 0.878 |
| Diet representation (Phase 18) | 0.453 | 0.882 |
| Restricted imputation (Phase 24) | 0.454 | 0.880 |
| Leaf L2 = 5 (Phase 25) | 0.453 | 0.883 |
| **Final combination: diet + restricted imputation, L2 = 1** | **0.455** | **0.882** |
| Diet + restricted imputation, L2 = 5 | 0.453 | 0.883 |

![AIcrowd feedback comparison](../assets/figures/aicrowd_progression.png)

Each candidate uses its own OOF-selected threshold before submission. The final choice follows **displayed challenge F1**, even though other candidates have slightly higher accuracy. Its displayed gain over Phase 14 is **0.003**. Because challenge feedback informed selection and no uncertainty interval is available for this difference, it does not establish a population-level improvement.

Scores were reported by the author on **12–13 October 2026** and rounded to three decimals. The [candidate feedback](../evidence/aicrowd/candidates_feedback_20261013.json) and [combined feedback](../evidence/aicrowd/combined_feedback_20261013.json) preserve the records; direct submission URLs and a screenshot were not supplied.

The author reported **3rd place on 14 October 2026** on the [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards), as recorded in the [release evidence](../evidence/RELEASE_20261014.json). This is a dated, author-reported position, not a final placing. The release record does not independently verify it, and rank is not inferred from F1.

## Historical controlled comparisons

The following results use **262,508 development rows, three outer folds and two inner threshold-selection folds**. Each outer training partition produces inner OOF probabilities to select a threshold; that threshold is then fixed for evaluation on the excluded outer fold. Preprocessing is fitted within every training partition. The table pools the resulting outer-fold predictions.

| Historical pipeline | Nested F1 | Precision | Recall | Average precision |
| --- | ---: | ---: | ---: | ---: |
| Ridge | 0.419508 | 0.333029 | 0.566652 | 0.390283 |
| Earlier logistic regression | 0.425628 | 0.357279 | 0.526316 | 0.387745 |
| Matched logistic, Phase 14 cleaning | 0.434467 | 0.367541 | 0.531191 | 0.420990 |
| **Reference booster (Phase 14)** | **0.442155** | 0.367632 | 0.554573 | 0.428609 |
| Corrected split search (Phase 34) | 0.440803 | 0.362001 | 0.563460 | 0.428781 |
| MLP 64 → 32 | 0.424451 | 0.360722 | 0.515531 | 0.387782 |
| MLP 128 → 64 | 0.419268 | 0.340005 | 0.546721 | 0.379380 |

![Historical development comparison](../assets/figures/model_comparison.png)

Matched logistic regression shares Phase 14's codebook cleaning, source variables and folds. It has its own train-fitted filling, missingness flags, scaling and optimizer, so this compares complete pipelines. The earlier ridge and logistic runs retain their historical median-fill representations.

Phase 14 has higher F1 than matched logistic in all three outer folds. The pooled gain is **0.007689**, with a paired 95% interval of **[+0.004919, +0.010463]**, conditional on the fitted models and selected thresholds. This interval excludes retraining and repeated-selection uncertainty. All nine logistic fits converged; the [study](../project/results/eda/phase38_matched_logistic_summary.md) and [verification record](../project/results/eda/phase38_matched_logistic_verification.json) retain the details.

The individual diet and restricted-imputation variants did not exceed Phase 14 under this historical nested protocol, although their later full-training submissions improved displayed challenge F1. The final combination was selected using challenge feedback. These results do not show that each transformation independently improves generalization.

## Final pipeline details

The final pipeline starts with the historical codebook cleaning, removes six mixed-code raw diet variables and retains the existing derived daily-frequency columns. Restricted conditional imputation learns from training features without using target labels. It fills specified nonresponses and height/weight information while preserving structural blanks and eight original missing-reason flags. The resulting matrix has **289 source variables plus eight flags: 297 transformed columns**, including `HAREHAB1`.

| Setting | Selected value |
| --- | --- |
| Trees / maximum depth | 200 / 5 |
| Learning rate / minimum leaf rows | 0.05 / 200 |
| Bins / candidate features per node | 64 / 128 |
| Leaf L2 / model seed | 1 / 20260920 |
| Final decision threshold | 0.21811010373987366 |
| Labeled rows / test predictions | 328,135 / 109,379 |
| Positive / negative test predictions | 13,999 / 95,380 |

The [final configuration](../project/configs/final_model.json) is the default for `python run.py`. The [preprocessing plan](../project/configs/experiments/combined18_24_preprocessing.json) specifies exclusions and imputation. The [submission record](../project/results/eda/final_combined18_24_submission.json) preserves parameters, calibration, input fingerprints and the submission CSV's SHA-256 hash.

The booster source is byte-identical to the historical Phase 14 implementation. The changed preprocessing and calibrated threshold define a new pipeline; preserving the booster source does not transfer the historical pipeline's evaluation to it.

## Scope and limitations

The target is a reported diagnosis in a cross-sectional survey. `HAREHAB1` concerns rehabilitation after a heart attack and remains included in the final pipeline. Removing it from the **historical** pipeline reduced nested F1 to **0.431039**. That ablation does not measure its effect in the final combination. Its post-event information limits interpretation as prediction before an event; no prospective, clinical, temporal or external-population validation is established.

The frozen booster omits some split candidates that separate observed values from missing responses. Phase 34 evaluates the corrected search separately: nested F1 **0.440803**, with a paired F1 difference interval of **[−0.003005, +0.000319]** versus Phase 14. The final combination uses the historical implementation and does not include that correction.

Development folds and AIcrowd feedback were consulted repeatedly, and early baselines also consulted the original **65,627-row** local validation partition. Threshold nesting reduces optimism from threshold selection; it does not remove optimism from repeated model selection. A new use case needs fresh evaluation data and a feature policy based on what is available when a prediction would be made.

## Evidence and reproduction

The [project guide](../project/README.md) explains how to reproduce the final pipeline, its threshold calibration and the historical evaluations. Official data, checkpoints, row-level OOF predictions and submission CSVs are excluded from Git.

The [release record](../evidence/RELEASE_20261014.json), [metrics](../evidence/METRICS.json), [challenge chart data](../assets/chart_data/aicrowd_progression.csv) and [historical chart data](../assets/chart_data/model_comparison.csv) identify protocols and sources. The [original snapshot manifest](../evidence/SNAPSHOT_MANIFEST.json) is a dated archive; historical experiment outcomes are preserved. The [technical report](../project/docs/FINAL_REPORT.md) provides further methodological detail.

The previous 16-slide [presentation PDF](../presentation/RESULTS_PRESENTATION.pdf) and [editable PowerPoint](../presentation/RESULTS_PRESENTATION.pptx) are being updated. The [presentation draft](../presentation/PRESENTATION_DRAFT.md) provides the revised narrative, per-slide sources and a Claude Design handoff; the published binaries remain the earlier version.
