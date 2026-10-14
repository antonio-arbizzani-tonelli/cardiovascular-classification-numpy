# Results presentation guide: EPFL Machine Learning CS-433

Create an editable **16:9 PowerPoint and a matching PDF** for [cardiovascular-classification-numpy](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy). Use **16 main slides and 3 technical appendix slides**. The deck must explain the completed portfolio release without a presenter, with readable captions, clear metric scopes and traceable sources. The audience is Data Scientist hiring teams and technical reviewers.

Credit **Antonio Arbizzani Tonelli**. Present this as an **EPFL Machine Learning CS-433 project**. Use English throughout, including chart labels, speaker notes and filenames. Describe the project, decisions and evidence directly; avoid recruiter slogans, invented business impact and claims of clinical deployment. The academic submission report is a separate artifact.

**Release date: 14 October 2026. Final selected pipeline for this release: `combined18_24_l2_1`.** It combines the Phase 18 diet representation with restricted Phase 24 conditional imputation, followed by the frozen historical Phase 14 NumPy booster. Its reported AIcrowd result is **F1 0.455 and accuracy 0.882**. The author reports **current leaderboard rank 3 on 14 October 2026**. This is a dated position, not a competition's final placing. The portfolio has a selected result and complete reproduction instructions; do not describe uncompleted local tests or invent outcomes for them.

## Evidence and metric rules

Use `evidence/RELEASE_20261014.json` for selection and rank, `evidence/aicrowd/` for copied feedback and delivery records, `project/configs/final_model.json` for the runnable default, and `docs/RESULTS.md` for interpretation. The selected record is `project/results/eda/final_combined18_24_submission.json`. `evidence/METRICS.json` and `assets/chart_data/model_comparison.csv` preserve the historical controlled comparisons; `assets/chart_data/aicrowd_progression.csv` supplies the challenge comparison. Source references below are relative to the repository root.

Keep these evidence types visibly separate:

| Evidence | Pipeline | F1 | What it establishes |
| --- | --- | ---: | --- |
| Historical nested development | Phase 14 reference | 0.442155 | Excluded outer folds with inner threshold selection |
| Matched nested development | Logistic, shared Phase 14 cleaning | 0.434467 | Controlled comparison on the same development rows and folds |
| Full-train OOF calibration | Selected combined pipeline | 0.443882 | Threshold selection; labels also describe the selected threshold |
| Reported AIcrowd feedback | Selected combined pipeline | 0.455 | Author-reported challenge display score, rounded to three decimals |

There is **no recorded nested held-out estimate for the selected combined pipeline**. Never relabel Phase 14's nested F1, interval, confusion counts or AP as the combined pipeline's result. Never present 0.442155 → 0.443882 → 0.455 as a same-protocol improvement curve. Challenge feedback contributed to selection and is not a pristine external test reserved until every choice was fixed.

On the cover and rank slide, use:

> Ranked 3rd on the AIcrowd leaderboard
>
> Leaderboard snapshot: 14 October 2026
>
> Position reported by the author; challenge scores from recorded author-reported AIcrowd feedback.

Link to the [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). Do not infer participant count, percentile, challenge year, independent verification or final placing.

## Narrative and visual direction

Lead with the selected outcome, then explain the data, semantic preprocessing, NumPy implementation, evaluation evidence, model selection and limitations. Each slide should answer one concrete question through its headline, body and caption.

Use white evidence slides, navy text and teal for the selected combined pipeline. A restrained navy cover and closing can frame the deck. Use a clean sans-serif, 30–36 pt headlines and 20–24 pt body text. Keep tables and notes readable; avoid text below 16 pt. Most slides should have 40–70 visible words, excluding concise chart labels. Use native PowerPoint charts, tables and editable diagrams. Avoid medical stock images, 3D charts, gauges and oversized rank badges.

