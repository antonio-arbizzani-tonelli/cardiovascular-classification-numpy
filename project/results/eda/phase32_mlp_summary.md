# Phase 32 — MLP with dedicated preprocessing

Full evaluation uses 262,508 development rows, three outer folds and two inner folds for F1 thresholds. Epoch selection uses a training-only 10% holdout, followed by full refit.

| Model | F1 | Delta Phase 14 | Precision | Recall | AP | Log loss | Improved folds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 14 | 0.442155227 | — | 0.367632 | 0.554573 | 0.428609 | 0.215225 | — |
| mlp64_32 | 0.424451233 | -0.017703995 | 0.360722 | 0.515531 | 0.387782 | 0.221674 | 0/3 |
| mlp128_64 | 0.419267861 | -0.022887366 | 0.340005 | 0.546721 | 0.379380 | 0.222710 | 0/3 |

| Model / fold | F1 | Delta Phase 14 | Inner threshold | Refit epochs | Input |
| --- | ---: | ---: | ---: | ---: | ---: |
| mlp64_32 / 1 | 0.411656403 | -0.027370445 | 0.216357470 | 7 | 1178 |
| mlp64_32 / 2 | 0.429213127 | -0.014840394 | 0.217222542 | 7 | 1180 |
| mlp64_32 / 3 | 0.429601553 | -0.013910093 | 0.202820331 | 5 | 1179 |
| mlp128_64 / 1 | 0.417129481 | -0.021897366 | 0.208536416 | 2 | 1178 |
| mlp128_64 / 2 | 0.422633317 | -0.021420204 | 0.190321296 | 4 | 1180 |
| mlp128_64 / 3 | 0.417587727 | -0.025923919 | 0.227644756 | 5 | 1179 |

The shared suite takes 8.86 minutes, including preprocessing, 18 epoch selections and 18 refits; this is not either candidate's individual cost. Data, labels, metadata and splits match the reference, whose historical F1 is reconstructed from OOF predictions. All 18 refit checkpoints reproduce saved scores/decisions. Gradient-fit, early-stopping and evaluation boundaries, thresholds, metrics and hashes are verified. Seven protected booster files retain preflight hashes.

The MLP uses 295 source fields plus the preprocessing plan's auxiliary age flag. Codebook cleaning is shared, but imputation, scaling, one-hot, missing/unseen flags and frequency conversions are MLP-specific. Scores compare complete pipelines, not model family alone. Both MLPs lose F1 against Phase 14 in every fold. `HAREHAB1` is retained; its target link is disclosed in the [final report](../../docs/FINAL_REPORT.md#harehab1).

Execution uses Python 3.14.3 / NumPy 2.4.2, OpenBLAS with one thread; official-runtime compatibility was not checked by this phase. Phase 14 stays selected. [MLP method](../../docs/MLP.md), [full comparison](../experiments/mlp/phase32_comparison.json). Checkpoints remain local under `results/mlp_artifacts/phase32/`.
