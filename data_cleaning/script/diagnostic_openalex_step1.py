#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
diagnostic_openalex_step1.py

Step 1: Inspect & pre-check ALL OpenAlex journal files in a folder.

Input  : All TSV files in RAW_BASE matching "*_openalex.tsv"
Output :
  1) For each NAMEJOURNAL_openalex.tsv → NAMEJOURNAL_step1.tsv
     - Rows with at least one issue:
         * missing in:
             "Journal", "Title", "Type", "Language",
             "DOI", "OpenAlex_ID", "Referenced_Works", "Authors"
         * duplicates in:
             "Title", "DOI", "OpenAlex_ID"
         * structural anomalies:
             - Year out of [1980, 2024]
             - Type not in {"article", "review"} (case-insensitive)
     - All original columns
     - Plus diagnostic columns:
         __journal__
         __issue_type__   ("missing", "duplicate",
                           "year_out_of_range", "invalid_type",
                           or "no_issues_detected")
         __issue_field__  (which column)

  2) Global summary:
         step1_summary_all_journals.tsv
     one row per journal with:
         journal_id
         n_rows, n_cols
         has_Journal, has_Title, has_Type, has_Language,
         has_DOI, has_OpenAlex_ID, has_Referenced_Works, has_Authors, has_Year
         n_missing_<col> for each missing-check column
         n_duplicate_<col>_rows for each duplicate-check column
         n_invalid_year_rows
         n_invalid_type_rows
         any_issues