F1 bar charts use a zero-based axis ending at 0.50. A difference plot may use a centered axis with zero and its interval labeled. Historical references use navy or neutral colors. Do not put historical Phase 14 in the selected-model accent because an older asset did so; regenerate editable charts from the supplied CSV.

## Slide 1 — Cardiovascular disease classification in NumPy

**On-slide copy:**

> Antonio Arbizzani Tonelli · EPFL Machine Learning CS-433
>
> Selected pipeline: diet representation + restricted imputation + NumPy boosting
>
> AIcrowd F1 0.455 · Accuracy 0.882
>
> Ranked 3rd · Leaderboard snapshot: 14 October 2026

**Visual:** Typographic cover with the project title leading. Include the small author-report note and clickable leaderboard link.

**Caption:** A completed portfolio release for classifying reported cardiovascular disease in BRFSS survey data.

**Source:** `evidence/RELEASE_20261014.json`, `evidence/aicrowd/combined_feedback_20261013.json`, author-reported rank.

## Slide 2 — The selected result comes from an inspectable pipeline

**On-slide copy:**

> Semantic cleaning → diet representation → restricted imputation → NumPy boosting → OOF threshold → challenge submission
>
> Final release: `combined18_24_l2_1`, 297 transformed features and 200 trees.
>
> Reported challenge F1 0.455; configuration and feedback are preserved with provenance.

**Visual:** One editable pipeline diagram. Pair threshold and submission stages with their separate calibration and feedback records.

**Caption:** The model and threshold are fixed for the 14 October 2026 public release.

**Notes:** “Completed release” describes the portfolio and selected recorded result. It does not assert that the challenge has ended.

**Source:** `project/configs/final_model.json`, `evidence/RELEASE_20261014.json`, `evidence/aicrowd/combined_manifest_summary_20261013.json`.

## Slide 3 — Missing responses and a minority positive class shape the task

**On-slide copy:**

> 328,135 labeled respondents · 109,379 challenge test rows
>
> 321 raw predictors · 8.83% positive labels
>
> 44.79% of raw predictor cells are missing.
>
> Target `_MICHD`: reported myocardial infarction or coronary heart disease.

**Visual:** A labeled positive/negative proportion strip beside sample and missingness counts.

**Caption:** BRFSS 2015 is a cross-sectional survey; the label describes a reported diagnosis.

**Source:** `project/docs/DATA.md`, `project/results/eda/dataset_audit.json`, `evidence/METRICS.json`.

## Slide 4 — Accuracy alone would miss every positive respondent

**On-slide copy:**

> An all-negative classifier reaches 91.17% accuracy and F1 0.
>
> F1 guides selection because recovering the minority positive class matters.
>
> The selected challenge result has accuracy 88.2% and F1 0.455; accuracy alone is not the success criterion.

**Visual:** Two labeled metric columns. Clearly distinguish the descriptive class-balance baseline from challenge feedback.

**Caption:** Precision and recall describe the F1 trade-off; majority-class accuracy can conceal zero positive recovery.

**Source:** Dataset prevalence in `evidence/METRICS.json`; selected feedback in `evidence/aicrowd/combined_feedback_20261013.json`.

## Slide 5 — Survey codes are interpreted before models are fitted

**On-slide copy:**

> `ALCDAY5=888`: no alcohol consumption → zero
>
> `PHYSHLTH=88`: zero unhealthy days → zero
>
> Feature-specific “unknown” and “refused” codes → missing
>
> The codebook separates real quantities, categories and nonresponses.

**Visual:** Three editable before/after examples. Do not imply that 88, 7 or 9 is recoded globally.

**Caption:** Semantic recoding is feature-specific. Learned quantities are fitted on training rows only.

**Notes:** Optional detail: 1,095,421 nonresponse codes and 899,687 zero-quantity codes were recoded in the historical 262,508-row, 295-column development audit. These are transformation counts, not combined feature counts or performance gains.

