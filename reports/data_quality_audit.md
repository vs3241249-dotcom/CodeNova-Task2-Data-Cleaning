# Data Quality Audit Report — CodeNova Task 2

## 1. Project overview
- **Task:** Data Cleaning Report (Data Hygiene & Reproducibility)
- **Source file:** `Sample - Superstore.csv`
- **Generated:** 2026-10-29 08:57:36 India Standard Time
- **Input shape:** 9994 rows × 21 columns
- **Cleaned shape:** 9994 rows × 21 columns
- **Raw input modified:** No. The script reads the source and writes outputs to separate folders.

## 2. Initial data-quality profile

- Missing cells: **0**
- Exact duplicate rows: **0**
- Columns: **21**

### Per-column profile before cleaning
| column | dtype | missing_count | missing_percent | unique_non_null |
|---|---|---|---|---|
| Row ID | int64 | 0 | 0 | 9994 |
| Order ID | str | 0 | 0 | 5009 |
| Order Date | str | 0 | 0 | 1237 |
| Ship Date | str | 0 | 0 | 1334 |
| Ship Mode | str | 0 | 0 | 4 |
| Customer ID | str | 0 | 0 | 793 |
| Customer Name | str | 0 | 0 | 793 |
| Segment | str | 0 | 0 | 3 |
| Country | str | 0 | 0 | 1 |
| City | str | 0 | 0 | 531 |
| State | str | 0 | 0 | 49 |
| Postal Code | int64 | 0 | 0 | 631 |
| Region | str | 0 | 0 | 4 |
| Product ID | str | 0 | 0 | 1862 |
| Category | str | 0 | 0 | 3 |
| Sub-Category | str | 0 | 0 | 17 |
| Product Name | str | 0 | 0 | 1850 |
| Sales | float64 | 0 | 0 | 5825 |
| Quantity | int64 | 0 | 0 | 14 |
| Discount | float64 | 0 | 0 | 12 |
| Profit | float64 | 0 | 0 | 7287 |

### Numeric summary before cleaning
| column | count | mean | std | min | q1 | median | q3 | max |
|---|---|---|---|---|---|---|---|---|
| Row ID | 9994 | 4997.5 | 2885.1636 | 1 | 2499.25 | 4997.5 | 7495.75 | 9994 |
| Postal Code | 9994 | 55190.3794 | 32063.6934 | 1040 | 23223 | 56430.5 | 90008 | 99301 |
| Sales | 9994 | 229.858 | 623.2451 | 0.444 | 17.28 | 54.49 | 209.94 | 22638.48 |
| Quantity | 9994 | 3.7896 | 2.2251 | 1 | 2 | 3 | 5 | 14 |
| Discount | 9994 | 0.1562 | 0.2065 | 0 | 0 | 0.2 | 0.2 | 0.8 |
| Profit | 9994 | 28.6569 | 234.2601 | -6599.978 | 1.7288 | 8.6665 | 29.364 | 8399.976 |

### IQR outlier scan before cleaning
| column | method | lower_bound | upper_bound | outlier_count | outlier_percent | note |
|---|---|---|---|---|---|---|
| Row ID | IQR (1.5 × IQR) | -4995.5 | 14990.5 | 0 | 0 | Flag only; investigate before changing or removing values. |
| Postal Code | IQR (1.5 × IQR) | -76954.5 | 190185.5 | 0 | 0 | Flag only; investigate before changing or removing values. |
| Sales | IQR (1.5 × IQR) | -271.71 | 498.93 | 1167 | 11.68 | Flag only; investigate before changing or removing values. |
| Quantity | IQR (1.5 × IQR) | -2.5 | 9.5 | 170 | 1.7 | Flag only; investigate before changing or removing values. |
| Discount | IQR (1.5 × IQR) | -0.3 | 0.5 | 856 | 8.57 | Flag only; investigate before changing or removing values. |
| Profit | IQR (1.5 × IQR) | -39.7241 | 70.8169 | 1881 | 18.82 | Flag only; investigate before changing or removing values. |

