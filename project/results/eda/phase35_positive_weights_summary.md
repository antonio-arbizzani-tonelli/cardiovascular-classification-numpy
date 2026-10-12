# Phase 35 — positive weights 1.25 and 1.5

Two new candidates use the historical Phase 30 numerical source, isolated from the later missing-only split-search correction. Only positive loss weight changes; negative weight remains 1. The same 262,508 development rows, 295 features, seeds and parameters use three outer and two inner threshold folds: nine fits per candidate. Phase 14 and the previously evaluated weight 2 are controls.

| Weight | F1 | Precision | Recall | AP | False positives | Delta F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.442155227 | 0.367632339 | 0.554572908 | 0.428609250 | 22112 | +0.000000000 |
| 1.25 | 0.440830852 | 0.372561865 | 0.539732528 | 0.429135259 | 21070 | -0.001324375 |
| 1.5 | 0.440613223 | 0.364315727 | 0.557333909 | 0.428593410 | 22542 | -0.001542004 |
| 2 | 0.439118448 | 0.361155162 | 0.560008628 | 0.428237932 | 22962 | -0.003036779 |

## Weight 1.25

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.436761167 | -0.002265680 | 0.252827616 |
| 2 | 0.443335634 | -0.000717887 | 0.257905940 |
| 3 | 0.442459051 | -0.001052594 | 0.258702229 |

No fold improves and the higher-F1/two-fold criterion fails. The conditional paired F1-delta interval is [−0.003075318, +0.000438710]. Record: `results/experiments/20261007T115927629165Z_phase35-phase14-positive-weight1p25-depth5-features128-200trees.json`.

## Weight 1.5

| Fold | F1 | Delta F1 | Inner threshold |
| --- | ---: | ---: | ---: |
| 1 | 0.437386203 | -0.001640645 | 0.277951874 |
| 2 | 0.442100867 | -0.001952654 | 0.289111002 |
| 3 | 0.442404261 | -0.001107385 | 0.279912741 |

No fold improves and the criterion fails. The conditional paired F1-delta interval is [−0.003190407, +0.000087698]. Record: `results/experiments/20261007T115928100147Z_phase35-phase14-positive-weight1p5-depth5-features128-200trees.json`.

Before testing, all three historical reference checkpoints replay exactly. Nine partitions/bins match Phase 30; all candidate outer checkpoints, inner OOF, thresholds and metrics are reproduced. Executed sources stay in `results/boosting_artifacts/phase35_positive_weights/source_snapshot/`; checkpoints every 25 trees allow resume.

Development folds have been reused for model choices; bootstrap holds fits/thresholds fixed. These historical-code comparisons do not establish the best weight after Phase 34 correction. During the run, an independent Phase 34 activity changed final configuration; it is not an input of these historical suites. Resume manifests excluded that control file while retaining numerical sources, inputs, suite and all nine partition signatures; earlier manifests remain saved. This experiment changed neither final configuration nor submission. Reproduce with `python -m tools.phase35_positive_weights prepare` then `python -m tools.phase35_positive_weights run`; local official data and the historical Phase 30 snapshot are required.

Weight 1.25 increases precision but loses 344 TP while avoiding 1,042 FP. Weight 1.5 gains 64 TP and adds 430 FP. Both lose F1 in every fold. Intervals include zero, so they do not prove certain population harm, but offer no operational advantage. Retain weight 1 for the historical implementation; best weight after correction needs its own matched comparison.

Recorded runtime around 497 seconds covers only the final resumed invocation: seven completed fits reused, an eighth resumed from 125 trees and a ninth fitted fresh. It is not nine original training costs. Multiple invocations and an approximately 90-minute interval without recorded progress occurred; per-tree times can include that pause. Logs/checkpoints preserve earlier work. No speed comparison is inferred.

All 15 targeted historical-code tests and four integration checks passed, including identical predictions for 25-tree resume versus continuous 200-tree training at both weights. Old weight-2 OOF results replay on matching inputs, rows, folds and sources. [Comparison JSON](../experiments/phase35_positive_weights_comparison.json).
