# Dataset and preprocessing

## Task and source

The task is to classify myocardial infarction or coronary heart disease reported
in the **2015 Behavioral Risk Factor Surveillance System (BRFSS)** survey. The
challenge target is `_MICHD`. There are **328,135 labeled rows**: 28,975 positive
and 299,160 negative, for a positive prevalence of **8.83%**. The test set contains
109,379 unlabeled rows.

Use the four CSV files distributed by the
[EPFL Project 1 AIcrowd challenge](https://www.aicrowd.com/challenges/epfl-machine-learning-project-1),
as described in the [data guide](../data/README.md). Raw data is excluded from Git.
The included [2015 codebook](../official_material/project1/brfss_2015_codebook.txt)
and [feature registry](../configs/feature_metadata.json) document variable meanings
and response codes. Commands and relative runtime paths refer to `project/`.

## Measured properties

- There are 321 predictors plus `Id`; train and test predictors have the same order.
- **44.79% of training feature cells are blank.** Survey branching explains much
  of this missingness; a blank is not interchangeable with a zero quantity.
- No duplicate rows were found within train, within test, or across the two.
- Three train column pairs are exact duplicates. `CELLFON2` and `CTELNUM1`
  differ in test, so exclusions must consider semantics as well as train equality.

The [dataset audit](../results/eda/dataset_audit.json) records dimensions,
missingness, ID checks, file sizes and SHA-256 fingerprints. Further measured
outputs are stored under `project/results/eda/`.

## Historical cleaning foundation: Phase 14

The historical Phase 14 representation retains **295 source columns**. It
excludes identifiers, interview dates and survey-design fields, plus six named
columns: `CTELNUM1`, `CELLFON2`, `_AGEG5YR`, `WEIGHT2`, `HEIGHT3` and `HTIN4`.
The [Phase 14 plan](../configs/experiments/phase14_codebook_corrections_only.json)
and [cleaning implementation](../src/feature_preprocessing.py) define the exact
selection and transformations.

Documented nonresponses become `NaN` per variable. Documented zero-day codes
become zero, including `ALCDAY5=888` (no drinking) and `PHYSHLTH=88` /
`MENTHLTH=88` (zero days). Phase 14 corrects fourteen gaps in parsed nonresponse
meanings. Binary response mappings are fitted on the training partition and
applied unchanged to held-out rows. The tree transformation adds no intercept,
scaling or generic missingness indicators; the auxiliary missing-age option in
the shared plan is used by other preprocessing paths, including the linear
models and MLP.

Historical Phase 14 does not impute missing values. Its histogram trees learn
quantile bins on training rows and choose a missing-value direction at each
split. The frozen historical booster omits some valid observed-versus-missing
split candidates. Phase 34 evaluates the corrected search separately; the
selected final pipeline still uses the frozen historical source. See the
[technical report](FINAL_REPORT.md#split-search-comparison-phase-34).

## Selected final representation: diet exclusions and restricted imputation

[`configs/final_model.json`](../configs/final_model.json) selects
`combined18_24_l2_1`. It uses the Phase 14 cleaning foundation with two changes,
specified in the
[combined preprocessing plan](../configs/experiments/combined18_24_preprocessing.json):

1. **Diet representation from Phase 18.** Remove six raw frequency columns that
   mix day, week and month codes: `FRUITJU1`, `FRUIT1`, `FVBEANS`, `FVGREEN`,
   `FVORANG` and `VEGETAB1`. Retain their already available BRFSS-derived daily
   counterparts: `FTJUDA1_`, `FRUTDA1_`, `BEANDAY_`, `GRENDAY_`, `ORNGDAY_` and
   `VEGEDA1_`. No new frequency conversion is fitted. This leaves **289 source
   columns**.
2. **Restricted feature-only imputation from Phase 24.** Fill documented,
   unambiguous unknown/refused codes only in `INCOME2`, `PNEUVAC3` and `EMPLOY1`;
   predict raw blank height (`HTM4`) and weight (`WTKG3`); then reconstruct
   missing `_BMI5` from completed height and weight when both are positive and
   the result is within the observed training BMI range. Observed values remain
   unchanged. Other blanks, including skipped or unasked questionnaire items,
   remain `NaN`. Combined labels such as “Don't know/Refused/Missing” are not
   treated as unambiguous questionnaire nonresponses.

The imputation step appends **eight indicators of the original state**:
`INCOME2__was_unknown`, `INCOME2__was_refused`, `PNEUVAC3__was_unknown`,
`PNEUVAC3__was_refused`, `EMPLOY1__was_refused`, `HTM4__was_blank`,
`WTKG3__was_blank` and `_BMI5__was_blank`. The model therefore receives
**297 transformed features**. These indicators retain the original quantile
binning recipe; this is distinct from the exact-binary-bin experiments.

The [imputation implementation](../src/conditional_imputation.py) fits anchor
bins and imputers only on the corresponding training partition, without the
disease label. It uses Naive Bayes for discrete responses and ridge regression
for height and weight. Learned imputers use the original cleaned anchors, so
one imputed feature is not fed into another learned imputer. BMI is derived
after height and weight completion. Remaining `NaN` values use tree routing.
The [imputation guide](IMPUTATION.md) describes the method and historical studies;
the combined plan is the authority for the final restricted recipe.

## What the recorded evaluations establish

The diet-only Phase 18 candidate had nested development F1 **0.441862**; the
original restricted-imputation Phase 24 candidate had **0.441791**, versus
**0.442155** for historical Phase 14. Neither individual change replaced Phase 14
under those nested comparisons. Their later combination was selected for the
highest displayed AIcrowd F1 among completed candidates with recorded feedback
at the **14 October 2026 release**. It has **no completed nested development
evaluation**.

For the selected combination, the threshold **0.21811010373987366** maximizes
F1 on pooled three-fold OOF probabilities over all 328,135 labeled rows, using
accuracy to break F1 ties. Each OOF fit learns preprocessing on its own training
rows. The resulting **0.443882381** F1 describes threshold calibration using
the same labels that selected the threshold. Author-reported AIcrowd feedback
is separately recorded as **F1 0.455 / accuracy 0.882** on **13 October 2026**.
See the [selected submission record](../results/eda/final_combined18_24_submission.json)
and [results guide](../../docs/RESULTS.md) for evidence and selection limits.

## Interpretation and remaining representation limits

`HAREHAB1` asks about outpatient rehabilitation after a heart attack and remains
in the final pipeline. All 620 development rows with a recorded response code
are positive. In the historical Phase 14 ablation, removing this feature lowered
nested F1 from **0.442155** to **0.431039**; this was not an ablation of the final
combination. Its post-event information makes this a survey classification
task, without established prospective clinical validity. See the
[HAREHAB1 analysis](FINAL_REPORT.md#harehab1).

Some raw frequency and nominal activity codes remain numeric. Isolated removal
of `ALCDAY5` in Phase 28 gave nested F1 **0.440535** and was not adopted;
exercise-frequency replacement remains deferred. Feature-specific zero mappings
are still required when `555=Never` or `888=Never` labels are not recognized by
the metadata parser; there is no global substitution for those codes.
`EXRACT11` and `EXRACT21` are nominal activity codes. Phase 22 tested one-hot
encoding with exact binary bins (nested F1 **0.440570**) and was not adopted.
These are historical comparisons, not separate evaluations of the final
combined representation. See the [experiment history](EXPERIMENTS.md);
the MLP has its own conversions and one-hot encoding in [MLP.md](MLP.md).