## 3. Cleaning log and rationale

The following transformations were applied by the script. Review them against the meaning of your dataset before final submission.

- Trimmed surrounding whitespace from text values; original text case was retained.
- Parsed `Order Date` as datetime; 0 non-null value(s) failed conversion and became missing.
- Parsed `Ship Date` as datetime; 0 non-null value(s) failed conversion and became missing.
- No exact duplicate rows were found.

### Row handling
- Exact duplicate rows removed: **0**
- Fully empty rows removed: **0**
- Input rows: **9994**
- Output rows: **9994**

## 4. Before-and-after comparison

| column | dtype_before | dtype_after | missing_before | missing_after | missing_percent_before | missing_percent_after | unique_non_null_before | unique_non_null_after |
|---|---|---|---|---|---|---|---|---|
| Row ID | int64 | int64 | 0 | 0 | 0 | 0 | 9994 | 9994 |
| Order ID | str | string | 0 | 0 | 0 | 0 | 5009 | 5009 |
| Order Date | str | datetime64[us] | 0 | 0 | 0 | 0 | 1237 | 1237 |
| Ship Date | str | datetime64[us] | 0 | 0 | 0 | 0 | 1334 | 1334 |
| Ship Mode | str | string | 0 | 0 | 0 | 0 | 4 | 4 |
| Customer ID | str | string | 0 | 0 | 0 | 0 | 793 | 793 |
| Customer Name | str | string | 0 | 0 | 0 | 0 | 793 | 793 |
| Segment | str | string | 0 | 0 | 0 | 0 | 3 | 3 |
| Country | str | string | 0 | 0 | 0 | 0 | 1 | 1 |
| City | str | string | 0 | 0 | 0 | 0 | 531 | 531 |
| State | str | string | 0 | 0 | 0 | 0 | 49 | 49 |
| Postal Code | int64 | int64 | 0 | 0 | 0 | 0 | 631 | 631 |
| Region | str | string | 0 | 0 | 0 | 0 | 4 | 4 |
| Product ID | str | string | 0 | 0 | 0 | 0 | 1862 | 1862 |
| Category | str | string | 0 | 0 | 0 | 0 | 3 | 3 |
| Sub-Category | str | string | 0 | 0 | 0 | 0 | 17 | 17 |
| Product Name | str | string | 0 | 0 | 0 | 0 | 1850 | 1850 |
| Sales | float64 | float64 | 0 | 0 | 0 | 0 | 5825 | 5825 |
| Quantity | int64 | int64 | 0 | 0 | 0 | 0 | 14 | 14 |
| Discount | float64 | float64 | 0 | 0 | 0 | 0 | 12 | 12 |
| Profit | float64 | float64 | 0 | 0 | 0 | 0 | 7287 | 7287 |
| __DATASET_TOTALS__ |  |  | 0 | 0 | 0 | 0 |  |  |

### Per-column profile after cleaning
| column | dtype | missing_count | missing_percent | unique_non_null |
|---|---|---|---|---|
| Row ID | int64 | 0 | 0 | 9994 |
| Order ID | string | 0 | 0 | 5009 |
| Order Date | datetime64[us] | 0 | 0 | 1237 |
| Ship Date | datetime64[us] | 0 | 0 | 1334 |
| Ship Mode | string | 0 | 0 | 4 |
| Customer ID | string | 0 | 0 | 793 |
| Customer Name | string | 0 | 0 | 793 |
| Segment | string | 0 | 0 | 3 |
| Country | string | 0 | 0 | 1 |
| City | string | 0 | 0 | 531 |
| State | string | 0 | 0 | 49 |
| Postal Code | int64 | 0 | 0 | 631 |
| Region | string | 0 | 0 | 4 |
| Product ID | string | 0 | 0 | 1862 |
| Category | string | 0 | 0 | 3 |
| Sub-Category | string | 0 | 0 | 17 |
| Product Name | string | 0 | 0 | 1850 |
| Sales | float64 | 0 | 0 | 5825 |
| Quantity | int64 | 0 | 0 | 14 |
| Discount | float64 | 0 | 0 | 12 |
| Profit | float64 | 0 | 0 | 7287 |

