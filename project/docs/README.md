# Technical documentation

This is the runnable implementation of the EPFL Machine Learning CS-433
project. Start with the [portfolio overview](../../README.md)
for the result story and the [project guide](../README.md) for setup and
reproduction.

The selected release pipeline combines **Phase 18 diet representation and
Phase 24 restricted imputation**, using the frozen Phase 14 booster and
[`configs/final_model.json`](../configs/final_model.json). Reported AIcrowd
F1 is **0.455**, accuracy **0.882**. Phase 14 remains the historical nested
reference; Phase 34 is a separate corrected-search comparison.

| Document | Purpose |
| --- | --- |
| [Technical results](FINAL_REPORT.md) | Methods, comparisons, limitations and links to numerical evidence |
| [DATA.md](DATA.md) | Dataset semantics and preprocessing |
| [EXPERIMENTS.md](EXPERIMENTS.md) | Evaluation protocols and experiment history |
| [MLP.md](MLP.md) | Neural preprocessing, training and reproduction |
| [IMPUTATION.md](IMPUTATION.md) | Imputation methods and measured outcomes |
| [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) | Retained settings, completed studies and future hypotheses |
| [Historical delivery checks](FINAL_AUDIT.md) | Original verification evidence and its limits |

[Results](../results/README.md) describes the stored analyses and records;
[configurations](../configs/README.md) identifies the reproduction settings.
The public package includes the project narrative and presentation; the
course-delivery PDF and LaTeX source are kept outside the public package.
