# BRFSS 2015: cardiovascular disease classification

This directory contains the runnable NumPy models, preprocessing and evaluation tools for classifying myocardial infarction or coronary heart disease reported in the **2015 Behavioral Risk Factor Surveillance System (BRFSS)**. The official challenge dataset contains **328,135 labeled respondents, 321 predictors and 109,379 unlabeled test rows**; **8.83%** of training labels are positive. The target is `_MICHD`.

The final pipeline uses histogram gradient boosting with codebook-based cleaning, derived dietary frequencies and restricted imputation learned from training features. Its author-reported AIcrowd feedback is **F1 0.455 and accuracy 0.882**, displayed to three decimals on **13 October 2026**. It was selected for the highest displayed F1 among completed candidates with recorded feedback. Full-training out-of-fold (OOF) threshold calibration gives **F1 0.443882**; **there is no completed nested evaluation of this exact pipeline**.

`HAREHAB1` is retained and contains information about rehabilitation after a heart attack. This is classification of reported disease in a survey, without established prospective clinical validity.

This is an **EPFL Machine Learning CS-433 project**, presented as a portfolio by **Antonio Arbizzani Tonelli**. See the [repository overview](../README.md), [results and interpretation](../docs/RESULTS.md) and the completed [presentation in PDF and PowerPoint](../presentation/README.md). The official course submission and its report are archived separately from this public package.

## Setup and data

**Run every command in this guide from `project/`, not the repository root.** The original course environment uses **Python 3.9 and NumPy 1.23.1**.

On Linux or macOS:

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
py -3.9 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Training uses NumPy and the Python standard library. For tests and EDA plots, install the development dependencies, which also include Matplotlib:

```bash
python -m pip install -r requirements-dev.txt
```

Download the official dataset from the [EPFL Project 1 AIcrowd challenge](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1). It is derived from the BRFSS U.S. health survey; the included [2015 codebook](official_material/project1/brfss_2015_codebook.txt) documents response meanings. Place these files in `data/raw/dataset/`:

| File | Rows | Contents |
| --- | ---: | --- |
| `x_train.csv` | 328,135 | `Id` and 321 predictors |
| `y_train.csv` | 328,135 | `Id` and `_MICHD` labels, encoded as `-1/+1` |
| `x_test.csv` | 109,379 | `Id` and the same 321 predictors |
| `sample_submission.csv` | 109,379 | Test IDs and submission schema |

The repository expects the sample filename shown above. Official data, caches, checkpoints, row-level predictions and submission CSVs are excluded from Git.

## Train the final pipeline

```bash
python run.py --data-dir data/raw/dataset --output submission.csv
```

This command fits the selected pipeline on all **328,135 labeled rows** and writes `Id,Prediction` with labels `-1/+1`. It reads the model parameters and the **already calibrated threshold** from [configs/final_model.json](configs/final_model.json); it does not rerun threshold selection.

The threshold, **0.21811010373987366**, was chosen to maximize F1 on pooled three-fold OOF probabilities across all labeled rows, with accuracy breaking F1 ties. Preprocessing was fitted within each OOF training fold. The resulting **0.443882** F1 describes threshold calibration on the same labels used for selection, separately from nested development evaluation and AIcrowd feedback.

