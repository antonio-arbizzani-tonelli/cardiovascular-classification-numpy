# BRFSS classification: technical results

These notes document the EPFL Machine Learning CS-433 project: dataset understanding, NumPy implementation, validation, experiments and result interpretation. The [portfolio overview](../../README.md) provides the concise story; this document retains the methods and evidence behind it. The filename is retained for compatibility with historical documentation. The course-delivery report is archived outside the public package.

The selected release model is **combined18_24_l2_1 NumPy histogram gradient boosting**, with 297 transformed features and the frozen implementation in [src/numpy_boosting_phase14.py](../src/numpy_boosting_phase14.py). It combines the Phase 18 diet representation with restricted Phase 24 feature-only imputation, retaining leaf L2=1. Recorded AIcrowd feedback is **F1 0.455 and accuracy 0.882** on 13 October 2026, displayed to three decimals and reported by the project author. The author reports **3rd place on 14 October 2026**, a dated current leaderboard position. Full-training OOF calibration F1 is **0.443882381**; no completed nested development evaluation exists for this combined model.

The historical Phase 14 baseline has nested development F1 **0.442155**, full-training calibration F1 **0.442770**, and AIcrowd feedback **F1 0.452 / accuracy 0.878** on 12 October 2026. The separate corrected Phase 34 comparison reaches development F1 0.440803. Historical validation, selected threshold calibration and AIcrowd feedback are distinct protocols. No numerical official Phase 34 score was provided.

This portfolio copy preserves experiment numeric outcomes. Four historical annotations were translated with updated copy hashes. At the portfolio root, `evidence/SNAPSHOT_MANIFEST.json` records original source-commit provenance and keeps the original course project distinct from the portfolio.

## Data and preprocessing

Codebook cleaning is part of the selected pipeline: it guides exclusions, distinguishes valid codes from nonresponses and preserves the difference between missing values and zero quantities. Later negative experiments change this already-cleaned representation and do not independently measure the contribution of initial cleaning.

The `_MICHD` target identifies myocardial infarction or coronary heart disease reported in BRFSS 2015. The dataset contains 328,135 labeled respondents, 321 predictors and 109,379 test rows. Positives account for 8.83% of training labels; 44.79% of predictor cells are missing.

Historical Phase 14 preprocessing retains 295 features, excluding identifiers, full interview date, survey-design variables and some redundant columns. Documented nonresponses become `NaN`; codes representing zero quantities become zero. For example, `ALCDAY5=888` means no alcohol consumption and `PHYSHLTH=88` means zero days. Binary recoding is fitted on training rows.

The selected combination excludes the six mixed-unit raw diet columns `FRUITJU1`, `FRUIT1`, `FVBEANS`, `FVGREEN`, `FVORANG` and `VEGETAB1`, retaining the existing CDC daily-frequency columns. This leaves 289 source features. Restricted imputation fills documented unknown/refused codes for `INCOME2`, `PNEUVAC3` and `EMPLOY1`, blank height/weight, and missing BMI derived from height/weight. It learns only from the corresponding training partition, without target labels, and preserves structural blanks and eight original missing-reason flags. The model therefore receives **297 transformed columns**. The exact plan is in [combined preprocessing](../configs/experiments/combined18_24_preprocessing.json).

Across the 295 development columns, cleaning changes 1,095,421 numeric nonresponse codes to `NaN` and 899,687 zero-quantity codes to zero. These [counts](../results/eda/phase33_preprocessing_counts.json) quantify the representation work.

The [complete raw-input benchmark](../results/eda/phase33_raw_preprocessing_summary.md), run before the algorithm correction, holds model and folds fixed and retains all 321 predictors, original numeric codes and `NaN` values. Raw F1 is **0.441457**, versus **0.442155** after cleaning: **+0.000698**, with a small advantage in each fold. The paired 95% interval for cleaned minus raw is **[−0.001226, +0.002635]**, conditional on fixed fits and thresholds, and includes zero. The gain is small and uncertain. This comparison combines recoding and exclusions, with 128 candidate features drawn from 321 or 295 columns; individual operations remain to be isolated.

