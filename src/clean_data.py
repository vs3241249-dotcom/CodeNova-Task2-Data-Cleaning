#!/usr/bin/env python3
"""
CodeNova Data Science Internship — Task 2: Data Cleaning Report

Run from the project root:
    python src/clean_data.py "data/raw/your_dataset.csv"
or:
    python src/clean_data.py "data/raw/your_dataset.xlsx"

The script never writes to or overwrites the raw input file.
It creates cleaned data, profiling outputs, before/after metrics, and an audit report.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATE_HINTS = ("date", "time", "timestamp", "dob", "birth")
ID_HINTS = ("id", "zip", "postal", "phone", "code")


def read_dataset(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        # Try common encodings without modifying the original file.
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
            try:
                return pd.read_csv(path, encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode CSV. Try saving a copy as UTF-8 CSV.")
    if suffix in (".xlsx", ".xls"):
        if suffix == ".xls":
            raise ValueError("For .xls files, save a copy as .xlsx or CSV first.")
        return pd.read_excel(path, sheet_name=sheet_name or 0)
    raise ValueError("Unsupported file type. Please use .csv or .xlsx.")


def safe_name(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_") or "column"


def missing_profile(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    return pd.DataFrame({
        "column": df.columns.astype(str),
        "dtype": [str(t) for t in df.dtypes],
        "missing_count": [int(v) for v in df.isna().sum().values],
        "missing_percent": [
            round(float(v) / total * 100, 2) if total else 0.0
            for v in df.isna().sum().values
        ],
        "unique_non_null": [int(v) for v in df.nunique(dropna=True).values],
    })


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        return pd.DataFrame(columns=[
            "column", "count", "mean", "std", "min", "q1", "median", "q3", "max"
        ])
    desc = numeric.describe().T
    out = pd.DataFrame({
        "column": desc.index.astype(str),
        "count": desc["count"].values,
        "mean": desc["mean"].values,
        "std": desc["std"].values,
        "min": desc["min"].values,
        "q1": desc["25%"].values,
        "median": desc["50%"].values,
        "q3": desc["75%"].values,
        "max": desc["max"].values,
    })
    return out.round(4)


def iqr_outlier_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.select_dtypes(include=[np.number]).columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) < 4:
            rows.append({
                "column": str(col), "method": "IQR (1.5 × IQR)",
                "lower_bound": np.nan, "upper_bound": np.nan,
                "outlier_count": 0, "outlier_percent": 0.0,
                "note": "Too few non-null numeric observations for a useful IQR scan."
            })
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        count = int(((s < low) | (s > high)).sum())
        rows.append({
            "column": str(col), "method": "IQR (1.5 × IQR)",
            "lower_bound": float(low), "upper_bound": float(high),
            "outlier_count": count,
            "outlier_percent": round(count / len(s) * 100, 2) if len(s) else 0.0,
            "note": "Flag only; investigate before changing or removing values."
        })
    return pd.DataFrame(rows, columns=[
        "column", "method", "lower_bound", "upper_bound",
        "outlier_count", "outlier_percent", "note"
    ])


def convert_obvious_types(df: pd.DataFrame, log: list[str]) -> pd.DataFrame:
    """Conservative conversion: only attempt conversions when column names suggest the type."""
    result = df.copy()
    for col in result.columns:
        name = str(col).strip().lower()
        if any(hint in name for hint in DATE_HINTS):
            original_non_null = result[col].notna().sum()
            if original_non_null:
                converted = pd.to_datetime(result[col], errors="coerce")
                converted_non_null = converted.notna().sum()
                # Accept only if at least 80% of non-null values parse successfully.
                if converted_non_null / original_non_null >= 0.80:
                    failed = int(original_non_null - converted_non_null)
                    result[col] = converted
                    log.append(
                        f"- Parsed `{col}` as datetime; {failed} non-null value(s) failed conversion and became missing."
                    )
        elif not any(hint in name for hint in ID_HINTS) and (pd.api.types.is_object_dtype(result[col]) or pd.api.types.is_string_dtype(result[col])):
            cleaned = result[col].astype("string").str.strip()
            # Recognize common quantitative field names so malformed values can be flagged
            # as missing rather than causing an entire numeric column to remain text.
            numeric_hints = ("sales", "profit", "quantity", "qty", "discount", "amount", "price", "cost", "revenue", "age", "score", "rate", "total", "count", "units", "margin")
            candidate = pd.to_numeric(cleaned.str.replace(",", "", regex=False), errors="coerce")
            non_blank = cleaned.notna() & cleaned.ne("")
            denom = int(non_blank.sum())
            ratio = (candidate[non_blank].notna().sum() / denom) if denom else 0.0
            if denom and (ratio >= 0.90 or any(hint in name for hint in numeric_hints) and ratio >= 0.50):
                failed = int((non_blank & candidate.isna()).sum())
                result[col] = candidate
                log.append(
                    f"- Converted `{col}` to numeric; {failed} non-blank value(s) failed numeric parsing and became missing."
                )
            else:
                # Trim text only; preserve original case because case may be meaningful.
                result[col] = cleaned
    return result


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, int]]:
    log: list[str] = []
    counts = {
        "input_rows": int(len(raw)),
        "input_columns": int(len(raw.columns)),
        "exact_duplicate_rows_removed": 0,
        "blank_strings_converted_to_missing": 0,
        "rows_dropped_for_all_missing": 0,
    }
    df = raw.copy(deep=True)

    # Standardize column labels for reliable access while preserving meaning.
    original_cols = list(df.columns)
    df.columns = [str(c).strip() for c in df.columns]
    if list(df.columns) != [str(c) for c in original_cols]:
        log.append("- Trimmed leading/trailing whitespace from column names.")

    # Convert blank-only strings to NA and trim surrounding whitespace in text.
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            before = int(df[col].isna().sum())
            s = df[col].astype("string").str.strip()
            s = s.replace("", pd.NA)
            after = int(s.isna().sum())
            counts["blank_strings_converted_to_missing"] += max(0, after - before)
            df[col] = s
    if counts["blank_strings_converted_to_missing"]:
        log.append(
            f"- Converted {counts['blank_strings_converted_to_missing']} blank/whitespace-only text cell(s) to missing values."
        )
    log.append("- Trimmed surrounding whitespace from text values; original text case was retained.")

    # Conservative type parsing for obvious date/numeric columns.
    df = convert_obvious_types(df, log)

    # Exact row duplicates only; do not drop repeated IDs without evidence.
    duplicate_mask = df.duplicated(keep="first")
    duplicate_count = int(duplicate_mask.sum())
    if duplicate_count:
        df = df.loc[~duplicate_mask].copy()
        counts["exact_duplicate_rows_removed"] = duplicate_count
        log.append(
            f"- Removed {duplicate_count} exact duplicate row(s), keeping the first occurrence. Repeated identifiers alone were not treated as duplicates."
        )
    else:
        log.append("- No exact duplicate rows were found.")

    # Remove completely empty rows; they contain no observations.
    all_missing = df.isna().all(axis=1) if len(df.columns) else pd.Series(False, index=df.index)
    empty_count = int(all_missing.sum())
    if empty_count:
        df = df.loc[~all_missing].copy()
        counts["rows_dropped_for_all_missing"] = empty_count
        log.append(f"- Removed {empty_count} fully empty row(s) because they contained no data.")

    # Impute remaining missing values using conservative, reproducible defaults.
    # Numeric: median. Non-numeric: mode. All-null columns are retained unchanged.
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing == 0:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            median = series.median(skipna=True)
            if pd.notna(median):
                df[col] = series.fillna(median)
                log.append(
                    f"- Imputed {missing} missing value(s) in numeric column `{col}` with the column median ({median}). Median is robust to skew/outliers."
                )
            else:
                log.append(
                    f"- Left `{col}` unchanged because it has no usable numeric values; missing values remain."
                )
        elif pd.api.types.is_datetime64_any_dtype(series):
            # No automatic datetime imputation: a fabricated date can be misleading.
            log.append(
                f"- Left missing values in datetime column `{col}` unchanged because filling dates without domain context could introduce false information."
            )
        else:
            modes = series.mode(dropna=True)
            if len(modes):
                mode_value = modes.iloc[0]
                df[col] = series.fillna(mode_value)
                log.append(
                    f"- Imputed {missing} missing value(s) in categorical/text column `{col}` with the mode ({str(mode_value)!r}). This is a baseline choice; assess whether it suits the field."
                )
            else:
                log.append(
                    f"- Left `{col}` unchanged because every value is missing; no defensible mode exists."
                )

    # Reindex output after dropped rows.
    df = df.reset_index(drop=True)
    return df, log, counts


def make_comparison(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    raw_profile = missing_profile(raw).set_index("column")
    clean_profile = missing_profile(clean).set_index("column")
    columns = list(dict.fromkeys(list(map(str, raw.columns)) + list(map(str, clean.columns))))
    rows = []
    for col in columns:
        b = raw_profile.loc[col] if col in raw_profile.index else None
        a = clean_profile.loc[col] if col in clean_profile.index else None
        rows.append({
            "column": col,
            "dtype_before": str(b["dtype"]) if b is not None else "not present",
            "dtype_after": str(a["dtype"]) if a is not None else "not present",
            "missing_before": int(b["missing_count"]) if b is not None else 0,
            "missing_after": int(a["missing_count"]) if a is not None else 0,
            "missing_percent_before": float(b["missing_percent"]) if b is not None else 0.0,
            "missing_percent_after": float(a["missing_percent"]) if a is not None else 0.0,
            "unique_non_null_before": int(b["unique_non_null"]) if b is not None else 0,
            "unique_non_null_after": int(a["unique_non_null"]) if a is not None else 0,
        })
    rows.append({
        "column": "__DATASET_TOTALS__",
        "dtype_before": "",
        "dtype_after": "",
        "missing_before": int(raw.isna().sum().sum()),
        "missing_after": int(clean.isna().sum().sum()),
        "missing_percent_before": round(float(raw.isna().sum().sum()) / max(raw.size, 1) * 100, 2),
        "missing_percent_after": round(float(clean.isna().sum().sum()) / max(clean.size, 1) * 100, 2),
        "unique_non_null_before": "",
        "unique_non_null_after": "",
    })
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "_No data available._"
    view = df.head(max_rows).copy()
    headers = [str(c) for c in view.columns]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, row in view.iterrows():
        vals = []
        for v in row.tolist():
            if pd.isna(v):
                text = ""
            elif isinstance(v, (float, np.floating)):
                text = f"{v:.4f}".rstrip("0").rstrip(".")
            else:
                text = str(v)
            vals.append(text.replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing first {max_rows} rows of {len(df)}._")
    return "\n".join(lines)


def write_audit_report(
    report_path: Path,
    source_path: Path,
    raw: pd.DataFrame,
    clean: pd.DataFrame,
    log: list[str],
    counts: dict[str, int],
    comparison: pd.DataFrame,
    outliers_before: pd.DataFrame,
    outliers_after: pd.DataFrame,
) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    raw_missing = int(raw.isna().sum().sum())
    clean_missing = int(clean.isna().sum().sum())
    raw_dups = int(raw.duplicated().sum())
    clean_dups = int(clean.duplicated().sum())
    numeric_before = numeric_summary(raw)
    numeric_after = numeric_summary(clean)

    content = f"""# Data Quality Audit Report — CodeNova Task 2

