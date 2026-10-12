# Historical delivery checks — 12 October 2026

This document preserves the original course-delivery verification, rather than certifying later portfolio edits. The selected model is **historical Phase 14** with 295 features, 200 trees, depth 5 and threshold **0.2106169795070252**, calibrated on three-fold OOF predictions over all 328,135 labeled rows. Recorded AIcrowd feedback is **F1 0.452 and accuracy 0.878**, reported by the project author. The [final record](../results/eda/final_phase14_submission.json) retains feedback provenance, parameters, calibration and the submission fingerprint. The coauthored course-delivery PDF and LaTeX source are archived outside the public package; [technical results](FINAL_REPORT.md) retain the methods and evidence.

## Model, results and reproduction

| Check | Result |
| --- | --- |
| Source selection | `run.py` and final CV select `src/numpy_boosting_phase14.py`, a byte-exact copy of the historical implementation |
| Source fingerprint | `6fede57915b07a6ea7675292833f8ad79269e665f09977bffd2a9562ce1aaf98`; Git preserves LF endings |
| Nested development F1 | 0.4421552272688187, with thresholds selected in inner folds |
| Submission threshold | 0.2106169795070252 from three-fold OOF predictions over all training rows; preprocessing fitted within each training fold |
| Calibration F1 | 0.44276954874267993; labels also select the threshold, so this is not an independent test |
| Full-model reproduction | Final checkpoint loaded through the normal Phase 14 module; rebuilt train/test matrices matched; maximum probability difference 0 |
| CSV reproduction | Same SHA-256 as the selected submission: `8583daf81f7afb378eef3eafdfefd988ce85f78de8d58d38cd8ca39e1faa0df1` |
| CSV writer | `create_csv_submission` in `helpers.py`, adapted from EPFL with explicit UTF-8 and LF; `run.py` validates shapes and label domain |
| Counts and schema | 109,379 unique IDs in official sample order; 14,746 positives and 94,633 negatives; `Id,Prediction` header and −1/+1 labels |
| Input data | Nine CSV/cache fingerprints checked before replay |
| Training entry point | End-to-end fixture test of normal `run_pipeline`, Phase 14 checkpoint creation and submission output |

Full training of both implementations had already completed: six OOF fits and two full-data fits, using identical parameters and folds. Replay checked these models and the final pipeline without repeating expensive fits. `configs/experiments/final_phase14_validation.json` reproduces historical CV without ignored local source copies.

Phase 34 retains the observed-versus-missing split correction. Leaderboard feedback contributed to the choice between the two submissions. The technical results separate development, calibration and AIcrowd metrics; no numerical Phase 34 AIcrowd score was supplied.

## Original GitHub-package verification

- **206 project tests passed** in the working tree and in a copy containing only Git-eligible files, without data, caches or checkpoints.
- **26 public course tests passed** against the delivery copy. The URL check was excluded because it used a local path and needs the published commit. Black was excluded because the official tests mark it optional.
- The six `implementations.py` functions passed official signature, docstring, loss and update checks. GD/SGD, least squares, ridge and logistic regression use NumPy.
- `tools.verify_repository` checked Python 3.9 syntax, JSON, local Markdown links, final configuration, frozen source and **114 record hashes** across five ledgers.
- Help commands for `run.py`, `run_mlp.py`, `tools.prepare_data` and `tools.final_phase14_phase34` also worked in the clean copy.
- `git diff --check` passed. Models and preprocessing use NumPy and the standard library; Matplotlib supports analysis and plots.
- Data, caches, checkpoints, individual OOF predictions, logs and submissions were excluded. The original eligible package was approximately 21.5 MiB.
- A scan found no matches for private-key, GitHub/OpenAI-token or AWS-access-key patterns within the scope recorded in the [automated summary](../results/eda/final_phase14_readiness.json).
- The PDF compiled without errors or overflow warnings; both rendered pages were visually checked.

Local runs used **Python 3.14.3 / NumPy 2.4.2**. Parsing Python 3.9 syntax does not replace execution in the official runtime. CI is configured for Python 3.9 / NumPy 1.23.1. These historical checks do not certify every later portfolio edit.

The portfolio is a separate copy of the original course project. Experiment numeric outcomes remain intact; four archival annotations were translated and their copy-ledger hashes updated. At the portfolio root, `evidence/SNAPSHOT_MANIFEST.json` retains original commit provenance and source/copy fingerprints.

## Current portfolio verification

The [current code review](../../docs/CODE_REVIEW.md) records portfolio checks.
The active [root CI](../../.github/workflows/checks.yml) is configured for
Python 3.9 / NumPy 1.23.1; its result must be checked after publication.
The [portfolio overview](../../README.md) links to the runnable project,
results and presentation material.

Remote visibility was not verified during the historical audit. AIcrowd
feedback came from the author's message without a submission URL. Historical
JSON readiness summaries retain the paths of the original course package;
they describe that past check and do not require its report files to be part
of this public portfolio.

[Earlier audits](../results/eda/final_readiness.json) and the [Phase 34 check](../results/eda/phase34_repository_verification.json) remain dated evidence; they do not define the current final model.