**Source:** `project/configs/experiments/phase14_codebook_corrections_only.json`, `project/results/eda/phase33_preprocessing_counts.json`.

## Slide 6 — The final representation combines two specific changes

**On-slide copy:**

> Diet: remove six mixed day/week/month codes; retain existing derived per-day equivalents.
>
> Restricted fill: estimate selected nonresponses and height/weight blanks from training features; derive missing BMI where applicable.
>
> Preserve structural missingness and missing-state information.
>
> Final input: 289 source columns + 8 flags = 297 features.

**Visual:** Two branches merge into the final matrix. Show `FRUIT1` → existing `FRUTDA1_`, labeled “retain derived field.”

**Caption:** The plan combines Phase 18 diet exclusions and Phase 24 restricted conditional imputation, rather than blanket filling.

**Notes:** The six excluded raw diet fields are `FRUITJU1`, `FRUIT1`, `FVBEANS`, `FVGREEN`, `FVORANG`, `VEGETAB1`; retained derived counterparts are `FTJUDA1_`, `FRUTDA1_`, `BEANDAY_`, `GRENDAY_`, `ORNGDAY_`, `VEGEDA1_`. Restricted unknown/refused filling targets `INCOME2`, `PNEUVAC3`, `EMPLOY1`, using feature-only conditional naive Bayes. Configured blank `HTM4` / `WTKG3` use anchor-bin ridge models; missing BMI is derived from completed height and weight. The imputer uses features, not disease labels, and is fitted within each training partition. Do not invent six new diet columns or call 297 the retained raw-variable count.

**Source:** `project/configs/experiments/combined18_24_preprocessing.json`, `project/src/conditional_imputation.py`, `evidence/aicrowd/combined_manifest_summary_20261013.json`.

## Slide 7 — Histogram boosting is implemented in NumPy

**On-slide copy:**

> Quantile bins → Newton tree updates for logistic loss → summed predictions
>
> Selected model: 200 trees, depth 5, learning rate 0.05, leaf L2 1.
>
> Training uses NumPy and the Python standard library; missing values are routed inside each tree.

**Visual:** An editable ensemble diagram: training-fitted bins, one tree and additive score converted to probability.

**Caption:** Combined preprocessing uses the preserved historical Phase 14 booster implementation.

**Notes:** The selected implementation preserves its historical split search, including an audited omission of some observed-versus-missing endpoint candidates. Corrected Phase 34 is a separate evaluated comparison. Do not claim that correction is in the selected model.

**Source:** `project/src/numpy_boosting_phase14.py`, `project/configs/final_model.json`, `docs/CODE_REVIEW.md`.

## Slide 8 — Each reported score answers a different question

**On-slide copy:**

> Historical nested development: compare pipelines using excluded outer folds and inner threshold selection.
>
> Selected full-train OOF: choose the final threshold using all labeled rows.
>
> AIcrowd feedback: compare submitted challenge candidates.
>
> No nested held-out score is recorded for the selected combination.

**Visual:** Three parallel rows: “controlled reference,” “calibration” and “challenge feedback.” Use the 3 outer / 2 inner fold diagram in the historical reference row only.

**Caption:** Threshold nesting controls threshold-selection optimism; repeated model choice still reuses development and challenge evidence.

**Notes:** Historical comparisons use 262,508 development rows. Full-train calibration uses three OOF folds across 328,135 rows; labels also optimize the threshold. Do not merge these populations into one performance trend.

**Source:** `evidence/METRICS.json`, `project/results/eda/final_combined18_24_submission.json`, `project/configs/experiments/final_phase14_validation.json`.

## Slide 9 — The historical booster beat a matched linear reference

**On-slide copy:**

> Matched logistic: nested F1 0.4345
>
> Historical Phase 14 booster: nested F1 0.4422
>
> Absolute difference: +0.0077, higher in all three outer folds.
>
> Shared cleaning, 295 source variables and nested folds.

