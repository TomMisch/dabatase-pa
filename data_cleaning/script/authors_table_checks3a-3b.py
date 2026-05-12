#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

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

# In the cleaned table these should already exist:
NAME_COL = "author_name_display"
NAME_CLEAN_COL = "author_name_display_clean"

# Keep these if present
PREFERRED_CONTEXT_COLS = ["work_OpenAlex_ID", "source_file"]


# --------------------
# HELPERS
# --------------------
def norm_series(s: pd.Series) -> pd.Series:
    """Strip strings; convert empty / None-like to NA."""
    s = s.astype(str).str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s


def similarity_pct(a: str, b: str) -> float:
    """Similarity percentage (0-100) between two strings."""
    if not a or not b:
        return 0.0
    return round(100 * SequenceMatcher(None, a, b).ratio(), 2)


def write_tsv(df: pd.DataFrame, path: Path):
    df.to_csv(path, sep="\t", index=False, encoding="utf-8")


def unique_preserve_order(items):
    """Deduplicate a list while preserving order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def make_row_level_detail(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Row-level detail output:
    - flags groups where author_name_display_clean has >1 distinct value
    - assigns canonical_clean_name (most frequent cleaned name in group)
    - computes similarity_to_canonical_pct per row
    - adds group-level counts per row
    """
    context_cols = [c for c in PREFERRED_CONTEXT_COLS if c in df.columns]

    # Build column list safely (no duplicates)
    cols = [group_col, NAME_COL, NAME_CLEAN_COL, COL_ORCID, COL_AID] + context_cols + ["_row_id"]
    cols = [c for c in cols if c in df.columns]
    cols = unique_preserve_order(cols)

    tmp = df.loc[:, cols].copy()

    # Drop missing group or missing cleaned name
    tmp = tmp.dropna(subset=[group_col, NAME_CLEAN_COL])

    # Group-level stats (repeated per row)
    tmp["group_n_unique_names_clean"] = tmp.groupby(group_col)[NAME_CLEAN_COL].transform("nunique")
    tmp["group_total_rows"] = tmp.groupby(group_col)[NAME_CLEAN_COL].transform("size")

    # Keep only problematic groups (>1 unique cleaned name)
    tmp = tmp[tmp["group_n_unique_names_clean"] > 1].copy()
    if tmp.empty:
        return tmp

    # Canonical cleaned name = most frequent cleaned name in group
    freq = (
        tmp.groupby([group_col, NAME_CLEAN_COL], dropna=True)
           .size()
           .reset_index(name="clean_name_count")
    )

    canon = (
        freq.sort_values([group_col, "clean_name_count"], ascending=[True, False])
            .groupby(group_col, as_index=False)
            .head(1)
            [[group_col, NAME_CLEAN_COL]]
            .rename(columns={NAME_CLEAN_COL: "canonical_clean_name"})
    )

    tmp = tmp.merge(canon, on=group_col, how="left")

    # Similarity per row (cleaned vs canonical)
    tmp["similarity_to_canonical_pct"] = tmp.apply(
        lambda r: similarity_pct(r[NAME_CLEAN_COL], r["canonical_clean_name"]), axis=1
    )

    # Sort for review
    tmp = tmp.sort_values(
        [group_col, "similarity_to_canonical_pct", NAME_CLEAN_COL, NAME_COL],
        ascending=[True, True, True, True]
    )

    return tmp


# --------------------
# MAIN
# --------------------
def main():
    if not IN_TSV.exists():
        raise FileNotFoundError(f"Cannot find input file: {IN_TSV}")

    df = pd.read_csv(IN_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Validate required columns
    for c in (COL_ORCID, COL_AID, NAME_COL, NAME_CLEAN_COL):
        if c not in df.columns:
            raise KeyError(f"Missing column '{c}' in {IN_TSV.name}. Found: {list(df.columns)}")

    # Normalise IDs and names (safe even if already normalised)
    df[COL_ORCID] = norm_series(df[COL_ORCID])
    df[COL_AID] = norm_series(df[COL_AID])
    df[NAME_COL] = norm_series(df[NAME_COL])
    df[NAME_CLEAN_COL] = norm_series(df[NAME_CLEAN_COL])

    # Fresh row id for traceability (for this file)
    df["_row_id"] = range(1, len(df) + 1)

    # --------------------
    # CHECK 3a: Same ORCID -> multiple cleaned display names
    # --------------------
    detail_3a = make_row_level_detail(df, group_col=COL_ORCID)
    out_3a = OUT_DIR / "check3a_orcid_name_display_detail.tsv"
    write_tsv(detail_3a, out_3a)

    # --------------------
    # CHECK 3b: Same Author_ID -> multiple cleaned display names
    # --------------------
    detail_3b = make_row_level_detail(df, group_col=COL_AID)
    out_3b = OUT_DIR / "check3b_author_id_name_display_detail.tsv"
    write_tsv(detail_3b, out_3b)

    print("\n=== Checks 3a & 3b complete (on authors_table_cleaned.tsv) ===")
    print("Input:", IN_TSV)
    print("Output folder:", OUT_DIR)
    print("Written:", out_3a.name, f"({len(detail_3a):,} rows)")
    print("Written:", out_3b.name, f"({len(detail_3b):,} rows)")


if __name__ == "__main__":
    main()
