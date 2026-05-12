#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

IN_TSV = BASE_PATH / "authors_table_cleaned.tsv"   # <-- NEW INPUT
OUT_DIR = BASE_PATH / "author_checks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------
# COLUMNS
# --------------------
COL_ORCID = "ORCID"
COL_AID = "Author_ID"

# Keep these in the output if present in the input
PREFERRED_CONTEXT_COLS = ["work_OpenAlex_ID", "source_file"]


def norm_series(s: pd.Series) -> pd.Series:
    """Strip strings; convert empty / None-like values to NA."""
    s = s.astype(str).str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s


def distinct_count(df: pd.DataFrame, group_col: str, value_col: str) -> pd.Series:
    """Count distinct non-null values of value_col within each group_col."""
    return (
        df.dropna(subset=[group_col, value_col])
          .groupby(group_col)[value_col]
          .nunique(dropna=True)
    )


def write_tsv(df: pd.DataFrame, path: Path):
    df.to_csv(path, sep="\t", index=False, encoding="utf-8")


def main():
    if not IN_TSV.exists():
        raise FileNotFoundError(f"Cannot find input file: {IN_TSV}")

    df = pd.read_csv(IN_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Validate required columns
    for c in (COL_ORCID, COL_AID):
        if c not in df.columns:
            raise KeyError(f"Missing column '{c}' in {IN_TSV.name}. Found: {list(df.columns)}")

    # Normalise key columns (safe even if already normalised in the cleaned table)
    df[COL_ORCID] = norm_series(df[COL_ORCID])
    df[COL_AID] = norm_series(df[COL_AID])

    # Add row id for traceability (fresh id for this file)
    df["_row_id"] = range(1, len(df) + 1)

    # Context columns that actually exist
    context_cols = [c for c in PREFERRED_CONTEXT_COLS if c in df.columns]

    # --------------------
    # CHECK 1: Same ORCID -> multiple Author_ID
    # --------------------
    c1 = distinct_count(df, COL_ORCID, COL_AID)
    bad_orcids = c1[c1 > 1].index

    check1 = df[df[COL_ORCID].isin(bad_orcids)].copy()
    sort_cols_1 = [COL_ORCID, COL_AID] + context_cols
    check1 = check1.sort_values(sort_cols_1)

    out1 = OUT_DIR / "check1_same_orcid_multiple_author_id.tsv"
    write_tsv(check1, out1)

    # --------------------
    # CHECK 2: Same Author_ID -> multiple ORCID
    # --------------------
    c2 = distinct_count(df, COL_AID, COL_ORCID)
    bad_aids = c2[c2 > 1].index

    check2 = df[df[COL_AID].isin(bad_aids)].copy()
    sort_cols_2 = [COL_AID, COL_ORCID] + context_cols
    check2 = check2.sort_values(sort_cols_2)

    out2 = OUT_DIR / "check2_same_author_id_multiple_orcid.tsv"
    write_tsv(check2, out2)

    # --------------------
    # SUMMARY
    # --------------------
    print("\n=== Checks 1 & 2 complete (on authors_table_cleaned.tsv) ===")
    print("Input:", IN_TSV)
    print("Output folder:", OUT_DIR)
    print("Written:", out1.name, f"({len(check1):,} rows)")
    print("Written:", out2.name, f"({len(check2):,} rows)")


if __name__ == "__main__":
    main()