The recorded final run produced **109,379 test predictions: 13,999 positive and 95,380 negative**. The [submission record](results/eda/final_combined18_24_submission.json) preserves source, threshold, input and CSV fingerprints. CSV output uses `create_csv_submission` in [helpers.py](helpers.py), adapted from the [official EPFL starter](https://github.com/epfml/ML_course/blob/main/projects/project1/helpers.py). Explicit UTF-8 encoding and LF line endings preserve the recorded submission's bytes.

The command creates reusable caches under `data/processed/`. If feature CSV values change, use a new `--cache-dir`, even when IDs and array shapes stay the same. To save the fitted model, add `--checkpoint results/final_model.pkl`.

## Reproduce threshold calibration

To rebuild the final combination's OOF calibration and the two leaf-L2 candidates, first prepare the official-data caches:

```bash
python -m tools.prepare_data
python -m tools.final_combined_18_24 prepare
python -m tools.final_combined_18_24 run --workers 1
```

For each of the L2 = 1 and L2 = 5 recipes, this driver fits three OOF models, selects a threshold from their pooled predictions, and fits one model on all labeled rows. It uses the frozen historical booster and learns imputation within each training fold. These are full-training threshold-calibration runs; they do not reproduce a nested evaluation of the final combination. The [utility guide](tools/README.md) describes the calibration tools in more detail; run those commands from `project/` as well.

<a id="reproduce-validation"></a>

## Reproduce historical evaluations

The historical reference is a separate **295-feature** pipeline with its own threshold, preserved in [historical_phase14_model.json](configs/historical_phase14_model.json). To train it and create its submission:

```bash
python run.py --config configs/historical_phase14_model.json --output submission_phase14.csv
```

To reproduce its nested development evaluation:

```bash
python -m tools.prepare_data
python -m src.run_boosting_cv configs/experiments/final_phase14_validation.json
```

The fixed split is included under `results/eda/analysis/splits/`. Historical comparisons use **262,508 development rows, three outer folds and two inner threshold-selection folds**. Each outer fold is evaluated using a threshold chosen from inner OOF predictions, with preprocessing fitted within every training partition. The suite explicitly selects the frozen Phase 14 implementation. For the separate corrected-search comparison, use `configs/experiments/phase34_missing_only_split.json`.

| Historical pipeline | Nested development F1 |
| --- | ---: |
| Ridge | 0.41951 |
| Earlier logistic regression | 0.42563 |
| Matched logistic, Phase 14 cleaning | 0.43447 |
| **Reference booster (Phase 14)** | **0.44216** |
| Corrected split search (Phase 34) | 0.44080 |
| MLP 64 → 32 | 0.42445 |
| MLP 128 → 64 | 0.41927 |

These are complete pipeline comparisons with different model-specific matrices. The historical linear runs retain their earlier median-fill representation. Matched logistic regression shares Phase 14's cleaning, source variables and folds, but uses its own train-fitted filling, scaling and missingness flags. The reference booster improves F1 by **0.00769**, with a conditional paired 95% interval of **[+0.004919, +0.010463]**, and has higher F1 in all three folds. The interval excludes retraining and repeated-selection uncertainty.

### Matched logistic regression

With official data and prepared caches, run:

```bash
python -m src.run_matched_logistic_cv
```

This reproduces the logistic metrics and compares them with the included Phase 14 result record. Reproducing the paired interval additionally requires the original Phase 14 row-level OOF archive from a trusted local copy. That archive is excluded from Git and its fingerprint is checked:

```bash
python -m src.run_matched_logistic_cv --reference-oof results/boosting_artifacts/phase14_codebook_corrections_only/oof_predictions/phase14_boosting_codebook_corrections_only_depth5_features128_200trees_oof.npz
```

The default configuration is [phase38_phase14_logistic.json](configs/experiments/phase38_phase14_logistic.json). It uses 295 cleaned source variables, 295 standardized missingness flags and an intercept, with train-fitted mode/median filling and z-score scaling. NumPy L-BFGS uses fixed L2 **0.0001**, without outer-fold tuning. See the [matched study](results/eda/phase38_matched_logistic_summary.md) and [verification record](results/eda/phase38_matched_logistic_verification.json). Differences from the earlier logistic result also involve the optimizer, regularization, flags and interactions, so they do not isolate a cleaning effect.

### Multilayer perceptrons

```bash
python -m src.run_mlp_cv configs/experiments/phase32_mlp.json
```

[MLP.md](docs/MLP.md) describes preprocessing and training. `run_mlp.py` provides the corresponding full-data training entry point.

## Pipeline details and interpretation

The selected configuration is named `combined18_24_l2_1`. It combines the diet representation studied in Phase 18 with restricted feature-only imputation from Phase 24, on top of Phase 14 codebook cleaning. Six mixed-code raw diet variables are excluded while their existing derived frequency columns are retained. Restricted imputation preserves structural blanks and original missing-reason flags. The resulting **297 transformed features** feed **200 trees of maximum depth 5**, with **leaf L2 = 1**. See [the preprocessing plan](configs/experiments/combined18_24_preprocessing.json) and [full results](../docs/RESULTS.md) for the exact settings.

The selected pipeline uses the frozen [historical booster](src/numpy_boosting_phase14.py). An audit found that this implementation omits some split candidates separating observed values from missing responses. Its exact source is preserved for reproduction of the historical model at commit `aa9a23e907015e91eda75d785c0425172ac32558`. Phase 34 evaluates the correction separately in [src/numpy_boosting.py](src/numpy_boosting.py), with the same 295 columns, parameters and nested folds: F1 changes by **−0.00135**, while average precision rises by **0.00017**. Both versions were submitted after full-training OOF threshold calibration; the historical version was retained before the final combination was selected. The final pipeline does not include the split-search correction.

`HAREHAB1` records rehabilitation after a heart attack. All **620 development respondents** with a recorded response are positive. Removing this feature in the historical ablation (Phase 15) lowered nested F1 to **0.43104**; this is not an ablation of the final combination. Its post-event information prevents treating the survey classification result as evidence of prediction before an event. Repeated development comparisons and challenge feedback also informed model selection; threshold nesting does not remove that selection effect.

The author reported **3rd place on 14 October 2026** on the [AIcrowd leaderboard](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1/leaderboards). The [release record](../evidence/RELEASE_20261014.json) preserves this dated, author-reported position; it is not a final placing or an independently verified rank.

## Checks

After installing the development dependencies, run:

```bash
python -m tools.verify_repository
python -m unittest discover -s tests -q
git diff --check
```

Tests use synthetic fixtures and the included text codebook. The [verification record](../evidence/VERIFICATION.json) reports **242 project tests** passing on **14 October 2026** under **Python 3.14.3 / NumPy 2.4.2**, including a clean public package without official data or saved models. These are dated checks, not a claim that they have been rerun after later documentation edits. The [code review](../docs/CODE_REVIEW.md) records the implementation audit, including logging and report-output regressions.

The original course-delivery audit separately recorded **206 project tests** and **26 public course tests**; [FINAL_AUDIT.md](docs/FINAL_AUDIT.md) preserves that historical evidence. The repository also links a [successful GitHub CI run](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/actions/runs/38324436873) in the official **Python 3.9 / NumPy 1.23.1** environment. The [CI workflow](../.github/workflows/checks.yml) runs that environment on pushes and pull requests.

## Project files

| Location | Purpose |
| --- | --- |
| `run.py` | Full-data training and submission for the selected configuration |
| `helpers.py` | Course CSV helper with explicit UTF-8 and LF output |
| `implementations.py` | Six linear-model functions required by the assignment |
| `src/`, `tests/` | Models, preprocessing, evaluation and tests |
| [configs/README.md](configs/README.md) | Model and experiment configurations |
| [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md) | Technical results, model choice and limitations |
| [docs/README.md](docs/README.md) | Method documentation and historical studies |
| [results/README.md](results/README.md) | Analyses and experiment records |
| [tools/README.md](tools/README.md) | Data preparation and study utilities |

Git includes code, configurations, aggregate reports and the fixed development split. Training data and generated row-level artifacts remain local.