Phase 14 fixes fourteen gaps in parsed nonresponse meanings. The booster learns quantile bins on training data and chooses the missing-value branch at each split. Its historical input contains 295 source columns; nominal activities and mixed-unit frequencies retain that earlier numeric encoding. The plan is in [Phase 14 preprocessing](../configs/experiments/phase14_codebook_corrections_only.json). The selected combination uses the same cleaning foundation with the diet exclusions and imputation described above.

## Model and evaluation

The booster adds Newton trees to minimize logistic loss. The [final configuration](../configs/final_model.json) specifies:

| Parameter | Value |
| --- | ---: |
| Trees / maximum depth | 200 / 5 |
| Learning rate / minimum leaf rows | 0.05 / 200 |
| Bins / candidate features per node | 64 / 128 |
| Leaf L2 / positive-class weight | 1 / 1 |
| Model seed | 20260920 |
| Final threshold | 0.21811010373987366 |

Historical nested comparisons use the same 262,508 development rows and three outer folds. Two inner folds select an F1 threshold within each outer training partition; the outer held-out fold evaluates the model once. Every fit learns preprocessing and statistics on its own training rows. Development F1 pools predictions using each fold's selected threshold. The selected combined pipeline has completed full-training calibration and AIcrowd submissions, but is absent from this nested comparison table.

For the final submission, three new stratified folds cover all 328,135 labeled rows. Each fold fits preprocessing and the booster on training rows; the final threshold maximizes F1 on pooled OOF predictions without test labels. Calibration F1 uses the labels that selected that threshold and is not an independent evaluation.

F1 balances positive recovery and false alarms. With this imbalance, predicting every row negative gives 91.17% accuracy and F1 zero.

| Model | F1 | Precision | Recall | Average precision | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical ridge | 0.419508 | 0.33303 | 0.56665 | 0.39028 | 0.22917 |
| Historical logistic regression | 0.425628 | 0.35728 | 0.52632 | 0.38775 | 0.22198 |
| Matched logistic, Phase 14 cleaning | 0.434467 | 0.367541 | 0.531191 | 0.420990 | 0.218147 |
| Booster on 321 raw predictors | 0.441457 | 0.366631 | 0.554659 | 0.427835 | 0.215348 |
| **Historical Phase 14 booster** | **0.442155** | **0.367632** | **0.554573** | **0.428609** | **0.215225** |
| Phase 34 booster, corrected search | 0.440803 | 0.362001 | 0.563460 | 0.428781 | 0.215229 |
| MLP 64 → 32 | 0.424451 | 0.360722 | 0.515531 | 0.387782 | 0.221674 |
| MLP 128 → 64 | 0.419268 | 0.340005 | 0.546721 | 0.379380 | 0.222710 |

Historical ridge and logistic scores come from median-fill runs before categorical fills changed to modes. The matched logistic baseline shares Phase 14 cleaning, 295 source variables and nested partitions. It uses train-fitted categorical modes, numeric medians, standardized filled values and 295 standardized missingness flags, plus an intercept: 591 design columns. NumPy L-BFGS uses fixed L2 0.0001, with no outer-fold tuning or interactions. These are complete pipeline comparisons with different model-specific final matrices.

The [matched study](../results/eda/phase38_matched_logistic_summary.md) gives logistic F1 **0.434467**, versus **0.442155** for Phase 14: an absolute gain of **0.007689**, positive in all three outer folds. Its paired 95% interval **[+0.004919, +0.010463]** is conditional on fitted models and selected thresholds, excluding retraining and repeated-selection uncertainty. All nine logistic fits converged within 484 iterations; recorded runtime is 404.6 seconds. The [verification record](../results/eda/phase38_matched_logistic_verification.json) checks the shared cleaning, rows, folds and frozen Phase 14 predictions. The change from historical logistic F1 0.425628 also changes the solver, regularization, flags and interactions, so it cannot isolate the contribution of cleaning.