**Visual:** Editable horizontal chart from `assets/chart_data/model_comparison.csv`, axis 0–0.50. Title: “Historical nested development comparison.” Label Phase 14 as the historical reference.

**Caption:** Conditional paired 95% interval: [+0.0049, +0.0105]. This supports the historical comparison, not a combined-model held-out claim.

**Notes:** Model-specific matrices differ. Logistic uses train-fitted filling, standardized values, missingness flags, an intercept and fixed L2 0.0001 with NumPy L-BFGS. The interval conditions on fixed fits and thresholds, excluding retraining and repeated-selection uncertainty. The improvement over older logistic is not a cleaning-only ablation.

**Source:** `assets/chart_data/model_comparison.csv`, `project/results/eda/phase38_matched_logistic_summary.md`, `evidence/METRICS.json`.

## Slide 10 — Several tested alternatives added complexity without a gain

**On-slide copy:**

> Historical nested F1:
>
> MLP 64 → 32: 0.4245 · MLP 128 → 64: 0.4193
>
> Top 100 features: 0.4392 · Positive weight 1.25: 0.4408
>
> Phase 14 reference: 0.4422

**Visual:** Editable table with tested change, F1 and decision. Use ordinary method names alongside phase identifiers.

**Caption:** These configurations did not beat the historical reference; other tuning is not ruled out.

**Notes:** MLPs use dedicated preprocessing, ReLU, binary cross-entropy, Adam and training-only epoch selection. Historical restricted imputation had nested F1 0.441791 but later challenge feedback F1 0.454. Do not call all imputation rejected: restricted imputation is selected in the combined release. Local and challenge evidence answer different questions.

**Source:** `project/results/eda/phase32_mlp_summary.md`, `project/results/eda/phase29_feature_selection_summary.md`, `project/results/eda/phase35_positive_weights_summary.md`, `project/results/eda/phase24_original_restricted_imputation_summary.md`.

## Slide 11 — Semantic correctness does not imply a large measured uplift

**On-slide copy:**

> Historical raw-predictor booster: F1 0.441457
>
> Historical cleaned reference: F1 0.442155
>
> Difference: +0.000698
>
> Conditional paired 95% interval: [−0.001226, +0.002635]

**Visual:** Difference plot centered on zero, with its interval crossing zero and both F1 values visible.

**Caption:** This measures cleaning and exclusions together; the small uncertain difference does not establish a large gain.

**Notes:** Raw and cleaned pipelines have 321 and 295 source variables. Each samples 128 features per node, so candidate fractions differ. This is historical preprocessing evidence, not an isolated final-combination test.

**Source:** `project/results/experiments/phase33_raw_preprocessing_comparison.json`, `project/results/eda/phase33_raw_preprocessing_summary.md`.

## Slide 12 — The selected combination has the highest reported challenge F1

**On-slide copy:**

| Submitted pipeline | AIcrowd F1 | Accuracy |
| --- | ---: | ---: |
| Historical Phase 14 | 0.452 | 0.878 |
| Diet representation, Phase 18 | 0.453 | 0.882 |
| Restricted imputation, Phase 24 | 0.454 | 0.880 |
| Leaf L2 = 5, Phase 25 | 0.453 | 0.883 |
| Combined diet + restricted fill, L2 1 | **0.455** | **0.882** |
| Combined diet + restricted fill, L2 5 | 0.453 | 0.883 |

**Visual:** Editable table or F1 bars from `assets/chart_data/aicrowd_progression.csv`, highlighting the selected combination. Do not interpolate or use a cumulative-gain waterfall.

**Caption:** Author-reported scores: Phase 14 on 12 October; later candidates on 13 October 2026. Selected F1 is +0.003 above the historical submission.

**Notes:** This rounded difference is not a significance claim. Accuracy did not determine selection: two alternatives report 0.883 accuracy but lower F1. Submission URLs and independently verified challenge predictions are unavailable. Rank 3 is author-reported on 14 October, not inferred from the table.

