# Discrete binning audit — 30 September 2026

Phase 14 quantile bins merge values that could remain distinct within 64 bins. This affects 79–82 low-cardinality columns in outer training folds, including age, unhealthy days, hypertension and diabetes. Four columns lose every distinction between observed values; two of eight restricted Phase 16 indicators collapse. This establishes lost representation detail, not improved F1 from preserving it. A nested-threshold training comparison is needed.

The audit uses 295 features and all 262,508 development rows; the initial 20% validation partition is excluded. It reproduces Phase 14 preprocessing and `HistogramBinner` on three outer and six inner training partitions: outer seed 20260919, inner seed 20260922 plus outer-fold number. Quantiles and diagnostic activity vocabularies use training rows only. Six input hashes, labels, row order and saved OOF fold assignments match Phase 14. Counts of distinct finite values and occupied bins are also checked against transformed matrices; low cardinality means 2–64 observed finite values, including continuous fields with few sampled values. NaN remains state 255 throughout.

The eight indicators follow the actual restricted Phase 16 path with `fill_values=False` on unchanged Phase 14 source matrices. Activity one-hot is diagnostic only, with training-only categories and NaNs preserved. No predictive model or imputer is trained. Runtime is 74.1 seconds in Python 3.14.3 / NumPy 2.4.2; official Python 3.9 / NumPy 1.23.1 execution is not verified by this audit.

## Extent of merging

| Training | Rows | Columns with 2–64 values | Columns merging values | Columns merging all observed values |
| --- | ---: | ---: | ---: | ---: |
| Outer fold 1 | 175,005 | 245 | 79 | 4 |
| Outer fold 2 | 175,005 | 246 | 82 | 4 |
| Outer fold 3 | 175,006 | 245 | 79 | 4 |

Seventy-five columns are affected in every outer training fold; the union has 83. The six inner-training counts are 77, 76, 79, 76, 78 and 77. The same four columns lose all observed distinctions in all nine partitions. In outer fold 1, the 79 affected columns comprise 31 categorical, 29 count, 13 ordinal, 2 binary and 4 nominally continuous fields. These are column counts, not affected-person or classification-error counts.

| Feature | Distinct values in three outer training folds | Occupied bins in three outer training folds | Observation |
| --- | --- | --- | --- |
| `_AGE80` | 63 / 63 / 63 | 52 / 52 / 52 | Some ages merge despite capacity for all 63 values. |
| `PHYSHLTH` | 31 / 31 / 31 | 12 / 13 / 12 | Some counts from 0 to 30 days become indistinguishable. |
| `MENTHLTH` | 31 / 31 / 31 | 11 / 11 / 11 | Similar loss of day-count detail. |
| `BPHIGH4` | 4 / 4 / 4 | 3 / 3 / 3 | Codes 3 and 4 become indistinguishable. |
| `DIABETE3` | 4 / 4 / 4 | 3 / 3 / 3 | Codes 1 and 2 become indistinguishable. |
| `ALCDAY5` | 38 / 38 / 37 | 18 / 18 / 18 | Many frequencies merge. |
| `DROCDY3_` | 35 / 35 / 34 | 18 / 17 / 18 | The uniform-frequency derived field also loses values. |
| `_STATE` | 53 / 53 / 53 | 47 / 47 / 47 | Some numerical region codes merge. |

In fold 1, `BPHIGH4=3` merges 101,182 No responses with 1,722 borderline/pre-hypertension responses (`4`); their positive counts are 3,803 and 112. `DIABETE3=1` merges 22,564 Yes responses with 1,419 pregnancy-only responses (`2`), with 4,981 and 62 positives. Code `2` is verified against the codebook because it is absent from the JSON registry. These are descriptive comparisons, not proof that separation helps classification. `_AGE80` merges ages 78/79 and several younger pairs; JSON lists all merges. `GENHLTH` keeps five values, `INCOME2` eight and `HAREHAB1` two: the issue does not affect every feature.

## Columns and indicators losing all observed distinctions

| Feature | Values after preprocessing | Minority-value rows in three outer training folds |
| --- | --- | --- |
| `PVTRESD1` | 0 e 1 | 11 / 20 / 15 |
| `PVTRESD2` | 0 e 1 | 436 / 405 / 447 |
| `_FRUITEX` | 0 e 2 | 35 / 34 / 37 |
| `_VEGETEX` | 0 e 2 | 18 / 15 / 21 |

Observed responses merge but NaNs remain separate, so response availability may still carry information. Rare-value preservation alone does not imply a large F1 gain.

| Collapsed indicator | Rows equal to 1 in three outer training folds | Training-row frequency |
| --- | --- | --- |
| `EMPLOY1__was_refused` | 1,475 / 1,517 / 1,508 | 0.843–0.867% |
| `PNEUVAC3__was_refused` | 856 / 797 / 819 | 0.455–0.489% |

Six of eight indicators preserve both states in all nine partitions: two income flags, `PNEUVAC3__was_unknown`, height/weight blank flags and the BMI blank flag. The two listed flags become constant. This limits indicator comparisons with the current binner without quantifying their F1 contribution.

## Activity one-hot diagnostic

`EXRACT11` has 75 categories in each outer training partition but 20 occupied bins. `EXRACT21` has 76 categories and 25/25/24 bins. Both exceed the proposed exact-binning limit of 64, so preserving smaller-cardinality fields does not directly solve their nominal encoding.

| Training | `EXRACT11`: collapsed / total indicators | `EXRACT21`: collapsed / total indicators |
| --- | ---: | ---: |
| Outer fold 1 | 64 / 75 | 63 / 76 |
| Outer fold 2 | 64 / 75 | 62 / 76 |
| Outer fold 3 | 64 / 75 | 63 / 76 |

Collapsed indicators in fold 1 correspond to 15,508 `EXRACT11` and 18,581 `EXRACT21` observed responses, counted by feature rather than unique people. Of these indicators, 22 and 23 have at least 200 positive responses. Preserved states are still subject to the minimum 200 rows per leaf, missing-value handling and feature sampling.

## Follow-up

The historical proposal was to preserve every observed finite value at cardinality at most 64, retain quantiles elsewhere and keep NaNs separate; hold 295 features and other parameters fixed and reselect thresholds within inner folds. Unseen values and 64-to-65-cardinality changes require deterministic handling. Later one-hot/indicator tests must preserve binary states and use matched controls.

No booster change or training comparison occurred during this audit. [Phase 20](phase20_binning_summary.md) and [Phase 21](phase21_preprocessing_summary.md) later tested exact bins; [Phase 22](phase22_preprocessing_summary.md) tested activity one-hot and [Phase 23](phase23_missing_reason_flags_summary.md) nonresponse indicators. None was adopted; historical Phase 14 remains the reference at nested F1 0.44216.

- [Complete results and hashes](discrete_binning_audit.json).
- [295-feature table for nine partitions](discrete_binning_features.csv).
- [Reproduction utility](../../tools/audit_discrete_binning.py).
- [Audited implementation](../../src/numpy_boosting.py).
- [DIABETE3 codebook](../../official_material/project1/brfss_2015_codebook.txt).
