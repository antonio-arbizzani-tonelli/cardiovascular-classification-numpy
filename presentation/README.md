# Results presentation

Read the [PDF](RESULTS_PRESENTATION.pdf) or download the [editable PowerPoint](RESULTS_PRESENTATION.pptx). Both contain **14 slides: 10 main slides and four technical appendices**. The author supplied these completed files on **15 October 2026**; they are published as received.

The presentation opens with the BRFSS survey problem and data, then covers missingness, preprocessing, NumPy gradient boosting, the historical logistic comparison, evaluation, challenge feedback and limitations. The appendices provide the selected recipe, historical comparisons, uncertainty intervals and historical classification errors.

The selected pipeline records author-reported **AIcrowd F1 0.455 and accuracy 0.882**. Full-training OOF F1 **0.443882** describes threshold calibration on the same labels used to select the threshold; historical nested F1 **0.442155** belongs to the earlier Phase 14 pipeline. No completed nested estimate exists for the exact final combination. AIcrowd feedback informed model selection. The retained post-event variable `HAREHAB1` limits interpretation to survey classification, without established prospective clinical validity.

The **3rd place on 14 October 2026** is an author-reported snapshot on the [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards), not a final placing or an independently verified rank. Its provenance is recorded in the [release evidence](../evidence/RELEASE_20261014.json).

## Slide sources

Some slide footers abbreviate filenames. These links resolve them from the repository:

| Slides | Sources |
| --- | --- |
| 1–2: problem and data | [Dataset metrics](../evidence/METRICS.json), [data guide](../project/docs/DATA.md) |
| 3: survey response codes | [Historical cleaning plan](../project/configs/experiments/phase14_codebook_corrections_only.json), [transformation counts](../project/results/eda/phase33_preprocessing_counts.json) |
| 4–5 and Appendix A: final pipeline | [Selected configuration](../project/configs/final_model.json), [preprocessing plan](../project/configs/experiments/combined18_24_preprocessing.json), [imputation source](../project/src/conditional_imputation.py), [frozen booster](../project/src/numpy_boosting_phase14.py) |
| 6 and Appendix B1: historical comparisons | [Matched logistic study](../project/results/eda/phase38_matched_logistic_summary.md), [comparison chart data](../assets/chart_data/model_comparison.csv), [metrics](../evidence/METRICS.json) |
| 7: evaluation and threshold selection | [Historical nested suite](../project/configs/experiments/final_phase14_validation.json), [final submission and calibration record](../project/results/eda/final_combined18_24_submission.json) |
| 8: challenge feedback | [Chart data](../assets/chart_data/aicrowd_progression.csv), [candidate feedback](../evidence/aicrowd/candidates_feedback_20261013.json), [combined feedback](../evidence/aicrowd/combined_feedback_20261013.json) |
| 9 and Appendix C: interpretation and historical errors | [Feature metadata](../project/configs/feature_metadata.json), [metrics and confusion counts](../evidence/METRICS.json), [technical report](../project/docs/FINAL_REPORT.md) |
| 10: reproduction and dated checks | [Project guide](../project/README.md), [verification record](../evidence/VERIFICATION.json), [selected-prediction replay](../evidence/SELECTED_REPLAY_20261014.json) |
| Appendix B2: historical uncertainty intervals | [Cleaning comparison](../project/results/eda/phase33_raw_preprocessing_summary.md), [corrected split-search comparison](../project/results/eda/phase34_missing_only_split_summary.md) |

## Version and verification

The supplied files were checked against the selected configuration and published results at public `main` commit [7f9a359](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/commit/7f9a359760e46de4c08336d3d319bfcda31cf997). Their text agrees slide by slide, and all 14 pages and PowerPoint slides were visually checked. No new training was performed.

The [14 October release record](../evidence/RELEASE_20261014.json) remains a historical record: its 16-slide count and presentation hashes describe the [previous files at that commit](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/tree/d6cbe39a669c61d9f3bbf1da1ac0dc0034c4be94/presentation), rather than the current files. Model, dataset and experiment evidence is unchanged.

**Author:** Antonio Arbizzani Tonelli. **Context:** EPFL Machine Learning CS-433.
