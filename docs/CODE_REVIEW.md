# Code review and verification

The **14 October 2026 release** selects `combined18_24_l2_1`: combined diet representation and restricted imputation with the frozen Phase 14 booster. The [final configuration](../project/configs/final_model.json) and [selected record](../project/results/eda/final_combined18_24_submission.json) agree on parameters, 297 transformed features and threshold 0.21811010373987366. Historical Phase 14 nested validation remains separately reproducible.

## Current release checks

The public preprocessing was replayed against the trusted completed local model. Its train/test matrix hashes match the original fit, predicted probabilities have maximum difference **0.0**, and the generated CSV has the selected SHA-256: `1e4817ab85020156f579ab33fc5384c8aecd24fd8453ce6e37a3dcc094a45854`. The replay recovers **13,999 positive and 95,380 negative** test predictions without retraining the booster. [Replay evidence](../evidence/SELECTED_REPLAY_20261014.json) records these checks.

The synthetic suite checks selected entry-point parity, configuration identity, training-fold imputation boundaries, checkpoint validation and interrupted-run resume, alongside the existing model, evaluation and report tests. Repository verification checks Python 3.9 syntax, JSON, documentation links, six experiment ledgers and 115 indexed hashes. The [current verification record](../evidence/VERIFICATION.json) reports executed outcomes; the [prior verification](../evidence/VERIFICATION_20261013.json) remains dated historical evidence.

The [root CI workflow](../.github/workflows/checks.yml) runs verification and tests under Python 3.9 / NumPy 1.23.1. A local pass and a completed GitHub Actions run are recorded separately. Official data, model checkpoints, row-level predictions and local logs are excluded from publication. The original course workspace and ongoing runs are not modified by this release.

## Earlier corrections retained

| Issue | Retained correction |
| --- | --- |
| Logged CV rejected the historical implementation keyword | The wrapper forwards it to the selected booster factory. |
| Booster copied columns from read-only inference data | Prediction reads selected columns without mutating inputs. |
| MLP module used a Python 3.9-incompatible dataclass option | The supported decorator is retained. |
| Error reports formatted absent statistics as numbers | Empty categories use an absent-value marker with fixture coverage. |

Public documentation and generated report text are in English. Historical translated annotations and numerical records retain the [original snapshot provenance](../evidence/SNAPSHOT_MANIFEST.json). The frozen booster is byte-identical; new release records add evidence without rewriting historical experiment outcomes.

## Interpretation and reproduction limits

The historical booster retains an audited omission of some observed-versus-missing split candidates. Phase 34 evaluates the correction separately; the selected combined pipeline uses the preserved historical source. The imputation and preprocessing recipe changes the pipeline, rather than the booster source.

Data caches validate structure and row IDs rather than all CSV values. Use a fresh cache directory when data values change. Historical experiment controllers may require ignored local checkpoints and OOF arrays; the default selected training entry point and completed combined calibration driver are documented in the [project guide](../project/README.md).

No completed nested estimate exists for the exact combined pipeline. Full-train OOF F1 describes threshold calibration, and author-reported AIcrowd feedback informed selection. Reused development folds and leaderboard feedback introduce model-selection optimism. `HAREHAB1` contains post-event information; prospective use needs a different feature policy and new validation.