## 1. Project overview
- **Task:** Data Cleaning Report (Data Hygiene & Reproducibility)
- **Source file:** `{source_path.name}`
- **Generated:** {timestamp}
- **Input shape:** {len(raw)} rows × {len(raw.columns)} columns
- **Cleaned shape:** {len(clean)} rows × {len(clean.columns)} columns
- **Raw input modified:** No. The script reads the source and writes outputs to separate folders.

## 2. Initial data-quality profile

- Missing cells: **{raw_missing}**
- Exact duplicate rows: **{raw_dups}**
- Columns: **{len(raw.columns)}**

### Per-column profile before cleaning
{md_table(missing_profile(raw))}

### Numeric summary before cleaning
{md_table(numeric_before)}

### IQR outlier scan before cleaning
{md_table(outliers_before)}

## 3. Cleaning log and rationale

The following transformations were applied by the script. Review them against the meaning of your dataset before final submission.

{chr(10).join(log) if log else "- No transformations were needed."}

### Row handling
- Exact duplicate rows removed: **{counts.get('exact_duplicate_rows_removed', 0)}**
- Fully empty rows removed: **{counts.get('rows_dropped_for_all_missing', 0)}**
- Input rows: **{counts.get('input_rows', len(raw))}**
- Output rows: **{len(clean)}**

