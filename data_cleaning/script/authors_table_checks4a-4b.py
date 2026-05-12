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

IN_TSV = BASE_PATH / "authors_table_cleaned.tsv"
OUT_DIR = BASE_PATH / "author_checks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------
# COLUMNS
# --------------------
COL_ORCID = "ORCID"
COL_AID = "Author_ID"
NAME_CLEAN_COL = "author_name_display_clean"
NAME_RAW_COL = "author_name_display"

PREFERRED_CONTEXT_COLS = ["work_OpenAlex_ID", "source_file"]


def norm_series(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s


def write_tsv(df: pd.DataFrame, path: Path):
    df.to_csv(path, sep="\t", index=False, encoding="utf-8")


def unique_preserve_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def make_name_to_id_detail(df: pd.DataFrame, id_col: str, outfile_name: str) -> pd.DataFrame:
    """
    Row-level detail output for:
      - same cleaned name -> multiple distinct values of id_col

    Always includes BOTH ORCID and Author_ID for inspection.
    """
    context_cols = [c for c in PREFERRED_CONTEXT_COLS if c in df.columns]

    cols = [
        NAME_CLEAN_COL,
        NAME_RAW_COL,
        COL_ORCID,
        COL_AID,
        "_row_id"
    ] + context_cols

    cols = [c for c in cols if c in df.columns]
    cols = unique_preserve_order(cols)

    tmp = df.loc[:, cols].copy()

    # Need name and checked identifier
    tmp = tmp.dropna(subset=[NAME_CLEAN_COL, id_col])

    # Group stats per name
    tmp[f"name_n_unique_{id_col}"] = tmp.groupby(NAME_CLEAN_COL)[id_col].transform("nunique")
    tmp["name_total_rows"] = tmp.groupby(NAME_CLEAN_COL)[id_col].transform("size")

    # Keep only problematic names
    tmp = tmp[tmp[f"name_n_unique_{id_col}"] > 1].copy()
    if tmp.empty:
        write_tsv(tmp, OUT_DIR / outfile_name)
        return tmp

    tmp = tmp.sort_values(
        [f"name_n_unique_{id_col}", "name_total_rows", NAME_CLEAN_COL, id_col],
        ascending=[False, False, True, True]
    )

    write_tsv(tmp, OUT_DIR / outfile_name)
    return tmp


def main():
    if not IN_TSV.exists():
        raise FileNotFoundError(f"Cannot find input file: {IN_TSV}")

    df = pd.read_csv(IN_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Validate required columns
    for c in (NAME_CLEAN_COL, COL_ORCID, COL_AID):
        if c not in df.columns:
            raise KeyError(f"Missing column '{c}' in {IN_TSV.name}")

    # Light normalisation
    df[NAME_CLEAN_COL] = norm_series(df[NAME_CLEAN_COL])
    df[COL_ORCID] = norm_series(df[COL_ORCID])
    df[COL_AID] = norm_series(df[COL_AID])
    if NAME_RAW_COL in df.columns:
        df[NAME_RAW_COL] = norm_series(df[NAME_RAW_COL])

    df["_row_id"] = range(1, len(df) + 1)

    # 4a: same name -> multiple ORCID
    out4a = make_name_to_id_detail(
        df=df,
        id_col=COL_ORCID,
        outfile_name="check4a_same_clean_name_multiple_orcid.tsv"
    )

    # 4b: same name -> multiple Author_ID
    out4b = make_name_to_id_detail(
        df=df,
        id_col=COL_AID,
        outfile_name="check4b_same_clean_name_multiple_author_id.tsv"
    )

    print("\n=== Check 4 complete (name → identifiers) ===")
    print("Written: check4a_same_clean_name_multiple_orcid.tsv", f"({len(out4a):,} rows)")
    print("Written: check4b_same_clean_name_multiple_author_id.tsv", f"({len(out4b):,} rows)")


if __name__ == "__main__":
    main()