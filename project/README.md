# BRFSS 2015: cardiovascular disease classification

Run this project from the `project/` directory of
[cardiovascular-classification-numpy](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy).
The project overview, Claude Design brief and current code review are at the
repository root.

An **EPFL Machine Learning CS-433 project** for the AIcrowd challenge.
**Author:** Antonio Arbizzani Tonelli. The target `_MICHD` identifies
myocardial infarction or coronary heart disease reported in the BRFSS survey.
The dataset contains 328,135 labeled respondents, 321 predictors and 8.83%
positive labels.

The final selected model is **Phase 14 histogram gradient boosting**, using
[src/numpy_boosting_phase14.py](src/numpy_boosting_phase14.py), with 295
features cleaned according to the Phase 14 codebook plan, 200 trees and
maximum depth 5. Its AIcrowd submission scores **F1 0.452 and accuracy 0.878**
(author-reported feedback, displayed to three decimals). Nested development F1
is **0.44216**.

An implementation audit recovered omitted splits separating observed values
from missing responses. Phase 34 evaluates the correction with the same
295 columns, parameters and nested folds. Historical Phase 14 reaches
0.44216 with the earlier search (commit
`aa9a23e907015e91eda75d785c0425172ac32558`); the correction changes F1 by
−0.00135 while AP rises by 0.00017. After full-train OOF calibration and
submission of both versions, Phase 14 was selected based on AIcrowd
feedback. Its exact historical source is included as
`src/numpy_boosting_phase14.py`; Phase 34 remains a separate evaluated
comparison using `src/numpy_boosting.py`.

| Pipeline | Development F1 |
| --- | ---: |
| Historical ridge | 0.41951 |
| Historical logistic regression | 0.42563 |
| Matched logistic, Phase 14 cleaning | 0.43447 |
| **Selected Phase 14 booster** | **0.44216** |
| Corrected Phase 34 booster | 0.44080 |
| MLP 64 → 32 | 0.42445 |
| MLP 128 → 64 | 0.41927 |

These scores use the same 262,508 development rows, three outer folds and
thresholds selected on two inner folds. Preprocessing is fitted within each
training partition. The matched logistic baseline shares Phase 14 cleaning
and source variables; it requires train-fitted filling, scaling and missingness
flags. Phase 14 improves F1 by **0.00769**, with a conditional paired 95%
interval **[+0.004919, +0.010463]**, and is higher in all three folds.
Historical linear rows retain their earlier median-fill representation.
Model-specific final matrices differ, so the comparison evaluates complete
pipelines.

`HAREHAB1` is included. It records rehabilitation after a heart attack;
all 620 development respondents with a recorded code are positive. The
historical Phase 15 ablation lowered F1 to 0.43104. Its post-event information limits the
interpretation of the result as prediction before an event.

The [technical results](docs/FINAL_REPORT.md) explain the comparisons,
model choice and limitations, with links to the original experiment evidence.
The [project overview](../README.md) summarizes the work, and the
[Claude Design brief](../presentation/CLAUDE_DESIGN_BRIEF.md) specifies a
19-slide results deck. The course-delivery report is archived outside the
public package.

## Setup

The original course environment uses **Python 3.9 and NumPy 1.23.1**.
Run every command below from the portfolio's **`project/` directory**:

```bash
python3.9 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, use `py -3.9 -m venv .venv` and activate with
`.venv\Scripts\Activate.ps1`.

For tests and EDA plots, install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Training uses NumPy and the Python standard library. Matplotlib is used for
EDA and its tests.

Download the official CSV files from the
[EPFL Project 1 AIcrowd challenge](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1)
and place them under `data/raw/dataset/`, following [data/README.md](data/README.md).

## Train and create a submission

```bash
python run.py --data-dir data/raw/dataset --output submission.csv
```

The command trains on all labeled rows and writes `Id,Prediction` with labels
`-1/+1`. Parameters and the decision threshold are in
[configs/final_model.json](configs/final_model.json). The threshold,
`0.2106169795070252`, maximizes F1 on pooled three-fold OOF predictions over
all **328,135 labeled rows**, with preprocessing fitted within each training
fold. Calibration F1 is 0.442770; it uses the threshold-selection labels and
is separate from the nested development score and AIcrowd feedback.

The selected full-data run produces **109,379 predictions: 14,746 positive
and 94,633 negative**. Its source, threshold, input and CSV fingerprints are
in the [final submission record](results/eda/final_phase14_submission.json).
The command above uses that Phase 14 source and calibrated threshold.

CSV output uses `create_csv_submission` in [helpers.py](helpers.py), adapted
from the [official EPFL starter](https://github.com/epfml/ML_course/blob/main/projects/project1/helpers.py).
Explicit UTF-8 and LF line endings preserve the selected submission's bytes.

The command stores reusable caches under `data/processed/`. When changing
feature CSV values, use a new `--cache-dir`, including when IDs and shape stay
the same. Add `--checkpoint results/final_model.pkl` to save the fitted model.

## Reproduce validation

Prepare the caches, then run the selected cross-validation:

```bash
python -m tools.prepare_data
python -m src.run_boosting_cv configs/experiments/final_phase14_validation.json
```

The fixed split is included under `results/eda/analysis/splits/`. Each outer
fold uses the threshold selected from its inner OOF predictions. This suite
explicitly selects the included frozen Phase 14 implementation. For the
corrected comparison, use `configs/experiments/phase34_missing_only_split.json`.
The [utility guide](tools/README.md) also explains full-train calibration of
both implementations.

To reproduce the matched logistic metrics with official data, run from `project/`:

```bash
python -m src.run_matched_logistic_cv
```

The point comparison uses the included Phase 14 result record. To reproduce
the paired interval, supply the original Phase 14 OOF archive from a trusted
local copy; it is excluded from Git and its fingerprint is checked:

```bash
python -m src.run_matched_logistic_cv --reference-oof results/boosting_artifacts/phase14_codebook_corrections_only/oof_predictions/phase14_boosting_codebook_corrections_only_depth5_features128_200trees_oof.npz
```

The default configuration is
[phase38_phase14_logistic.json](configs/experiments/phase38_phase14_logistic.json).
Logistic regression uses 295 cleaned source variables, 295 standardized missingness flags
and an intercept, with train-fitted mode/median filling and z-score scaling.
NumPy L-BFGS uses fixed L2 0.0001 without outer-fold tuning. See the
[matched study](results/eda/phase38_matched_logistic_summary.md) and
[verification](results/eda/phase38_matched_logistic_verification.json).
The historical and matched logistic scores also differ in optimizer,
regularization, flags and interactions; their difference is not an isolated
cleaning effect.

To reproduce the MLP comparison:

```bash
python -m src.run_mlp_cv configs/experiments/phase32_mlp.json
```

[MLP.md](docs/MLP.md) describes its preprocessing and training.
`run_mlp.py` provides the corresponding full-data training command.

## Checks

```bash
python -m tools.verify_repository
python -m unittest discover -s tests -q
git diff --check
```

The original delivery audit passed **206 project tests** and **26 public
course tests**, including a clean Git-eligible package without data or saved
models. The [current code review](../docs/CODE_REVIEW.md) records checks of
this portfolio copy, including the logging and report-output regressions.
Local verification uses Python 3.14.3 / NumPy 2.4.2. [GitHub CI passed](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/actions/runs/38324436873)
in the official Python 3.9 / NumPy 1.23.1 environment. The active
[portfolio CI](../.github/workflows/checks.yml) runs Python 3.9 / NumPy 1.23.1
on pushes and pull requests. Tests use synthetic fixtures and the included
text codebook. [Historical delivery checks](docs/FINAL_AUDIT.md) preserve
the earlier audit evidence.

## Project files

| Location | Purpose |
| --- | --- |
| `run.py` | Training and submission for the selected model |
| `helpers.py` | Course CSV submission helper, with explicit UTF-8 and LF output |
| `implementations.py` | Six functions required by the assignment |
| `src/`, `tests/` | Models, preprocessing, evaluation and tests |
| [configs/README.md](configs/README.md) | Model and experiment configurations |
| [docs/README.md](docs/README.md) | Technical results and method documentation |
| [results/README.md](results/README.md) | Analyses and experiment records |
| [tools/README.md](tools/README.md) | Data preparation and study utilities |

Git includes code, configurations, reports and the fixed development split.
Data, caches, checkpoints, row-level predictions and submissions are stored
locally.