**Source:** `assets/chart_data/aicrowd_progression.csv`, `evidence/aicrowd/candidates_feedback_20261013.json`, `evidence/aicrowd/combined_feedback_20261013.json`, historical submission record.

## Slide 13 — The final threshold is calibrated, not independently tested

**On-slide copy:**

> Selected threshold: 0.21811010373987366
>
> Three-fold OOF over 328,135 labeled rows: calibration F1 0.443882.
>
> Fit on all labeled rows, then predict 109,379 challenge test rows.
>
> The same calibration labels select and describe the threshold.

**Visual:** Folds → pooled OOF probabilities → F1 threshold → full-data fit → signed CSV. Do not invent a probability distribution or threshold curve.

**Caption:** OOF prediction excludes each row from model fitting; pooled threshold selection still introduces calibration optimism.

**Notes:** F1 ties are broken by accuracy. The submitted CSV has 13,999 positive and 95,380 negative predictions. These are prediction counts, not a confusion matrix: official test labels are unavailable locally.

**Source:** `project/configs/final_model.json`, `project/results/eda/final_combined18_24_submission.json`, `evidence/aicrowd/combined_verification_20261013.json`.

## Slide 14 — Historical error analysis shows the F1 trade-off

**On-slide copy:**

> Historical Phase 14 nested decisions:
>
> 12,855 positives recovered · 10,325 positives missed
>
> 22,112 false positives · 217,216 true negatives
>
> Precision 0.3676 · Recall 0.5546

**Visual:** Editable confusion matrix labeled as the historical nested reference.

**Caption:** These are historical development counts. No equivalent independent final-combined confusion matrix is recorded.

**Notes:** An operational threshold requires a decision, error costs and fresh validation. Do not translate respondents into patients treated, cases prevented or business savings.

**Source:** Historical Phase 14 result in `evidence/METRICS.json` and linked experiment record.

## Slide 15 — A post-event question limits what the result can claim

**On-slide copy:**

> `HAREHAB1` asks about rehabilitation after a heart attack.
>
> All 620 development respondents with a recorded response are positive.
>
> Removing it lowers historical nested F1 from 0.4422 to 0.4310.
>
> The selected pipeline retains the feature.

**Visual:** Survey-question annotation and a historical with/without comparison, with feature timing explicit.

**Caption:** The project classifies reported disease; its score does not establish prediction before a cardiovascular event.

**Notes:** A prospective study needs a new feature-availability policy and fresh evaluation, including timing checks on other variables. Keep historical ablation attribution visible.

**Source:** `evidence/METRICS.json`, `project/docs/FINAL_REPORT.md`, historical Phase 15 ablation record.

## Slide 16 — The release connects its result to code and evidence

**On-slide copy:**

> Selected NumPy pipeline · Reported AIcrowd F1 0.455
>
> Rank 3, reported by the author on 14 October 2026
>
> Inspect configurations, experiments, verification and limitations on GitHub.
>
> Antonio Arbizzani Tonelli · EPFL Machine Learning CS-433

**Visual:** Restrained closing with the clickable [repository link](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy) and artifact map: `project/`, `docs/RESULTS.md`, `evidence/`, `presentation/`.

**Caption:** The completed release makes the selected outcome reproducible and its evidence limits explicit.

**Notes:** Cite only completed checks in verification records. Do not invent successful CI or a current test count. Local verification, exact prediction replay and a full training rerun are distinct activities.

**Source:** `docs/CODE_REVIEW.md`, `evidence/VERIFICATION.json`, `evidence/SELECTED_REPLAY_20261014.json`, `evidence/RELEASE_20261014.json`, `project/README.md`.

## Appendix A — The selected release has an exact specification

Use an editable parameter table:

| Parameter | Selected value |
| --- | --- |
| Pipeline identifier | `combined18_24_l2_1` |
| Preprocessing variant | `combined18_24` |
| Model input | 289 source columns + 8 flags = 297 |
| Booster implementation | Frozen historical Phase 14 |
| Trees / maximum depth | 200 / 5 |
| Learning rate | 0.05 |
| Minimum rows per leaf | 200 |
| Quantile bins | 64 |
| Candidate features per node | 128 |
| Leaf L2 | 1 |
| Seed | 20260920 |
| Decision threshold | 0.21811010373987366 |
| Calibration | Three-fold full-train OOF; fold seed 20260919 |

Keep the threshold and configuration reference visible; move the SHA-256 to notes. Frozen booster source SHA-256: `6fede57915b07a6ea7675292833f8ad79269e665f09977bffd2a9562ce1aaf98`. Source preservation enables replay; it does not mean the historical split-search omission is corrected.

From the repository's `project/` directory, follow `project/README.md`. After installing development requirements, run `python -m tools.verify_repository` and `python -m unittest discover -s tests -q`. With official CSVs, `python run.py --data-dir data/raw/dataset --output submission.csv` trains the selected default. Original course environment: Python 3.9 / NumPy 1.23.1. Official data, checkpoints and row-level predictions remain outside Git.

**Source:** `project/configs/final_model.json`, `project/README.md`, `evidence/aicrowd/combined_manifest_summary_20261013.json`, `docs/CODE_REVIEW.md`.

## Appendix B — Preserve complete metric scope and provenance

Use the seven-model table from `assets/chart_data/model_comparison.csv`: historical ridge, historical logistic, matched logistic, historical Phase 14 reference, corrected Phase 34 comparison and both MLPs. Include F1, precision, recall and AP. Title it **“Historical nested development comparison”**. Round to four decimals; preserve exact repository values.

Add a separate selected-release block: **OOF calibration F1 0.443882; reported AIcrowd F1 0.455 / accuracy 0.882; author-reported rank 3 on 14 October 2026**. State **“No nested held-out estimate recorded for the combined pipeline.”** Do not add the combination to the historical table as though it shares that protocol.

Corrected Phase 34 has nested F1 0.440803 and AP 0.428781, versus Phase 14's F1 0.442155 and AP 0.428609. It is a methodological comparison, not the selected implementation; the paired F1 difference interval includes zero.

**Source:** `evidence/METRICS.json`, `assets/chart_data/model_comparison.csv`, `evidence/RELEASE_20261014.json`, `evidence/aicrowd/`.

## Appendix C — A new use case requires a new validation study

Use an editable sequence: define decision and error costs → audit feature availability and timing → reserve fresh evaluation data → fit transformations and threshold within training → assess performance and subgroup stability → evaluate impact in the actual operational setting.

Label this **“Proposed validation for a new use case.”** These are transfer requirements, not missing work required to read the completed challenge portfolio. No prospective study, deployment, A/B test or clinical outcome is claimed.

**Source:** Limitations in `docs/RESULTS.md` and `project/docs/FINAL_REPORT.md`.

## Delivery and inspection

Return editable `RESULTS_PRESENTATION.pptx`, matching `RESULTS_PRESENTATION.pdf` and PNG previews of every slide. The PDF is the reading artifact; PowerPoint is the editable source. Source references belong in speaker notes; metric scopes, the rank date and material caveats remain visible on relevant slides.

Check each number against its source. Inspect all exports for clipping, readable tables, consistent model names and working links. No slide may call standalone Phase 14 the final pipeline, report rank 7, assign historical nested evidence to the combination, or call calibration an independent test. Avoid fabricated error bars and stale figures. This guide is the design specification; it is not the slide deck.

Use the latest `CLAUDE_DESIGN_INPUT.zip` with `CLAUDE_DESIGN_PROMPT.md`. Follow `presentation/README.md` to publish the finished deck.