Historical Phase 14 recovers 12,855 of 23,180 development positives and produces 22,112 false positives. Fold F1 values are 0.439027, 0.444054 and 0.443512.

## Experimental progression

Early short runs compared linear representations and parameters. More updates and age interactions brought logistic F1 to 0.425628. The booster grid compared depths 3/5, 100/200/400 trees and 64/128 candidate features, selecting 200 trees at depth 5 with F1 0.441741. Phase 14 codebook corrections raised F1 to 0.442155. The small gain (+0.000415) changes sign across folds; codebook correctness is the main reason to retain the corrections.

Later studies tested representation, imputation and model changes against Phase 14. The table shows the **best measured F1 in each family, with thresholds selected in inner folds**.

| Family | Main variants | Best F1 |
| --- | --- | ---: |
| Feature representation | Daily food frequencies, activity one-hot, removal of `ALCDAY5` | 0.441862 |
| Binning | Preserve discrete states across low-cardinality columns or clinical variables only | 0.440783 |
| Missingness and imputation | Nonresponse indicators and selective imputation | 0.441791 |
| Parameters and weighting | Smaller leaves, alternative learning rates, 400 trees, larger L2, depth 7, positive weight 2 | 0.441393 |
| Seeds and ensemble | Second seed and uniform average of both boosters | 0.441111 |
| Feature selection | 100 or 60 columns selected by training-only permutation | 0.439224 |
| MLP | 64 → 32 and 128 → 64 networks with dedicated preprocessing | 0.424451 |

**None of these individual nested-evaluated variants exceeded Phase 14 F1 0.442155.** Imputation showed a small initial screening advantage, but nested confirmation reached 0.441791. Some variants improve recall or AP while adding enough false positives to reduce F1. Both 100- and 60-feature selection performed worse in every fold. Combining diet exclusions and restricted imputation was later selected using AIcrowd feedback, as documented below; its calibration F1 cannot be inserted into this nested table.

MLPs use two ReLU hidden layers, sigmoid output, BCE and Adam. Dedicated training-fitted preprocessing provides imputation, scaling, one-hot encoding and frequency conversion. An internal training holdout selects epochs before a full refit. Both networks underperform the booster in all three folds; the wider network performs worse.

These studies established the Phase 14 reference and informed the combined release candidate. Phase 34 separately evaluates corrected split search; other historical variants were not repeated after that correction. [Experiment history](EXPERIMENTS.md) retains individual results; [MLP.md](MLP.md) documents the neural pipeline.

## HAREHAB1

`HAREHAB1` asks about outpatient rehabilitation after a heart attack and depends on an earlier `CVDINFR4` response. All 620 development rows with a recorded code are positive: response availability itself carries diagnosis-related information.

The feature remains included. Its isolated historical ablation reduces F1 from 0.442155 to 0.431039, a loss of 0.011116. This supports classification of reported disease and limits interpreting the result as prediction before an event. The effect is documented in the [ablation record](../results/experiments/20260921T154905753681Z_phase15-boosting-ablate-harehab1-depth5-features128-200trees.json).

## Split-search comparison: Phase 34

Review found an omission in quantile-bin split search: when edge bins contain observed values, the model could skip a split separating every observed value from all `NaN` values. The correction adds the final boundary when a node contains missing rows, retaining minimum-leaf and gain constraints. It applies to recursive and levelwise strategies.

Forty-nine booster tests passed, including eight regression tests for the correction. An independent check compared 700 cases against exhaustive split enumeration and found no omissions. Gradients, Hessians and leaf updates remain logistic-loss updates with L2 regularization.

Phase 34 retains the same 295 columns, parameters, three outer folds and two inner folds. All nine corrected models were retrained; the control reuses historical Phase 14 results. This isolates the algorithm correction. Phase 33 raw-versus-cleaned comparisons use the earlier implementation.

