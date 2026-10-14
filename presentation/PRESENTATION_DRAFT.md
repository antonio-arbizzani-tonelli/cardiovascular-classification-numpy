# Presentation draft for Claude Design

The previous [PowerPoint](RESULTS_PRESENTATION.pptx) and [PDF](RESULTS_PRESENTATION.pdf) are being updated. This document is the content and design handoff for their replacement. It does not report new experiments or a new model.

## Recommendation and source baseline

**Rewrite the narrative structure rather than make a small wording update.** The existing deck introduces methods and leaderboard results before explaining the survey problem, repeats result summaries, and puts some evaluation qualifications in small footnotes. Its charts and much of its evidence remain useful. A shorter story with **10 main slides and optional technical appendices** would be easier to follow; there is no requirement to preserve the existing 16-slide structure.

The audience is a Data Scientist or portfolio visitor reading without a presenter. Explain what is being classified before introducing repository phase names. Keep exact configurations and development history in appendices. Qualifications that change the interpretation must remain visible on the relevant slide.

Reviewed on **15 October 2026** against the public default branch main at [d6cbe39a669c61d9f3bbf1da1ac0dc0034c4be94](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/commit/d6cbe39a669c61d9f3bbf1da1ac0dc0034c4be94), together with the documentation corrections in this update. All source paths below are relative to the outer repository root; links resolve from this document. Metrics come from recorded experiments and the 14 October release, not new training.

## Slide 1: Classifying reported cardiovascular conditions

**Essential text**

> Classify whether respondents to the 2015 Behavioral Risk Factor Surveillance System (BRFSS), a U.S. health survey, reported myocardial infarction or coronary heart disease.
>
> The challenge extract contains 328,135 labeled respondents, 321 predictors and 109,379 unlabeled test respondents. Models and preprocessing are implemented with NumPy and the Python standard library.

Identify Antonio Arbizzani Tonelli and the EPFL Machine Learning CS-433 context in a small author line. The course context should not be needed to understand the task.

**Recommended visual:** A simple problem statement with a compact dataset summary. Avoid a clinical-risk illustration or a leaderboard badge on the opening slide.

