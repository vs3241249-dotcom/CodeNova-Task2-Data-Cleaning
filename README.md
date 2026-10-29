# CodeNova Internship — Task 2: Data Cleaning Report

## Objective
Identify missing values, exact duplicates, inconsistent data types, and statistical outliers; document cleaning choices; and produce reproducible before-and-after data-quality metrics.

This project is designed to align with the CodeNova Data Science Batch 01 Task 2 specification.

## Features
- CSV and XLSX input support.
- Per-column missing-value profile and numeric statistical summaries.
- Conservative parsing for likely date and numeric columns.
- Whitespace/blank-value standardization.
- Exact duplicate-row detection and removal.
- Numeric median and categorical/text mode imputation where a non-missing value exists.
- IQR (1.5 × IQR) outlier flags before and after cleaning.
- Separate cleaned output; the original input is never overwritten.
- Automated before-and-after CSV reports and Markdown audit report.

## Project structure
```text
CodeNova_Task2_Data_Cleaning_Project/
├── data/
│   ├── raw/              # Place original dataset here; never overwrite it
│   └── cleaned/          # Generated cleaned CSV
├── reports/              # Generated comparison tables and audit report
├── outputs/
├── src/
│   └── clean_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup (Windows / VS Code)
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal → New Terminal.
4. Create and activate a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```
5. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Add your dataset
Copy the actual dataset from Project 1 into `data/raw/`. Do not edit or overwrite the original. Supported formats are `.csv` and `.xlsx`.

Example filename only (replace it with your actual filename):
`data/raw/Sample - Superstore.csv`

## Run
From the project root, run the command with the exact filename:
```bash
python src/clean_data.py "data/raw/Sample - Superstore.csv"
```
For an Excel file:
```bash
python src/clean_data.py "data/raw/your_actual_file.xlsx"
```
For a specific Excel sheet:
```bash
python src/clean_data.py "data/raw/your_actual_file.xlsx" --sheet "Sheet1"
```

## Generated deliverables
- `data/cleaned/cleaned_<filename>.csv`
- `reports/before_after_comparison.csv`
- `reports/missing_profile_before.csv`
- `reports/missing_profile_after.csv`
- `reports/numeric_summary_before.csv`
- `reports/numeric_summary_after.csv`
- `reports/outliers_iqr_before.csv`
- `reports/outliers_iqr_after.csv`
- `reports/data_quality_audit.md`
- `reports/run_summary.json`

## Actual Dataset Results

The cleaning script was executed on `Sample - Superstore.csv`.

| Metric | Before Cleaning | After Cleaning |
|---|---:|---:|
| Rows | 9,994 | 9,994 |
| Columns | 21 | 21 |
| Missing cells | 0 | 0 |
| Exact duplicate rows | 0 | 0 |

### Data Type Improvements
- `Order Date` was converted from string to datetime.
- `Ship Date` was converted from string to datetime.
- Other column types were reviewed and retained where appropriate.

### Outlier Analysis

The IQR method (1.5 × IQR) was used to flag potential outliers.

| Column | Outlier Flags |
|---|---:|
| Sales | 1,167 |
| Quantity | 170 |
| Discount | 856 |
| Profit | 1,881 |

Outliers were flagged for investigation and were not automatically removed, since extreme values may be valid business observations.

### Validation
- The cleaned dataset was saved separately from the original input.
- Before-and-after data-quality reports were generated.
- The original dataset was reported as unchanged by the cleaning script.
- Results should be reviewed against the business meaning of the data before final submission.

### Reproducibility

Run the following command from the project root:

```bash
python src/clean_data.py "data/raw/Sample - Superstore.csv"
```

The script generates a cleaned CSV, data-quality profiles, numeric summaries, IQR outlier reports, a comparison report, and an audit report.
## Cleaning rationale and limitations
- Exact duplicate rows are removed, retaining the first occurrence. Repeated IDs alone are not assumed to be duplicates.
- Blank/whitespace-only text cells become missing values.
- Obvious date columns are parsed only if most non-null values can be parsed. Numeric-looking text columns are converted only if at least 90% of non-blank values parse; ID-like columns are excluded from automatic numeric conversion.
- Numeric missing values are imputed with the median; categorical/text missing values with the mode when available. All-null columns remain missing. Date missing values are not automatically filled.
- Outliers are flagged using IQR, not automatically deleted. A statistical flag is not proof of an error.
- Review the generated audit report against the dataset's business meaning before submitting.

## Before submitting
- [ ] Confirm the script runs on your actual dataset.
- [ ] Review every transformation and its justification.
- [ ] Verify raw input is unchanged.
- [ ] Review before-and-after tables and audit report.
- [ ] Add screenshots of the successful run and generated report.
- [ ] Keep the GitHub repository Public.
- [ ] Never commit passwords, API keys, or private credentials.

## Dataset and Results

The project was executed on `Sample - Superstore.csv` containing 9,994 rows and 21 columns. The audit report records zero missing cells and zero exact duplicate rows before and after cleaning.

Date columns were converted to datetime, and potential outliers were flagged using the IQR method. Outliers were retained for review rather than automatically removed.

See `reports/data_quality_audit.md` and `reports/run_summary.json` for the recorded results. Review all transformations against the business meaning of the dataset before submission.
