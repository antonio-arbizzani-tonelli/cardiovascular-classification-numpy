# Ready-to-paste Claude Design prompt

Upload `CLAUDE_DESIGN_INPUT.zip` to Claude Design and paste the prompt below. If uploading individual files, use the set in `presentation/README.md`. The prompt is self-contained; the attached guide supplies slide-level copy and source references.

---

Create a finished, editable 16:9 PowerPoint and matching PDF for my public GitHub project, **“Cardiovascular disease classification in NumPy.”** Credit **Antonio Arbizzani Tonelli** and label it **EPFL Machine Learning CS-433 project**. Deliver **16 main slides plus 3 technical appendix slides**, following the attached `presentation/CLAUDE_DESIGN_BRIEF.md`. All text, captions, labels, notes and filenames must be in English.

The audience is Data Scientist hiring teams and technical reviewers. This is a completed portfolio release dated **14 October 2026**. Explain the result and reasoning clearly enough to read without a presenter. Focus on methods, evidence, decisions and limitations. Do not add recruiter slogans, invented product impact, clinical deployment or prospective heart-attack prediction.

The selected final pipeline is **`combined18_24_l2_1`**: **Phase 18 diet representation + restricted Phase 24 conditional imputation + frozen historical Phase 14 NumPy histogram booster**. Model input is **289 source columns + 8 missing-state flags = 297 transformed features**. Parameters: **200 trees**, **depth 5**, **learning rate 0.05**, **minimum 200 rows per leaf**, **64 bins**, **128 candidate features per node**, **leaf L2 1**, **seed 20260920**. Final threshold: **0.21811010373987366**, selected using pooled three-fold full-train out-of-fold predictions.

Lead with **reported AIcrowd F1 0.455 / accuracy 0.882**. State **“Ranked 3rd on the AIcrowd leaderboard”**, **“Leaderboard snapshot: 14 October 2026”**, and a visible note that position is reported by the author. Challenge scores come from recorded author-reported display feedback, rounded to three decimals, dated 13 October for the selected pipeline. This is a dated current position, not the competition's final placing. Link to https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards. Do not invent participant counts, percentile, independent verification or challenge year.

Dataset facts: **328,135 labeled respondents**, **109,379 challenge test rows**, **321 raw predictors**, **8.83% positive labels**, **44.79% raw missing predictor cells**. BRFSS 2015 target `_MICHD` is **reported myocardial infarction or coronary heart disease**, a cross-sectional classification. All-negative prediction gives **91.17% accuracy and F1 0**; explain why F1 guides selection.

Diet preprocessing excludes six mixed day/week/month source codes while retaining already-existing derived per-day fields; it does not synthesize six new diet variables. Restricted filling uses training features, not disease labels: conditional naive Bayes for selected unknown/refused answers; anchor-bin ridge for height/weight blanks; missing BMI derived where configured. Structural missingness and missing-state information are preserved. Fit imputation inside the relevant training partition. Use the configuration for exact fields.

Keep three result scopes visibly separate:

1. **Historical nested development:** Phase 14 F1 **0.4421552272688187** versus matched logistic F1 **0.4344665761013391**, sharing 262,508 development rows, cleaning, 295 source variables and 3 outer / 2 inner folds. Complete model-specific representations differ. Booster-minus-logistic F1 is **+0.0076886511674795766**, conditional paired 95% interval **[+0.0049185842528166445, +0.010463250337598444]**. This evidence concerns the historical reference.
2. **Selected combined full-train OOF calibration:** F1 **0.4438823812013395** across 328,135 labeled rows. The same labels select and describe the threshold; this is not an independent test.
3. **Selected combined AIcrowd feedback:** reported F1 **0.455**, accuracy **0.882**. Feedback contributed to selection; it is not a pristine external test reserved until all decisions were fixed.

There is **no recorded nested held-out estimate for the selected combination**. Do not assign Phase 14's nested score, interval, confusion matrix or AP to it. Do not plot nested, calibration and challenge F1 as a successive improvement curve. Use the historical CSV for **“Historical nested development comparison”** only. Label Phase 14 as **“Historical Phase 14 reference.”**

Show this separate author-reported challenge comparison, using `assets/chart_data/aicrowd_progression.csv`:

| Pipeline | AIcrowd F1 | Accuracy |
| --- | ---: | ---: |
| Historical Phase 14 | 0.452 | 0.878 |
| Phase 18 diet representation | 0.453 | 0.882 |
| Phase 24 restricted imputation | 0.454 | 0.880 |
| Phase 25 leaf L2 = 5 | 0.453 | 0.883 |
| Combined diet + restricted fill, L2 1 — selected | 0.455 | 0.882 |
| Combined diet + restricted fill, L2 5 | 0.453 | 0.883 |

Selected reported F1 is **+0.003** above Phase 14; do not assert significance from rounded feedback. Accuracy did not decide selection. Do not call imputation wholly rejected: restricted filling is part of the final pipeline.

Include historical neural/ablation results and semantic-cleaning uncertainty from the guide, labeled as historical. Phase 14 nested counts are TP **12,855**, FN **10,325**, FP **22,112**, TN **217,216**, precision **0.367632**, recall **0.554573**. No equivalent independent final-combination confusion matrix is recorded. Submitted test predictions contain **13,999 positives and 95,380 negatives**; these counts are not a confusion matrix.

Include the validity limitation: **`HAREHAB1` is rehabilitation after a heart attack**, retained in the selected pipeline; all **620** historical development respondents with a recorded response are positive. Removing it lowers historical F1 from **0.4422 to 0.4310**. The result does not establish pre-event prediction. The frozen booster also preserves an audited observed-versus-missing split-search omission. Corrected Phase 34 is a separate evaluated comparison, not the selected implementation.

Use restrained navy, white and teal. White evidence slides, navy text, teal for the selected combination, neutrals for historical references. Readable sans-serif: 30–36 pt headlines, 20–24 pt body, table labels no smaller than 16 pt. Most slides should have 40–70 visible words and one main point. Use editable charts, tables and diagrams, not screenshots of paragraphs. F1 bars start at zero and end at 0.50. Difference plots show zero. Do not invent error bars, distributions or threshold curves.

Follow the guide's 16-slide narrative and 3 appendices. Source references go in notes; protocol labels, rank date and material caveats stay visible. Closing link: https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy. Include configuration, evidence and reproduction commands in the appendix. Only cite completed checks in the attached verification; do not invent successful CI or a test count.

Deliver **`RESULTS_PRESENTATION.pptx`**, **`RESULTS_PRESENTATION.pdf`**, and PNG previews of all slides. Inspect exports for clipping, readable tables, stale names, correct dates, metric attribution and working links. PPTX must be editable; PDF must match. Create the finished files, not merely an outline or another design brief.

---