The three corrected outer models give AP 0.428781 versus 0.428609 and log loss 0.215229 versus 0.215225. Probability correlation is 0.99693. For HAREHAB1 and CVDASPRN, an empty leading bin already allowed the earlier search to separate observed and missing rows. Historical models contain 830 observed-versus-missing splits; corrected models contain 805, including 270 at the newly available final boundary. Many such separations were already representable, helping explain the small ranking change.

Complete nested F1 is **0.440803** versus **0.442155**: **−0.001352**, with two folds lower and one slightly higher. Corrected models recover 13,061 positives and produce 23,019 false positives: 206 additional recoveries and 907 additional false alarms. The paired 95% interval **[−0.003005, +0.000319]**, conditional on fixed models and thresholds, includes zero. The correction completes valid split candidates; its predictive effect is small and uncertain and leaves further tuning open.

The [threshold diagnostic](../results/eda/phase34_threshold_diagnostic.json) crosses scores and thresholds from both versions. Corrected scores with old thresholds give F1 0.441583; corrected scores with new thresholds give 0.440803. The operating threshold contributes to the difference. These cells are descriptive: development comparisons retain thresholds selected in inner folds, without selecting by outer F1. Final calibration later uses new full-train OOF predictions. The [complete comparison](../results/experiments/phase34_missing_only_split_comparison.json) retains metrics, transitions and diagnostic curves; the [summary](../results/eda/phase34_missing_only_split_summary.md) explains the study.

