# Cardiovascular Disease Classification in NumPy

This project classifies whether respondents to the **2015 Behavioral Risk Factor Surveillance System (BRFSS)**, a U.S. health survey, reported myocardial infarction or coronary heart disease. It uses the dataset supplied for the EPFL Machine Learning CS-433 challenge: **328,135 labeled respondents, 321 predictors and 109,379 unlabeled test rows**. Positive labels account for **8.83%** of the training data.

The models and training pipeline are implemented with **NumPy and the Python standard library**. The project compares linear models, histogram gradient boosting and two multilayer perceptrons (MLPs), with particular attention to survey response codes, missing data and decision thresholds. The final pipeline uses histogram gradient boosting with codebook-based cleaning, derived dietary frequencies and restricted imputation learned from training data.

The target, `_MICHD`, describes reported disease in a cross-sectional survey. The retained `HAREHAB1` question concerns rehabilitation after a heart attack and contains post-event information. These results support survey classification; they do not establish prospective clinical prediction.

## Results at a glance

| Result | F1 | What it measures |
| --- | ---: | --- |
| Final pipeline: AIcrowd feedback | **0.455** | Author-reported challenge score used in model selection; accuracy **0.882** |
| Final pipeline: out-of-fold threshold calibration | **0.443882** | Three-fold predictions over all labeled rows; the same labels select and describe the threshold |
| Historical reference: nested development evaluation | **0.442155** | Earlier pipeline, with threshold selection inside each outer training fold |

**No completed nested evaluation is available for the exact final pipeline.** Its challenge F1 is 0.003 higher than the historical reference's displayed 0.452, but repeated challenge feedback informed the choice. The out-of-fold (OOF) calibration score is not an independent test result.

![Recorded AIcrowd results](assets/figures/aicrowd_progression.png)

The final pipeline's challenge scores were reported by the author on **13 October 2026**, to three decimal places. The author also reported **3rd place on 14 October 2026** on the [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). This is a dated, author-reported position, not a final placing; the [release record](evidence/RELEASE_20261014.json) preserves its provenance.

In the historical controlled comparison, the reference booster reached F1 **0.442155**, versus **0.434467** for logistic regression with the same codebook cleaning, source variables and folds: a gain of **0.007689**. These results use **262,508 development rows, three outer folds and two inner threshold-selection folds**. They compare complete historical pipelines and do not evaluate the final combination.

![Historical nested development comparison](assets/figures/model_comparison.png)

## Run the project

Follow the [project guide](project/README.md) to create the environment and obtain the official challenge CSVs, which are excluded from Git. Run commands from `project/`. With the data in `project/data/raw/dataset/`, train the selected pipeline and write a submission with:

```bash
python run.py --data-dir data/raw/dataset --output submission.csv
```

The command fits all labeled rows and applies the threshold stored in [final_model.json](project/configs/final_model.json). The guide also explains how to reproduce threshold calibration, historical nested evaluation and the model comparisons.

Repository checks use synthetic fixtures and the included codebook. After installing `requirements-dev.txt` from `project/`, run:

```bash
python -m tools.verify_repository
python -m unittest discover -s tests -q
```

## Methods and evidence

The final pipeline is recorded as `combined18_24_l2_1`: it combines the diet representation studied in Phase 18 with restricted conditional imputation from Phase 24. It uses **297 transformed features, 200 trees, maximum depth 5 and leaf L2 = 1**. Its threshold, **0.21811010373987366**, maximizes F1 on pooled three-fold OOF probabilities over all labeled rows, with accuracy breaking F1 ties. Among completed candidates with recorded AIcrowd feedback, this pipeline had the highest displayed F1 at the **14 October 2026 release**.

The booster source is the frozen historical Phase 14 implementation. It retains an audited omission of some observed-versus-missing split candidates so that the historical submission remains reproducible. The corrected implementation was evaluated separately as Phase 34; the final pipeline uses the frozen version. The experiment archive also records studies of representations, missingness, imputation, tree parameters, weighting, sampling and feature selection. The six linear-model functions required by the course are included in `project/implementations.py`.

| Document | Contents |
| --- | --- |
| [Results and interpretation](docs/RESULTS.md) | Evaluation protocols, model selection, detailed scores and limitations |
| [Runnable project](project/README.md) | Setup, data files, training, calibration and historical reproduction |
| [Technical report](project/docs/FINAL_REPORT.md) | Preprocessing, experiments and implementation details |
| [Code review](docs/CODE_REVIEW.md) | Implementation audit and recorded release checks |
| [Presentation PDF](presentation/RESULTS_PRESENTATION.pdf) · [PowerPoint](presentation/RESULTS_PRESENTATION.pptx) | Problem, methods, results and limitations in 10 main slides and four appendices; [sources and version notes](presentation/README.md) |
| [Release evidence](evidence/RELEASE_20261014.json) · [Verification record](evidence/VERIFICATION.json) | Configuration, score provenance, dated rank and previously executed checks |

This is an **EPFL Machine Learning CS-433 project**, presented here as a portfolio by **Antonio Arbizzani Tonelli**. The official course submission and its report remain separate from this public package.

Course: [EPFL Machine Learning, CS-433](https://www.epfl.ch/labs/mlo/machine-learning-cs-433/). Challenge and dataset access: [AIcrowd EPFL Machine Learning Project 1](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1). Repository: [cardiovascular-classification-numpy](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy).
