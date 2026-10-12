# Phase 36 — two undersampling methods

The matched control is corrected Phase 34. All positives remain in training, with three negatives retained per positive. Random samples uniformly. Hybrid hard combines half random negatives and half highest-scoring negatives from a 24-tree, depth-3 pilot trained only inside the training partition; the pilot itself uses random 3:1 sampling.

The same 295 columns, model parameters and control seed are used. Sampling is independent within three outer and six inner training fits. Final preprocessing/bins use only retained rows; inner/outer validation keeps all rows at original prevalence. F1 thresholds use inner OOF scores; local holdout/test labels are not consulted.

| Method | F1 | Precision | Recall | AP | False positives | Delta F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All data | 0.440803240 | 0.362001109 | 0.563459879 | 0.428781433 | 23019 | +0.000000000 |
| random | 0.439388760 | 0.363860265 | 0.554486626 | 0.425835951 | 22471 | -0.001414480 |
| hybrid_hard | 0.393534831 | 0.314654950 | 0.525194133 | 0.384225019 | 26516 | -0.047268409 |

## Random 3:1

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.435385160 | -0.001336289 | 0.471973692 |
| 2 | 0.441968912 | +0.000233812 | 0.481669488 |
| 3 | 0.440899501 | -0.002833570 | 0.479532323 |

One fold improves. The conditional paired 95% F1-delta interval is [−0.003355609, +0.000540069]. Summed nine-fit time including sampling/pilot work is 1,456.7 seconds. Outer retained-row counts are 61,812/61,812/61,816, keeping every positive; no fit resumes (0/9). Record: `results/experiments/20261007T124912476309Z_phase36-undersampling-random-depth5-features128-200trees.json`.

## Hybrid hard 3:1

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.387837389 | -0.048884060 | 0.305151003 |
| 2 | 0.397755028 | -0.043980072 | 0.319127579 |
| 3 | 0.395340202 | -0.048392868 | 0.306946255 |

No fold improves. The conditional paired 95% F1-delta interval is [−0.051378719, −0.043164603]. Summed nine-fit time including sampling/pilot is 1,650.7 seconds. Outer retained-row counts again are 61,812/61,812/61,816, keeping every positive; no fit resumes (0/9). Record: `results/experiments/20261007T125233036668Z_phase36-undersampling-hybrid-hard-depth5-features128-200trees.json`.

Reference checkpoints replay exactly; every selection is reproduced, nine training boundaries checked and three final/three outer pilot checkpoints replayed. Inner OOF, thresholds and metrics are reconstructed; sources and 25-tree checkpoints stay local. Development folds have been reused. Intervals hold fits/thresholds fixed and exclude sampling-seed, retraining and repeated-selection uncertainty. Ratio/pilot are fixed before results, with one sampling seed and no hyperparameter search. Undersampling changes prevalence and, especially for hard selection, the negative distribution; raw scores are not calibrated to the original population.

Reproduce with `python -m tools.phase36_undersampling prepare`, `python -m tools.phase36_undersampling run` and `python -m tools.phase36_undersampling report --publish`. This experiment leaves final configuration and submission unchanged.

Retain all rows in the corrected-code comparison. Random is close but does not improve pooled F1. Hybrid worsens every fold and also lowers AP, precision and recall. These conclusions concern the two fixed 3:1 methods and one seed, not all sampling methods.

Additional replay verifies all 18 main models, nine pilots and 18 bin-boundary sets reconstructed from retained rows alone. Inner OOF probabilities also replay exactly. All 17 unit tests pass; each method passes the synthetic full workflow and 25-tree resume with eight complete checkpoints reused.

Full runner durations are 24.9 minutes random and 28.2 minutes hybrid, including preprocessing, sampling/pilot, training and prediction. Candidates run concurrently, both fresh without resumes. Summed fit times above omit some runner preprocessing. The historical control has two outer models resumed from 125 trees and timers affected by pauses; it is not a clean reference for an acceleration factor.