The [Phase 34 comparison's error analysis](../results/eda/phase34_error_followup.json) identifies 9,363 positives missed by both corrected boosting and historical logistic regression: 40.39% of development positives. Of these, 2,307 have `_AGE80 >= 65` and excellent/very good health (`GENHLTH` 1/2). `_AGE80` is CDC-imputed age; this definition reproduces 2,332 cases in the earlier analysis. Combining positive decisions recovers 756 positives but adds 3,480 false positives, reducing F1 to 0.43521. These errors are consistent with the difficulty of recovering past diagnoses from current responses; they do not establish a ceiling on achievable performance.

## Final studies: weighting and training sampling

None of the six late-stage candidates improves its matched control. The selected combined release retains all rows and positive weight 1. Weights 1.25/1.5 and random ratios 5:1/7:1 use historical Phase 14; random 3:1 and hybrid hard use corrected Phase 34. These ratios are not a single comparison of data quantity under one algorithm.

| Study | Control | F1 | Delta F1 | Favorable folds |
| --- | --- | ---: | ---: | ---: |
| Positive weight 1.25 | Historical Phase 14 | 0.440831 | −0.001324 | 0/3 |
| Positive weight 1.5 | Historical Phase 14 | 0.440613 | −0.001542 | 0/3 |
| Random undersampling 5:1 | Historical Phase 14 | 0.438226 | −0.003929 | 0/3 |
| Random undersampling 7:1 | Historical Phase 14 | 0.439820 | −0.002336 | 0/3 |
| Random undersampling 3:1 | Corrected Phase 34 | 0.439389 | −0.001414 | 1/3 |
| Hybrid hard 3:1 | Corrected Phase 34 | 0.393535 | −0.047268 | 0/3 |

[Intermediate positive weights](../results/eda/phase35_positive_weights_summary.md) reduce F1 in every fold. Weight 1.25 removes 1,042 false positives but loses 344 true positives; weight 1.5 recovers 64 positives but adds 430 false alarms. Conditional intervals include zero. This supports weight 1 for historical code; corrected-code weighting needs its own matched study.

[Sampling at 3:1](../results/eda/phase36_undersampling_summary.md) retains every positive and three negatives per positive. Hybrid selection combines half random negatives with half high-scoring negatives from a 24-tree, depth-3 pilot fitted only within the training partition. Statistics, preprocessing and bins use retained rows; evaluation keeps every row and original prevalence. Hybrid AP drops from 0.428781 to 0.384225, F1 falls in every fold and the delta interval is entirely negative. Reduced coverage of the negative distribution is a plausible explanation.

[Random 5:1 and 7:1 ratios](../results/eda/phase37_undersampling_ratios_summary.md) share a permutation for each fit, making 5:1 rows a subset of 7:1. Both reduce F1 in every fold relative to historical control, with entirely negative conditional intervals. The 7:1 decline is smaller. Full training preserves negative-distribution coverage and remains selected. Sampling uses one seed; intervals fix fits, samples and thresholds and exclude retraining and repeated-selection variability.

## Full training and submission

The completed combined study compares leaf L2=1 and L2=5 with the same 297-feature representation, three full-training OOF folds and one full-data fit each. Each candidate selects its own threshold by maximizing pooled OOF F1, with accuracy as a tie-breaker. These metrics describe calibration over all 328,135 labeled rows.

| Combined candidate | Calibration F1 | Threshold | AIcrowd F1 | AIcrowd accuracy |
| --- | ---: | ---: | ---: | ---: |
| **Selected L2=1** | **0.443882381** | **0.21811010373987366** | **0.455** | **0.882** |
| L2=5 | 0.442654786 | 0.2206061257480886 | 0.453 | 0.883 |

AIcrowd values are author-reported feedback on **13 October 2026**, displayed to three decimals. The [combined feedback record](../../evidence/aicrowd/combined_feedback_20261013.json) links both table entries to their submission CSV SHA-256 fingerprints; direct submission URLs were not provided. The separate [candidate feedback record](../../evidence/aicrowd/candidates_feedback_20261013.json) records **Phase 18: F1 0.453 / accuracy 0.882**, **Phase 24: 0.454 / 0.880**, and **Phase 25 L2=5: 0.453 / 0.883**, each linked to its own CSV fingerprint.

The combined L2=1 candidate was selected for the highest displayed AIcrowd F1 among completed candidates with recorded feedback at the 14 October 2026 release. Its advantage over the historical Phase 14 submission is 0.003 in displayed AIcrowd F1; this rounded difference is not a significance test. The author reports a current leaderboard position of **3rd on 14 October 2026**, as recorded in the [release evidence](../../evidence/RELEASE_20261014.json); this was not independently verified and is not a final placing claim.

The selected model trains on all **328,135 labeled rows** and produces **109,379 predictions: 13,999 positive and 95,380 negative**. The CSV uses header `Id,Prediction`, labels −1/+1 and official sample ID order. The [selected submission record](../results/eda/final_combined18_24_submission.json) preserves calibration, model and configuration fingerprints, counts and feedback provenance. From `project/`, `python run.py` uses the combined preprocessing and the byte-exact frozen Phase 14 booster with the selected threshold. The completed driver is reproduced from the same directory with `python -m tools.final_combined_18_24 prepare` followed by `python -m tools.final_combined_18_24 run --workers 1`; a fresh run requires official data and fits both combined candidates.

The earlier two-implementation calibration study is preserved separately. Historical Phase 14 uses threshold **0.2106169795070252** with calibration F1 **0.442769549** and AIcrowd **0.452 / 0.878**; corrected Phase 34 uses threshold **0.2214498433950319** with calibration F1 **0.443569854**. Phase 34's calibration advantage does not reveal its AIcrowd score. Historical Phase 14 produces **14,746 positive and 94,633 negative** predictions. Its [submission record](../results/eda/final_phase14_submission.json), [preserved configuration](../configs/historical_phase14_model.json) and [nested validation suite](../configs/experiments/final_phase14_validation.json) retain that earlier pipeline. The [September summary](../results/eda/final_training_summary.json) records threshold 0.21086909970855153 and 14,728 positive predictions.

Development CV supported many choices, and early baselines consulted the original 20% partition. Repeated AIcrowd submissions also contributed to selecting the combined release. Inner threshold selection reduces one source of optimism but does not remove repeated model-selection effects. There is no completed nested development estimate or matched significance interval for the combined pipeline; its reported calibration result remains separate from historical validation.
