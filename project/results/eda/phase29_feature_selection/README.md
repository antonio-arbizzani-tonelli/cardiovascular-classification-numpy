# Phase 29 — selecting 100 and 60 features

Both tests are complete. Phase 14 retains 295 features and nested F1 0.442155227.

| Input | Nested F1 | Delta versus Phase 14 | Improved folds |
| ---: | ---: | ---: | ---: |
| 100 | 0.439223556 | −0.002931671 | 0/3 |
| 60 | 0.437584073 | −0.004571154 | 0/3 |

Both reductions lose every fold. The three outer lists share 37/100 and 19/60 columns, showing substantial variation across training partitions. The [full report](../phase29_feature_selection_summary.md) and [comparison JSON](comparison.json) contain metrics and verification.

Each of nine training partitions independently selects columns on the same development rows/seeds as Phase 14, within three outer/two inner folds. The selector/preprocessing fit on 80%; the remaining 20% chooses a threshold and supplies importance. Ranking uses mean F1 drop on up to 10,000 stratified rows, three permutations per column including NaNs, and a fixed threshold. Top 60 is contained in top 100; reduced boosters refit on all training rows. Feature sampling preserves 128/295: 44 candidates with 100 inputs and 27 with 60. Final thresholds use inner OOF predictions. A tenth development-only selection creates diagnostic lists.

`outer_N`, `outer_N_inner_M` and `development` contain rankings, lists and group importance. Start with the [development ranking](development/ranking.csv), [top 100](development/top100.json), [top 60](development/top60.json) and [selection frequencies](selection_frequency.csv). Records are in `results/experiments/phase29_feature_selection/`; checkpoint/OOF artifacts under `results/boosting_artifacts/phase29_phase14_feature_selection/` remain local and excluded from Git.

The historical runner `tools/phase29_feature_selection.py` uses `configs/experiments/phase29_phase14_feature_selection.json`. Reproduction requires four official CSVs, project dependencies, Phase 14 OOF/checkpoints, verification manifests and source hashes required by preflight. OOF, checkpoints and manifests are local artifacts from the original run. From project root:

```powershell
python -m tools.prepare_data
python -m tools.phase29_feature_selection preflight
python -m tools.phase29_feature_selection run
```

To resume, use `run` alone: it preserves original preflight and verifies completed fits before reuse.
