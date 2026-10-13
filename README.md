# Cardiovascular Disease Classification in NumPy

An **EPFL Machine Learning CS-433 project** for the AIcrowd challenge, focused on cardiovascular disease classification from BRFSS 2015 survey data. The final model is **Phase 14 histogram gradient boosting in NumPy**, with 295 codebook-cleaned predictors, 200 trees and maximum depth 5. Phase 34 is a separate experimental comparison.

**Ranked 7th on the AIcrowd leaderboard · AIcrowd F1 0.452**

Position reported by the author, 12 Oct 2026: [current leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). This is a current position, not a final placing.

**328,135 labeled respondents · 295 selected features**

The AIcrowd score is reported feedback for the selected **Phase 14 submission**, displayed to three decimals and preserved in the academic submission record. On nested development evaluation, Phase 14 reaches **F1 0.4422**, compared with **0.4256** for logistic regression: an absolute improvement of **0.0165** on the same development rows and outer folds.

![Model comparison](assets/figures/model_comparison.png)

The work combines data quality, model implementation and reliable comparisons. The pipeline interprets survey codes using the codebook, routes missing values inside the trees and selects thresholds within training folds. Tests of deeper trees, alternative representations, imputation, class weighting, undersampling, feature selection and two NumPy MLPs supported retaining the selected configuration. The repository records these decisions, including experiments that did not improve F1 and limitations that affect interpretation.

## Explore the work

| Start here | What it shows |
| --- | --- |
| [Results](docs/RESULTS.md) | Comparable metrics, decisions and limitations |
| [Project](project/README.md) | Setup, training and reproduction commands |
| [Code review](docs/CODE_REVIEW.md) | Current checks, corrections and remaining limits |
| [Claude Design brief](presentation/CLAUDE_DESIGN_BRIEF.md) · [PDF](presentation/CLAUDE_DESIGN_BRIEF.pdf) | A 19-slide specification with copy, visual direction and source evidence |

## Technical scope

Training uses NumPy and the Python standard library. The project implements the six required linear-model functions, a histogram gradient booster and a two-hidden-layer MLP with Adam. Configurations, fixed development splits and experiment records make the comparisons inspectable.

The target is **reported myocardial infarction or coronary heart disease** (`_MICHD`). Phase 14 includes `HAREHAB1`, a question about rehabilitation after a heart attack, which limits interpretation as prediction before an event. Its source is preserved in `project/src/numpy_boosting_phase14.py`, including an audited split-search omission. The Phase 34 correction was evaluated separately and was not adopted as the final model. See [the results and scope](docs/RESULTS.md).

## Run the checks

From `project/`, after installing `requirements-dev.txt`:

```bash
python -m tools.verify_repository
python -m unittest discover -s tests -q
```

Training requires the official challenge CSVs, which are excluded from this repository. Follow the [project setup](project/README.md) before running `python run.py`.

Course context: [EPFL Machine Learning, CS-433](https://www.epfl.ch/labs/mlo/machine-learning-cs-433/). Challenge: [AIcrowd EPFL Machine Learning Project 1](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1).

**Author:** Antonio Arbizzani Tonelli · [GitHub repository](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy).
