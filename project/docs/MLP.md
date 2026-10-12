# NumPy MLP: preprocessing, training and evaluation

The MLP is a separate experimental pipeline. `run.py`, tree preprocessing and `configs/final_model.json` define the selected booster. Phase 32 compares against historical Phase 14, before the Phase 34 observed-versus-missing split correction. Both networks are configured in `configs/experiments/phase32_mlp.json`.

The comparison is complete. Both networks had lower F1 than Phase 14 in all three folds and were not adopted:

| Pipeline | Nested F1 | Delta versus Phase 14 | Favorable folds |
| --- | ---: | ---: | ---: |
| Historical Phase 14 booster | 0.442155 | — | — |
| MLP 64 → 32 | 0.424451 | −0.017704 | 0/3 |
| MLP 128 → 64 | 0.419268 | −0.022887 | 0/3 |

Metrics, thresholds and checks are in the [Phase 32 report](../results/eda/phase32_mlp_summary.md) and [comparison JSON](../results/experiments/mlp/phase32_comparison.json). The comparison preserves the historical booster configuration and preprocessing. [EXPERIMENTS.md](EXPERIMENTS.md) documents the current selected model.

## Code

- `src/numpy_mlp.py`: ReLU, sigmoid output, stable BCE on logits, backpropagation, Adam, weight-only L2, mini-batches and early stopping.
- `src/mlp_preprocessing.py`: dedicated representation fitted on training rows.
- `src/run_mlp_cv.py`: nested CV, checkpoints with preprocessing, reproducible inference, inner/outer OOF predictions and experiment records.
- `run_mlp.py`: full-data training and −1/+1 CSV predictions; requires a threshold selected on development data.

## Representation

Cleaning shares the Phase 14 codebook and overrides: the same 295 permitted predictors plus the configured auxiliary missing-age flag. Raw inputs and tree preprocessing remain unchanged.

Continuous variables and counts use training medians; ordinal and binary variables use modes. Numeric and ordinal channels are centered and scaled using post-imputation training statistics. Binary, indicator and one-hot channels remain 0/1. Nominal features use full one-hot encoding, a missing flag and an unseen-category flag. Every numeric/binary feature has a missing flag. Documented binary codes remain available when training contains only one level. All-missing columns use zero placeholders and flags, without held-out statistics. There is no intercept column or tree binning.

Nine encoded frequencies become daily rates: `ALCDAY5`, `EXEROFT1/2` and six food-frequency columns. Weekly responses use divisor 7; monthly responses use 30. Separate flags preserve the reported unit. Food code 300 means less than monthly: it uses zero in the numeric channel **and a distinct flag**, rather than assigning an exact rate; it remains distinguishable from Never. Semantics were checked against local codebook pages 32, 34–36, 40 and 43. Unexpected finite codes raise an error.

Input width is learned per fold from observed categories. The outer-fold-1 preflight produced 1,178 inputs: approximately 77,569 parameters for 64 → 32 and 159,233 for 128 → 64. Channels that are always zero in training receive zero initial weights, avoiding arbitrary effects when an unseen category activates at inference.

## Protocol

The study uses the same 262,508 development examples, three outer folds (seed 20260919) and two inner folds per outer fold (seed 20260922 + outer-fold number). Each F1 threshold uses only inner OOF predictions.

Each training partition is split 90/10 with stratification to select epochs; selection preprocessing uses only the 90%. Unweighted BCE controls early stopping: at most 80 epochs, patience 8 and `min_delta=0.0001`. The minimum-BCE epoch is retained. Preprocessing and the network are then refitted from scratch on **every training row in that fit** for the selected epoch count. Evaluation rows do not enter this process.

Each architecture requires nine epoch-selection fits and nine full refits: 36 network trainings for two candidates. Adam uses learning rate 0.001, batch size 512 and seed 20261001. The objective is mean BCE + 0.5 × 0.0001 × squared-weight sum; biases are unpenalized. There are no class weights or resampling.

## Reproduction

Install [README](../README.md) dependencies and place the four official CSVs as described in [data/README.md](../data/README.md). CV reads prepared NumPy caches. From the project root in PowerShell:

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
python -m tools.prepare_data
python -m unittest discover -s tests -q
python -u -m src.run_mlp_cv configs/experiments/phase32_mlp.json
```

`tools.prepare_data` checks ID alignment and creates `data/processed/` caches without training models. If feature CSV values change, use a fresh cache directory: reuse checks dimensions and IDs rather than every value. The development-row list is included.

Fits save loss curves, exact gradient-fit/early-stopping/evaluation boundaries, feature audits and checkpoints under `results/mlp_artifacts/phase32/`. Executed source copies, data/configuration hashes and inner/outer OOF predictions are retained locally. Experiment records use `results/experiments/mlp/`. Each candidate's recorded runtime covers the shared suite; individual training times appear in fit reports. Caches, checkpoints, OOF arrays and fit reports are excluded from Git; compact reports and experiment records are included. Historical records retain original execution paths; checkpoint replay requires the local artifacts and consistent paths.

The suite ran under Python 3.14.3 / NumPy 2.4.2 with one OpenBLAS thread. Official Python 3.9 / NumPy 1.23.1 execution remains unverified. Recorded total runtime was 531.47 seconds and depends on hardware and numerical environment.

`run_mlp.py` supports experimental full-data training after fixing the model and threshold on development data:

```powershell
python run_mlp.py --help
```

`--model` accepts `mlp64_32` or `mlp128_64`; mandatory `--threshold` must be between 0 and 1. No final MLP threshold was adopted. The command reads official CSVs, saves the network and preprocessing under `results/mlp_artifacts/full_training/` and defaults to `results/submission_mlp.csv`. Load pickle checkpoints only from trusted local sources. `load_pipeline` and `predict_pipeline` in `src/run_mlp_cv.py` provide inference from raw matrices.

## Interpretation

The primary metric is pooled F1 with nested thresholds. Reports also include fold F1, precision, recall, AP, log loss and runtime. Both networks share preprocessing. The booster comparison evaluates complete pipelines, so it does not isolate architecture under identical input encoding.

Repeated development experiments can introduce selection optimism; this CV is not an untouched final test. A single initialization seed does not establish that every MLP is inferior. `HAREHAB1` remains included, limiting outcome interpretation as explained in the [final report](FINAL_REPORT.md). CV saves validation predictions and does not generate a submission.
