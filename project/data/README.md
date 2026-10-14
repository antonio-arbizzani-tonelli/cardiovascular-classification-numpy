# Dataset files

Download the official archive from the
[EPFL Project 1 AIcrowd challenge](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1)
and place the four CSV files under **`project/data/raw/dataset/`**, relative to
the outer repository root. These are challenge extracts from the 2015 BRFSS
survey; use the challenge files rather than a separately downloaded BRFSS release.

| File | Rows | Recorded bytes | Contents |
| --- | ---: | ---: | --- |
| `x_train.csv` | 328,135 | 227,376,867 | `Id` and 321 predictors |
| `y_train.csv` | 328,135 | 3,469,411 | `Id` and labels `-1/+1` |
| `x_test.csv` | 109,379 | 91,705,179 | `Id` and the same 321 predictors |
| `sample_submission.csv` | 109,379 | 1,203,182 | Test IDs and output schema |

The [dataset audit](../results/eda/dataset_audit.json) records these sizes and
SHA-256 fingerprints. See [DATA.md](../docs/DATA.md) for target semantics,
missingness and the distinction between historical and final preprocessing.

**Run project commands from `project/`.** If the shell is at the outer
repository root, first change directory, then prepare the caches:

```bash
cd project
python -m tools.prepare_data
```

If already in `project/`, run only the `python` command. All paths below are
relative to that working directory.

The utility validates schemas and ID alignment, then stores arrays under
`data/processed/` (the outer path is `project/data/processed/`). This command
does not train a model. `run.py` uses the same loaders for full training;
follow the [project guide](../README.md#train-the-final-pipeline).

When changing feature CSV values, use a new `--cache-dir`, including when
IDs and shape stay the same: existing feature caches are checked for dimensions
and IDs, not every value. The defaults are `--data-dir data/raw/dataset` and
`--cache-dir data/processed`; custom relative paths also resolve from `project/`.
Raw data and caches are local files ignored by Git.