"""

import os
import glob
import pandas as pd
from typing import List, Dict

# --------------------
# Paths
# --------------------
RAW_BASE = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
OUTPUT_DIR = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\step_1"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Columns to check for MISSING values (blank / whitespace)
MISSING_COLS = [
    "Journal",
    "Title",
    "Type",
    "Language",
    "DOI",
    "OpenAlex_ID",
    "Referenced_Works",
    "Authors",
]

# Columns to check for DUPLICATES (non-empty only)
DUPLICATE_COLS = [
    "Title",
    "DOI",
    "OpenAlex_ID",
]

# Columns to show in preview at the end (if present)
PREVIEW_COLS = [
    "Journal",
    "Title",
    "DOI",
    "Year",
    "Type",
    "Language",
    "OpenAlex_ID",
    "Referenced_Works",
    "Authors",
]

# Container for per-journal summary rows
SUMMARY_ROWS: List[Dict] = []


def find_nonempty_duplicates(df: pd.DataFrame, colname: str) -> pd.Series:
    """
    Return a boolean mask of rows that are duplicates in the given column,
    considering only non-empty values.
    """
    if colname not in df.columns:
        return pd.Series([False] * len(df), index=df.index)

    s = df[colname].fillna("").map(lambda x: x.strip())
    mask_nonempty = s != ""
    mask_dupe = s.duplicated(keep=False) & mask_nonempty
    return mask_dupe


def process_one_file(path: str):
    fname = os.path.basename(path)

    if not fname.endswith("_openalex.tsv"):
        print(f"Skipping (does not match *_openalex.tsv): {fname}")
        return

    journal_id = fname[:-len("_openalex.tsv")]
    print(f"\n=== Processing journal: {journal_id} ===")
    print(f"Input file: {path}")

    # ---- Load ----
    try:
        df = pd.read_csv(
            path,
            sep="\t",
            dtype=str,
            na_filter=False,
            engine="python",
        )
    except Exception as e:
        print(f"❌ Error reading file {fname}: {e}")
        return

    n_rows, n_cols = df.shape
    print(f"Loaded: {n_rows:,} rows | {n_cols:,} columns.")

    # ---- Per-journal summary dict ----
    summary: Dict[str, object] = {
        "journal_id": journal_id,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "has_Journal": "Journal" in df.columns,
        "has_Title": "Title" in df.columns,
        "has_Type": "Type" in df.columns,
        "has_Language": "Language" in df.columns,
        "has_DOI": "DOI" in df.columns,
        "has_OpenAlex_ID": "OpenAlex_ID" in df.columns,
        "has_Referenced_Works": "Referenced_Works" in df.columns,
        "has_Authors": "Authors" in df.columns,
        "has_Year": "Year" in df.columns,
        "n_invalid_year_rows": 0,
        "n_invalid_type_rows": 0,
        "any_issues": False,
    }

    # Initialise missing counters
    for col in MISSING_COLS:
        summary[f"n_missing_{col}"] = 0

    # Initialise duplicate counters
    for col in DUPLICATE_COLS:
        summary[f"n_duplicate_{col}_rows"] = 0

    # ---- Prepare container for issue rows ----
    issues = []

    # ---- Missing data checks ----
    print("Checking missing values...")
    for col in MISSING_COLS:
        if col not in df.columns:
            print(f"- {col}: NOT PRESENT in this file.")
            continue

        empty_mask = df[col].map(lambda x: isinstance(x, str) and x.strip() == "")
        n_empty = empty_mask.sum()
        n_non_empty = len(df) - n_empty
        print(f"- {col}: {n_empty} empty / {n_non_empty} non-empty")

        summary[f"n_missing_{col}"] = int(n_empty)

        if n_empty > 0:
            summary["any_issues"] = True
            subset = df[empty_mask].copy()
            subset["__journal__"] = journal_id
            subset["__issue_type__"] = "missing"
            subset["__issue_field__"] = col
            issues.append(subset)

    # ---- Duplicate checks ----
    print("Checking duplicates...")
    for col in DUPLICATE_COLS:
        dup_mask = find_nonempty_duplicates(df, col)
        n_dup_rows = dup_mask.sum()
        summary[f"n_duplicate_{col}_rows"] = int(n_dup_rows)

        if n_dup_rows > 0:
            summary["any_issues"] = True
            subset = df[dup_mask].copy()
            subset["__journal__"] = journal_id
            subset["__issue_type__"] = "duplicate"
            subset["__issue_field__"] = col
            issues.append(subset)
            print(f"- Duplicate {col}: {n_dup_rows} rows involved.")
        else:
            print(f"- No duplicate {col} values.")

    # ---- Structural anomalies: Year range ----
    if "Year" in df.columns:
        print("Checking Year range (1980–2024)...")
        def year_out_of_range(val: str) -> bool:
            s = str(val).strip()
            if not s:
                # empty Year is NOT treated as structural anomaly here
                return False
            if not s.isdigit() or len(s) != 4:
                return True
            y = int(s)
            return not (1980 <= y <= 2024)

        year_mask = df["Year"].map(year_out_of_range)
        n_invalid_year = year_mask.sum()
        summary["n_invalid_year_rows"] = int(n_invalid_year)

        if n_invalid_year > 0:
            summary["any_issues"] = True
            subset = df[year_mask].copy()
            subset["__journal__"] = journal_id
            subset["__issue_type__"] = "year_out_of_range"
            subset["__issue_field__"] = "Year"
            issues.append(subset)
            print(f"- Year out of range / invalid: {n_invalid_year} rows.")
        else:
            print("- All non-empty Year values within 1980–2024 or valid format.")
    else:
        print("Year column not present; skipping Year range check.")

    # ---- Structural anomalies: Type values ----
    if "Type" in df.columns:
        print('Checking Type ∈ {"article", "review"}...')
        valid_types = {"article", "review"}

        def invalid_type(val: str) -> bool:
            s = str(val).strip()
            if not s:
                # empty Type is treated as "missing" only, not as structural anomaly
                return False
            return s.lower() not in valid_types

        type_mask = df["Type"].map(invalid_type)
        n_invalid_type = type_mask.sum()
        summary["n_invalid_type_rows"] = int(n_invalid_type)

        if n_invalid_type > 0:
            summary["any_issues"] = True
            subset = df[type_mask].copy()
            subset["__journal__"] = journal_id
            subset["__issue_type__"] = "invalid_type"
            subset["__issue_field__"] = "Type"
            issues.append(subset)
            print(f"- Invalid Type values (not article/review): {n_invalid_type} rows.")
        else:
            print("- All non-empty Type values are article/review.")
    else:
        print("Type column not present; skipping Type validity check.")

    # ---- Combine all issues for this journal ----
    if issues:
        issues_df = pd.concat(issues, ignore_index=True)
        # Drop exact duplicate rows in the issue report
        issues_df = issues_df.drop_duplicates()
        out_path = os.path.join(OUTPUT_DIR, f"{journal_id}_step1.tsv")
        issues_df.to_csv(out_path, sep="\t", index=False)
        print(f"💾 Saved diagnostic file for {journal_id}:\n    {out_path}")
        print(f"Rows with issues: {len(issues_df):,}")
    else:
        # Create a small "no issues" file so you know it was processed
        out_path = os.path.join(OUTPUT_DIR, f"{journal_id}_step1.tsv")
        no_issue_df = pd.DataFrame(
            [{
                "__journal__": journal_id,
                "__issue_type__": "no_issues_detected",
                "__issue_field__": "",
            }]
        )
        no_issue_df.to_csv(out_path, sep="\t", index=False)
        print(f"✅ No issues detected for {journal_id}.")
        print(f"💾 Created summary file:\n    {out_path}")

    # ---- Small preview (optional) ----
    print("Preview of first 3 rows (key columns if present):")
    cols_preview = [c for c in PREVIEW_COLS if c in df.columns]
    if cols_preview:
        print(df[cols_preview].head(3).T)
    else:
        print("No preview columns found.")

    # Add this journal's summary row to the global list
    SUMMARY_ROWS.append(summary)


def main():
    pattern = os.path.join(RAW_BASE, "*_openalex.tsv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No files found matching: {pattern}")
        return

    print(f"Found {len(files)} file(s) to process.")
    for path in files:
        process_one_file(path)

    # ---- Save global summary ----
    if SUMMARY_ROWS:
        summary_df = pd.DataFrame(SUMMARY_ROWS)
        summary_path = os.path.join(OUTPUT_DIR, "step1_summary_all_journals.tsv")
        summary_df.to_csv(summary_path, sep="\t", index=False)
        print("\n💾 Saved global Step 1 summary for all journals:")
        print(f"    {summary_path}")
    else:
        print("\n⚠️ No journals were successfully processed; no summary created.")

    print("\n✅ Step 1 diagnostic completed for all journals.")
    print(f"All outputs in:\n  {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