**Precise sources:** [METRICS.json](../evidence/METRICS.json), dataset fields; [dataset audit](../project/results/eda/dataset_audit.json); [task and provenance](../project/docs/DATA.md#task-and-source).

## Slide 2: An uncommon positive class and substantial missingness

**Essential text**

> Positive labels account for 28,975 of 328,135 training respondents: 8.83%.
>
> 44.79% of raw training predictor cells are blank. Many blanks reflect questionnaire branching rather than a zero quantity.
>
> Predicting every respondent as negative gives 91.17% training accuracy and F1 = 0. F1 guides selection because positive recovery and false positives both matter.

**Recommended visual:** Reuse the prevalence bar from original slide 3, with explicit positive and negative labels. Put missingness beside it as a separate statistic; it has a different denominator. Do not present the all-negative training baseline as an AIcrowd result.

**Precise sources:** [METRICS.json](../evidence/METRICS.json), dataset.positive_fraction, class counts and missing-cell fraction; [dataset audit](../project/results/eda/dataset_audit.json); [data interpretation](../project/docs/DATA.md#measured-properties). The all-negative accuracy is the complement of the recorded positive fraction, rounded to two decimals.

## Slide 3: Response codes need their survey meanings

**Essential text**

> Interpret response codes separately for each variable. A finite number can represent a quantity, a category or a nonresponse.
>
> ALCDAY5 = 888 means no alcohol consumption and becomes 0. PHYSHLTH = 88 means zero physically unhealthy days and becomes 0. Documented unknown or refused codes become NaN.
>
> The historical cleaning audit mapped 1,095,421 nonresponse codes to missing and 899,687 zero-quantity codes to zero, across 262,508 development rows and 295 retained columns.

**Recommended visual:** Reuse the three code-to-meaning examples from original slide 4 as an editable table. Label the counts as historical transformation counts, not evidence of a performance gain. Do not suggest a universal rule for codes such as 7, 9, 88 or 888.

**Precise sources:** [historical cleaning plan](../project/configs/experiments/phase14_codebook_corrections_only.json), preprocessing overrides; [cleaning audit](../project/results/eda/phase33_preprocessing_counts.json), counts and scope; [feature preprocessing](../project/src/feature_preprocessing.py), tree_feature_matrices; [codebook](../project/official_material/project1/brfss_2015_codebook.txt).

## Slide 4: The final representation adds diet exclusions and restricted imputation

**Essential text**

> Start with the historical codebook cleaning. Exclude six raw diet questions that mix daily, weekly and monthly codes, while retaining the existing derived daily-frequency columns.
>
> Fill only specified unknown or refused answers and blank height/weight information. Derive missing BMI from completed height and weight. Imputers learn from training features without disease labels.
>
> Keep questionnaire-branching blanks missing and preserve the original missing-state indicators. The final model receives 289 source columns plus eight flags: 297 transformed features.

**Recommended visual:** Two clearly labeled preprocessing changes converging on the final feature matrix, adapted from original slide 5. Show that imputation is fitted within each training partition. Do not depict all missing values as filled, or imply that the daily-frequency columns are newly calculated by this pipeline.

**Precise sources:** [selected configuration](../project/configs/final_model.json), preprocessing; [combined plan](../project/configs/experiments/combined18_24_preprocessing.json), variants[0].preprocessing; [conditional imputation](../project/src/conditional_imputation.py), impute_tree_pair; [final representation guide](../project/docs/DATA.md#selected-final-representation-diet-exclusions-and-restricted-imputation).

## Slide 5: Histogram gradient boosting in NumPy

**Essential text**

> Learn up to 64 quantile bins per feature from training rows. Fit trees using Newton updates on logistic loss, and add their outputs with learning rate 0.05.
>
> The selected booster uses 200 trees with maximum depth 5. Splits learn which branch receives missing responses. A respondent is classified positive when the predicted probability is at or above the saved threshold.
>
> The final pipeline uses the preserved historical booster source. It retains an audited omission of some observed-versus-missing split candidates; the corrected search was evaluated separately.

**Recommended visual:** Adapt the bin / fit / sum / decide flow from original slide 6. Use "up to 64 bins" and p >= threshold. Keep the source limitation as a short visible qualification; move the remaining parameters to Appendix A.

**Precise sources:** [frozen booster](../project/src/numpy_boosting_phase14.py), HistogramBinner, _NewtonTree and HistogramGradientBoostingClassifier; [selected parameters](../project/configs/final_model.json), model, implementation and source hash; [split-search audit](../project/docs/FINAL_REPORT.md#split-search-comparison-phase-34); [corrected comparison](../project/results/eda/phase34_missing_only_split_summary.md).

## Slide 6: The historical booster outperformed a matched logistic pipeline

**Essential text**

> Historical nested development F1: 0.442155 for the reference booster and 0.434467 for matched logistic regression, a difference of +0.007689.
>
> Both use the same cleaning, 295 source variables, development rows and folds. Logistic regression has its own fitted filling, scaling and missingness flags, so the comparison evaluates complete pipelines.
>
> The booster has higher F1 in all three outer folds. The paired 95% interval is [+0.004919, +0.010463], conditional on the fitted models and thresholds. It excludes retraining and repeated-selection uncertainty.

**Recommended visual:** Reuse the historical F1 bars from original slide 8 or the [model comparison SVG](../assets/figures/model_comparison.svg). Label the metric and axis explicitly. Emphasize the matched comparison and put the full model table in an appendix. State visibly that this comparison does not evaluate the final combined pipeline.

**Precise sources:** [chart data](../assets/chart_data/model_comparison.csv), Phase 14 reference and Matched logistic regression rows; [matched study](../project/results/eda/phase38_matched_logistic_summary.md), shared inputs, nested results and paired interval; [verification](../project/results/eda/phase38_matched_logistic_verification.json).

## Slide 7: Evaluation and threshold calibration answer different questions

**Essential text**

> Historical nested evaluation uses 262,508 development rows, three outer folds and two inner folds. Each threshold is selected from inner out-of-fold probabilities, then fixed before the excluded outer fold is scored.
>
> For final decision-threshold calibration, three new stratified folds produce out-of-fold (OOF) probabilities covering all 328,135 labeled rows. The threshold maximizes F1 on pooled OOF probabilities, with accuracy breaking F1 ties. The final fit then uses all labeled rows and applies the fixed threshold.
>
> Each fit learns preprocessing from its training partition. The same pooled labels select and describe the final threshold, so calibration F1 is not an independent test score. This is threshold calibration, not a separate probability-calibration model.

Display these distinctions in a compact table:

| Pipeline and protocol | Recorded F1 | Interpretation |
| --- | ---: | --- |
| Historical Phase 14, nested development | 0.442155 | Earlier pipeline evaluated on excluded outer folds |
| Final combination, OOF threshold calibration | 0.443882 | Same labels select and score the threshold |
| Final combination, AIcrowd feedback | 0.455 | Author-reported challenge feedback used in selection |
| Final combination, nested development | Unavailable | No completed estimate for this exact pipeline |

**Recommended visual:** Two protocol lanes or a simple fold diagram, followed by the table. Avoid an ascending score chart: the values are not successive improvements under one protocol. Split this into protocol and interpretation slides if needed, rather than shrink the qualifications.

**Precise sources:** [historical nested suite](../project/configs/experiments/final_phase14_validation.json); [historical result](../project/results/experiments/20260921T105139261213Z_phase14-boosting-codebook-corrections-only-depth5-features128-200trees.json), outcome.nested_threshold_evaluation; [final submission record](../project/results/eda/final_combined18_24_submission.json), threshold, calibration_metrics and nested status; [selected configuration](../project/configs/final_model.json), threshold_source and validation.

## Slide 8: Challenge feedback selected the final combination

**Essential text**

> The final combination was selected for the highest displayed AIcrowd F1 among completed candidates with recorded feedback at the 14 October 2026 release. Each candidate has its own OOF-selected threshold.
>
> The final combination records F1 0.455 and accuracy 0.882. The displayed F1 difference from the historical submission is +0.003. Repeated challenge feedback informed selection; this rounded difference does not establish a statistically reliable improvement.

| Completed candidate | Displayed F1 | Displayed accuracy |
| --- | ---: | ---: |
| Historical reference | 0.452 | 0.878 |
| Diet representation only | 0.453 | 0.882 |
| Restricted imputation only | 0.454 | 0.880 |
| Leaf L2 = 5 only | 0.453 | 0.883 |
| **Diet + restricted imputation, L2 = 1 (selected)** | **0.455** | **0.882** |
| Diet + restricted imputation, L2 = 5 | 0.453 | 0.883 |

**Recommended visual:** Reuse the candidate table from original slide 11, or rebuild from its CSV. Label individual variants as "only," rather than ambiguous sequential "+" additions. F1 decides the choice, even when another candidate has higher accuracy. A bar chart must not imply a controlled causal progression.

**Visible source note:** Author-reported AIcrowd display scores, rounded to three decimals. Historical reference reported on 12 October 2026; other candidates on 13 October 2026. Direct submission URLs and screenshots were not supplied.

**Precise sources:** [challenge chart data](../assets/chart_data/aicrowd_progression.csv); [individual feedback](../evidence/aicrowd/candidates_feedback_20261013.json), variant-specific scores and CSV hashes; [combined feedback](../evidence/aicrowd/combined_feedback_20261013.json), both combined variants; [selected record](../project/results/eda/final_combined18_24_submission.json), selection_reason and selection_limits.

## Slide 9: Post-event information limits the interpretation

**Essential text**

> HAREHAB1 asks about rehabilitation after a heart attack and remains in the final pipeline. All 620 development respondents with a recorded response are positive.
>
> Removing this feature from the historical pipeline reduced nested F1 from 0.442155 to 0.431039. This ablation does not measure its effect in the final combination.
>
> The project classifies reported disease in a survey. It does not demonstrate prospective clinical prediction, and no temporal or external-population validation is established. Development folds and challenge feedback were consulted repeatedly, so neither threshold nesting nor the challenge score removes model-selection optimism.

**Recommended visual:** Adapt the post-event relationship from original slide 13. Label rehabilitation as information collected after the event, with the historical ablation as a separate annotation. Do not suggest a deployed clinical tool or move these limits to notes alone.

**Precise sources:** [feature metadata](../project/configs/feature_metadata.json), HAREHAB1; [METRICS.json](../evidence/METRICS.json), temporal_proxy and evaluation.limits; [historical ablation](../project/results/experiments/20260921T154905753681Z_phase15-boosting-ablate-harehab1-depth5-features128-200trees.json); [technical interpretation](../project/docs/FINAL_REPORT.md#harehab1).

## Slide 10: Reproduction and dated release evidence

**Essential text**

> Run commands from project/ after installing the documented environment and obtaining the official challenge CSVs. The entry point fits all labeled rows and uses the threshold already stored in the selected configuration.
>
> The recorded final submission contains 109,379 predictions: 13,999 positive and 95,380 negative. These are prediction counts, not classification errors.
>
> The repository provides configurations, aggregate experiment records and reproduction guides. Official data, model checkpoints and row-level predictions remain outside Git.

Use one complete command:

~~~bash
python run.py --data-dir data/raw/dataset --output submission.csv
~~~

Guide paths such as docs/RESULTS.md and project/README.md start at the outer repository root. If verification is mentioned, date it: the release record reports 242 synthetic project tests and exact selected-prediction replay on 14 October 2026; these are not new training results.

**Optional final detail:** "The author reported 3rd place on the AIcrowd leaderboard on 14 October 2026. This dated snapshot is not independently verified and is not a final placing." Keep this secondary to the methods and evaluation limits.

**Recommended visual:** A short reproduction block with links to the guides and selected record. Avoid oversized rank or score cards. Keep commands on complete lines or use explicit shell continuation syntax.

**Precise sources:** [project guide](../project/README.md); [entry point](../project/run.py), run_pipeline; [selected record](../project/results/eda/final_combined18_24_submission.json), prediction counts; [release evidence](../evidence/RELEASE_20261014.json), dated rank provenance; [verification](../evidence/VERIFICATION.json), project_tests and selected_replay; [leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards), context rather than independent proof of the historical rank.

## Optional technical appendices

### Appendix A: Selected recipe and threshold

**Essential text:** Identifier combined18_24_l2_1; 289 retained source variables plus eight original missing-state flags; 200 trees; depth 5; learning rate 0.05; minimum leaf rows 200; up to 64 bins; 128 candidate features per node; leaf L2 = 1; model seed 20260920. The final threshold is **0.21811010373987366**, selected from pooled three-fold full-training OOF probabilities with fold seed 20260919 and accuracy breaking F1 ties.

**Recommended visual:** An editable parameter table adapted from original slide 15. Explain the historical Phase 14 source and the two later preprocessing changes here; do not use phase labels as the opening story.

**Precise sources:** [final configuration](../project/configs/final_model.json), model and threshold_source; [combined preprocessing](../project/configs/experiments/combined18_24_preprocessing.json); [selected record](../project/results/eda/final_combined18_24_submission.json), threshold and implementation hash.

### Appendix B: Historical comparisons and uncertainty

**Essential text:** The full comparison covers ridge, earlier logistic, matched logistic, the historical booster, corrected split search and two MLP architectures. Display the linked CSV's metrics to six decimals and define AP as average precision. All rows describe historical nested pipelines, not the final combination.

The raw-input benchmark gives F1 0.441457 versus 0.442155 after cleaning and exclusions: difference +0.000698, with paired 95% interval [-0.001226, +0.002635]. It combines recoding and exclusions and conditions on fixed fits and thresholds. Corrected split search gives nested F1 0.440803; its paired difference interval versus the historical booster is [-0.003005, +0.000319]. The final pipeline retains the historical search implementation.

**Recommended visual:** The complete historical metrics table from original slide 16 and, if needed, the raw-versus-cleaned interval from original slide 10. Split into two appendix slides if both are retained. The intervals exclude retraining and repeated model selection.

**Precise sources:** [historical chart data](../assets/chart_data/model_comparison.csv); [raw-input comparison](../project/results/eda/phase33_raw_preprocessing_summary.md); [corrected-search comparison](../project/results/eda/phase34_missing_only_split_summary.md); [METRICS.json](../evidence/METRICS.json), preprocessing, phase34 and matched_logistic_comparison.

### Appendix C: Historical classification errors

**Essential text:** Historical nested development decisions contain 12,855 true positives, 10,325 false negatives, 22,112 false positives and 217,216 true negatives. Precision is 0.367632 and recall 0.554573. These decisions belong to the historical reference, not an independent evaluation of the final model.

**Recommended visual:** Rebuild the confusion matrix from original slide 12. Put actual classes to the left aligned with their rows and predicted classes above the columns; the original placement of actual-class labels is confusing. Final test prediction counts must not be used as confusion-matrix counts.

**Precise source:** [METRICS.json](../evidence/METRICS.json), model_results entry Phase 14 reference, confusion_counts and metrics.

## Reusable visuals from the existing presentation

Slide numbers below refer to the unchanged previous deck, not the proposed sequence.

| Previous slide | Reusable material | Source and required adjustment |
| --- | --- | --- |
| 3 | Prevalence bar and dataset counts | dataset in [METRICS.json](../evidence/METRICS.json); distinguish row prevalence from missing-cell fraction |
| 4 | Survey-code examples and cleaning counts | [preprocessing counts](../project/results/eda/phase33_preprocessing_counts.json); preserve historical scope |
| 5 | Diet and restricted-imputation changes | [combined plan](../project/configs/experiments/combined18_24_preprocessing.json); preserve structural blanks and training-only fitting |
| 6 | Bin / fit / sum / decide flow | [frozen source](../project/src/numpy_boosting_phase14.py); correct "64 bins" to "up to 64" and "above" to "at or above" |
| 7 | Separate score-protocol comparison | [selected record](../project/results/eda/final_combined18_24_submission.json); define OOF and show final nested evaluation as unavailable |
| 8 | Historical F1 bars | [SVG](../assets/figures/model_comparison.svg), [PNG](../assets/figures/model_comparison.png), [CSV](../assets/chart_data/model_comparison.csv); retain historical labels and complete-pipeline qualification |
| 10 | Raw-versus-cleaned paired interval | [study](../project/results/eda/phase33_raw_preprocessing_summary.md); label joint cleaning/exclusion effect and conditional interval |
| 11 | Challenge candidate table | [SVG](../assets/figures/aicrowd_progression.svg), [PNG](../assets/figures/aicrowd_progression.png), [CSV](../assets/chart_data/aicrowd_progression.csv); keep candidate identities and dated author-reported provenance |
| 12 | Historical confusion counts | [METRICS.json](../evidence/METRICS.json); recreate labels rather than copy their original placement |
| 13 | Post-event relationship and historical ablation | [HAREHAB1 analysis](../project/docs/FINAL_REPORT.md#harehab1); keep the clinical-validity limit visible |
| 15-16 | Configuration and full metrics tables | [selected configuration](../project/configs/final_model.json) and [historical CSV](../assets/chart_data/model_comparison.csv); keep as appendices and use complete command lines |

The two existing figure files are useful references, with their CSVs as the authority for values and protocols. Rebuilding them as editable charts is preferable when changing labels or emphasis. Use English decimal points, explicit axes and consistent precision. Do not reuse the opening rank/KPI cards or summary grid as the new introduction.

## Ready-to-use prompt for Claude Design

Attach this draft, the existing PPTX/PDF, and the two chart CSVs and figure files if Claude Design cannot access repository links. Then use:

~~~text
Create a self-contained English portfolio presentation from the attached PRESENTATION_DRAFT.md. The audience is a Data Scientist or portfolio visitor reading without a presenter. Rewrite the structure around its proposed narrative rather than restyling the old opening. Use about 10 main slides, splitting a dense slide when useful, with optional technical appendices. Do not preserve 16 slides as a constraint.

Open with the BRFSS 2015 survey problem and dataset. Then explain class imbalance and missingness, response-code cleaning, the final diet/imputation representation, histogram gradient boosting in NumPy, the matched historical baseline comparison, evaluation protocols, challenge selection and limitations. Put phase names, exact configurations and expanded tables in appendices.

Treat the draft and linked records as the factual authority. The final pipeline has author-reported AIcrowd F1 0.455 and accuracy 0.882. Its full-training OOF threshold-calibration F1 is 0.443882, using the same pooled labels to select and score the threshold. Historical Phase 14 nested F1 0.442155 does not evaluate the final combination. No completed nested estimate exists for the exact final pipeline. Show these boundaries visibly, not only in notes.

Explain threshold selection and model selection separately. The threshold maximizes pooled three-fold OOF F1 over all labeled rows, with accuracy breaking ties. The final pipeline was selected using repeated AIcrowd feedback and the highest displayed F1 among completed candidates with recorded feedback. The displayed +0.003 over the historical submission is not a significance result. Preserve the dated author-reported provenance and three-decimal precision of challenge scores.

Keep HAREHAB1 visible as a post-heart-attack rehabilitation variable retained in the final model. Attribute its ablation only to the historical pipeline. Describe survey classification without suggesting prospective clinical prediction. Preserve the historical split-search limitation and separately evaluated correction.

Use a restrained layout, readable typography and editable evidence charts/tables. Reuse or rebuild only visuals identified in the draft, using their cited data. Label axes and protocols clearly, use English decimal points, and keep uncertainty qualifications beside the relevant comparison. Avoid promotional language, clinical-risk imagery and leaderboard badges. Include rank only as an optional final detail: 3rd on 14 October 2026, reported by the author, not independently verified and not a final placing.

Give each slide a clear title, concise essential copy and a visible source note. Keep full source paths or links in notes as well. Commands must remain complete and identify project/ as the working directory. Guide paths are relative to the outer repository root. Do not invent results, error bars, sources or claims. If a source is unavailable, retain the documented value and flag the missing source rather than infer new evidence. Provide an editable presentation and a matching PDF.
~~~