## 4. Before-and-after comparison

{md_table(comparison)}

### Per-column profile after cleaning
{md_table(missing_profile(clean))}

### Numeric summary after cleaning
{md_table(numeric_after)}

### IQR outlier scan after cleaning
{md_table(outliers_after)}

**Outlier interpretation:** IQR results are flags for investigation, not proof of errors. This script does not automatically delete outliers because legitimate high/low values may be important. Any removal or capping should be justified with domain evidence and documented.

## 5. Validation and reproducibility

- Output was written separately from the raw input.
- Exact duplicate rows remaining after cleaning: **{clean_dups}**
- Missing cells after cleaning: **{clean_missing}**
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
python src/clean_data.py "data/raw/{source_path.name}"
```
"""
    report_path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reproducible data cleaning and generate a data quality audit.")
    parser.add_argument("input_file", help="Path to input .csv or .xlsx file")
    parser.add_argument("--sheet", default=None, help="Optional Excel sheet name (defaults to first sheet)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    input_path = Path(args.input_file)
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        print('Place your file in data/raw/ and pass its path, e.g. python src/clean_data.py "data/raw/my_data.csv"', file=sys.stderr)
        return 2

    raw = read_dataset(input_path, args.sheet)
    if raw.empty:
        print("ERROR: Dataset has no rows. Please check the source file.", file=sys.stderr)
        return 2

    cleaned, log, counts = clean_data(raw)
    source_stem = safe_name(input_path.stem)
    cleaned_dir = project_root / "data" / "cleaned"
    reports_dir = project_root / "reports"
    outputs_dir = project_root / "outputs"
    for folder in (cleaned_dir, reports_dir, outputs_dir):
        folder.mkdir(parents=True, exist_ok=True)

    cleaned_path = cleaned_dir / f"cleaned_{source_stem}.csv"
    cleaned.to_csv(cleaned_path, index=False, encoding="utf-8-sig")

    comparison = make_comparison(raw, cleaned)
    comparison.to_csv(reports_dir / "before_after_comparison.csv", index=False)
    missing_profile(raw).to_csv(reports_dir / "missing_profile_before.csv", index=False)
    missing_profile(cleaned).to_csv(reports_dir / "missing_profile_after.csv", index=False)
    numeric_summary(raw).to_csv(reports_dir / "numeric_summary_before.csv", index=False)
    numeric_summary(cleaned).to_csv(reports_dir / "numeric_summary_after.csv", index=False)
    out_before = iqr_outlier_profile(raw)
    out_after = iqr_outlier_profile(cleaned)
    out_before.to_csv(reports_dir / "outliers_iqr_before.csv", index=False)
    out_after.to_csv(reports_dir / "outliers_iqr_after.csv", index=False)

    write_audit_report(
        reports_dir / "data_quality_audit.md", input_path, raw, cleaned,
        log, counts, comparison, out_before, out_after
    )
    summary = {
        "source_file": str(input_path),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "input_rows": int(len(raw)),
        "input_columns": int(len(raw.columns)),
        "output_rows": int(len(cleaned)),
        "output_columns": int(len(cleaned.columns)),
        "missing_cells_before": int(raw.isna().sum().sum()),
        "missing_cells_after": int(cleaned.isna().sum().sum()),
        "exact_duplicate_rows_before": int(raw.duplicated().sum()),
        "exact_duplicate_rows_after": int(cleaned.duplicated().sum()),
        "cleaned_file": str(cleaned_path.relative_to(project_root)),
        "audit_report": "reports/data_quality_audit.md",
        "note": "Review transformations and IQR flags against domain meaning before submission."
    }
    (reports_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nTASK 2 DATA CLEANING COMPLETED")
    print(f"Input rows/columns: {len(raw)} / {len(raw.columns)}")
    print(f"Output rows/columns: {len(cleaned)} / {len(cleaned.columns)}")
    print(f"Missing cells before/after: {raw.isna().sum().sum()} / {cleaned.isna().sum().sum()}")
    print(f"Exact duplicate rows before/after: {raw.duplicated().sum()} / {cleaned.duplicated().sum()}")
    print(f"Cleaned dataset: {cleaned_path}")
    print(f"Audit report: {reports_dir / 'data_quality_audit.md'}")
    print(f"Comparison table: {reports_dir / 'before_after_comparison.csv'}")
    print("\nPlease review the audit report and confirm each cleaning choice makes sense for your dataset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
