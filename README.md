# Cardiovascular Disease Classification in NumPy

An **EPFL Machine Learning CS-433 project** that implements and evaluates a complete classification pipeline for BRFSS 2015 survey data using NumPy.

**Ranked 3rd on the AIcrowd leaderboard · F1 0.455 · Accuracy 0.882**

Position reported by the author on **14 October 2026**; challenge scores reported on **13 October 2026**, displayed to three decimals. [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). The position is a dated snapshot.

The selected pipeline combines **Phase 18 diet representation and Phase 24 restricted conditional imputation**, using the preserved Phase 14 histogram gradient booster: **297 transformed features, 200 trees, depth 5 and leaf L2 = 1**. It trains on all **328,135 labeled respondents** and generates **109,379 test predictions**. This repository contains the final presentation, completed results and selected model for the **14 October 2026 release**.

![Recorded AIcrowd results](assets/figures/aicrowd_progression.png)

The selected combination improves displayed challenge F1 from the historical Phase 14 result of **0.452 to 0.455**. It uses codebook cleaning, retains derived dietary frequencies in place of six mixed-code raw diet variables, and fits restricted imputation within each training partition. Its decision threshold is **0.21811010373987366**, calibrated using three-fold out-of-fold probabilities across all labeled rows.

## Results and evidence

The selected pipeline records **full-train OOF calibration F1 0.443882** and **AIcrowd feedback F1 0.455**. Calibration labels also select the threshold, and challenge feedback informed model selection. No completed nested-development estimate is available for this exact combined pipeline.

The historical controlled comparison uses **262,508 development rows, three outer folds and two inner threshold-selection folds**. Phase 14 reaches **F1 0.442155**, compared with **0.434467** for logistic regression with shared codebook cleaning and source variables: a gain of **0.007689**. These scores describe the historical pipelines.

![Historical nested development comparison](assets/figures/model_comparison.png)

| Start here | Contents |
| --- | --- |
| [Results and interpretation](docs/RESULTS.md) | Selected result, challenge comparisons and evaluation boundaries |
| [Runnable project](project/README.md) | Setup, training, historical reproduction and checks |
| [Code review](docs/CODE_REVIEW.md) | Implementation audit and release verification |
| [Results presentation: PDF](presentation/RESULTS_PRESENTATION.pdf) · [PowerPoint](presentation/RESULTS_PRESENTATION.pptx) | 16 slides explaining the methods, results and limitations |
| [Release evidence](evidence/RELEASE_20261014.json) | Selected configuration, score provenance and dated rank |

## Technical scope

Training uses NumPy and the Python standard library. The project implements the six required linear-model functions, histogram gradient boosting and two MLP architectures. The experiment archive records completed studies of representations, missingness, imputation, tree parameters, weighting, sampling and feature selection.

The target, `_MICHD`, records **reported myocardial infarction or coronary heart disease**. The retained `HAREHAB1` rehabilitation question contains post-event information, so the demonstrated task is survey disease classification. Prospective clinical use would require a different feature policy and fresh validation. The historical booster also retains an audited split-search omission for exact reproducibility; the corrected Phase 34 implementation is evaluated separately.

## Reproduce the project

From `project/`, install `requirements-dev.txt` and run:

```bash
python -m tools.verify_repository
python -m unittest discover -s tests -q
```

Training requires the official challenge CSVs, which are excluded from Git. Follow the [project setup](project/README.md), then use `python run.py` for the selected combined pipeline. The [historical configuration](project/configs/historical_phase14_model.json) preserves the Phase 14 reference. The [verification record](evidence/VERIFICATION.json) distinguishes current checks from dated evidence.

Course: [EPFL Machine Learning, CS-433](https://www.epfl.ch/labs/mlo/machine-learning-cs-433/). Challenge: [AIcrowd EPFL Machine Learning Project 1](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1).

**Author:** Antonio Arbizzani Tonelli · [GitHub repository](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy).
