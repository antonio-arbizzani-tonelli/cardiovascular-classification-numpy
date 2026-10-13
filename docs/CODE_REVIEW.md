# Code review and verification

The portfolio copy was reviewed against the final **Phase 14** configuration, recorded evaluation protocols and existing test contracts. `configs/final_model.json` and `run.py` select `src/numpy_boosting_phase14.py`; Phase 34 is a separate comparison. The review covers the root entry points, linear implementations, every `src/` module, every `tools/` module, configurations and CI. Static checks cover all published Python files; execution uses synthetic fixtures and bounded checks.

## Corrections in the portfolio copy

| Issue | Correction |
| --- | --- |
| Logged CV rejected the selected Phase 14 implementation keyword | The wrapper forwards the selector and records the selected source fingerprint. A regression exercises the final suite, corrected Phase 34 and the default selector without expensive training. |
| Five historical launchers used a Windows-only subprocess flag unconditionally | The launchers use the available flag on Windows and zero elsewhere, matching the other controllers. A mocked non-Windows check verifies the launch argument. |
| Two analysis scripts passed a Python 3.10-only keyword to `Path.write_text` | They now use `Path.open` with explicit UTF-8 and LF output, compatible with the official Python 3.9 target. |
| Error analysis formatted absent statistics as numbers when a confusion category was empty | Empty categories now display an absent-value marker. A synthetic end-to-end report test covers the case. |

Documentation and generated report text are in English. Four historical hypothesis annotations and the imputation decision table are translated; the copied ledger fingerprints are updated. Numerical outcomes and the frozen selected source are preserved. The [snapshot manifest](../evidence/SNAPSHOT_MANIFEST.json) records original and copied file hashes.

## Interpretation and reproduction limits

The final Phase 14 booster retains the known omission of some observed-versus-missing split candidates. Its frozen source reproduces the selected submission. Phase 34 evaluates a correction separately and was not adopted as the final model. Changing the Phase 14 source would break the recorded submission identity.

Data caches check structure and IDs rather than the full CSV content. When data values change, use a fresh cache directory even if shape and IDs stay the same. Historical experimental controllers may need ignored local checkpoints and OOF artifacts; the default final training entry point is documented separately.

Preprocessing and nested threshold fitting use their training partitions. The same development folds were reused across many model choices, and AIcrowd feedback contributed to final selection. Threshold nesting does not eliminate that model-selection optimism. `HAREHAB1` contains post-event information; prospective use requires a different feature policy and validation study.

**All 213 tests pass in the assembled portfolio copy and in the clean publication package.** The baseline audit passed 206 project tests and 26 applicable public course tests. This portfolio adds regressions for logged model selection, report output, Python 3.9 compatibility and publication boundaries. Repository verification also passes: 97 Python files, 281 JSON files and 114 indexed record hashes. The final checks are recorded in [VERIFICATION.json](../evidence/VERIFICATION.json). Local execution uses Python 3.14.3, NumPy 2.4.2 and Matplotlib 3.10.8. [GitHub CI passed](https://github.com/antonio-arbizzani-tonelli/cardiovascular-classification-numpy/actions/runs/38324436873) with Python 3.9 / NumPy 1.23.1, including repository verification, all tests and entry-point checks.

Full training and the challenge submission were not repeated during this portfolio review. The checks support the documented behavior and reviewed contracts; they do not establish that every possible input is bug-free.