### Numeric summary after cleaning
| column | count | mean | std | min | q1 | median | q3 | max |
|---|---|---|---|---|---|---|---|---|
| Row ID | 9994 | 4997.5 | 2885.1636 | 1 | 2499.25 | 4997.5 | 7495.75 | 9994 |
| Postal Code | 9994 | 55190.3794 | 32063.6934 | 1040 | 23223 | 56430.5 | 90008 | 99301 |
| Sales | 9994 | 229.858 | 623.2451 | 0.444 | 17.28 | 54.49 | 209.94 | 22638.48 |
| Quantity | 9994 | 3.7896 | 2.2251 | 1 | 2 | 3 | 5 | 14 |
| Discount | 9994 | 0.1562 | 0.2065 | 0 | 0 | 0.2 | 0.2 | 0.8 |
| Profit | 9994 | 28.6569 | 234.2601 | -6599.978 | 1.7288 | 8.6665 | 29.364 | 8399.976 |

### IQR outlier scan after cleaning
| column | method | lower_bound | upper_bound | outlier_count | outlier_percent | note |
|---|---|---|---|---|---|---|
| Row ID | IQR (1.5 × IQR) | -4995.5 | 14990.5 | 0 | 0 | Flag only; investigate before changing or removing values. |
| Postal Code | IQR (1.5 × IQR) | -76954.5 | 190185.5 | 0 | 0 | Flag only; investigate before changing or removing values. |
| Sales | IQR (1.5 × IQR) | -271.71 | 498.93 | 1167 | 11.68 | Flag only; investigate before changing or removing values. |
| Quantity | IQR (1.5 × IQR) | -2.5 | 9.5 | 170 | 1.7 | Flag only; investigate before changing or removing values. |
| Discount | IQR (1.5 × IQR) | -0.3 | 0.5 | 856 | 8.57 | Flag only; investigate before changing or removing values. |
| Profit | IQR (1.5 × IQR) | -39.7241 | 70.8169 | 1881 | 18.82 | Flag only; investigate before changing or removing values. |

**Outlier interpretation:** IQR results are flags for investigation, not proof of errors. This script does not automatically delete outliers because legitimate high/low values may be important. Any removal or capping should be justified with domain evidence and documented.

## 5. Validation and reproducibility

- Output was written separately from the raw input.
- Exact duplicate rows remaining after cleaning: **0**
- Missing cells after cleaning: **0**
- The script can be rerun with the same input file and dependencies to reproduce the outputs.
- Some missing values may remain intentionally, especially in all-null columns or date fields where automatic imputation would be misleading.

## 6. Limitations and review required

- Median imputation for numeric fields and mode imputation for categorical/text fields are baseline strategies, not universally correct choices.
- Validate all transformations against the dataset's business meaning. In particular, review ID-like fields, date columns, and any failed conversions.
- IQR outliers need investigation; do not remove them solely because they cross a statistical threshold.
- If the dataset has a meaningful unique key, define and document duplicate rules based on that key rather than assuming repeated identifiers are errors.

## 7. Generated files

- `data/cleaned/cleaned_<source-stem>.csv`
- `reports/before_after_comparison.csv`
- `reports/missing_profile_before.csv`
- `reports/missing_profile_after.csv`
- `reports/numeric_summary_before.csv`
- `reports/numeric_summary_after.csv`
- `reports/outliers_iqr_before.csv`
- `reports/outliers_iqr_after.csv`
- `reports/data_quality_audit.md`
- `reports/run_summary.json`

## 8. Execution command

```bash
python src/clean_data.py "data/raw/Sample - Superstore.csv"
```
