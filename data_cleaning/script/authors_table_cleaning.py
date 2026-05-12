#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import unicodedata
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

IN_TSV = BASE_PATH / "authors_table.tsv"
OUT_TSV = BASE_PATH / "authors_table_cleaned.tsv"

# --------------------
# COLUMNS
# --------------------
COL_ORCID = "ORCID"
COL_AID = "Author_ID"
NAME_COL = "author_name_display"
NAME_CLEAN_COL = "author_name_display_clean"

# Make the TSV safe to open (no row jumps)
MAKE_TSV_REVIEW_FRIENDLY = True


# --------------------
# HELPERS
# --------------------
def norm_series(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s


def fix_mojibake(s: str) -> str:
    if s is None:
        return None
    s = str(s)
    if not s.strip():
        return s.strip()

    try:
        repaired = s.encode("latin1").decode("utf-8")
        if repaired != s:
            s = repaired
    except Exception:
        pass

    try:
        repaired = s.encode("cp1252").decode("utf-8")
        if repaired != s:
            s = repaired
    except Exception:
        pass

    return s


def normalise_name(s: str) -> str:
    if s is None:
        return None

    s = fix_mojibake(s)
    s = unicodedata.normalize("NFKC", s)

    # normalise dash/hyphen variants
    s = s.replace("\u2010", "-").replace("\u2011", "-") \
         .replace("\u2012", "-").replace("\u2013", "-") \
         .replace("\u2014", "-").replace("\u2212", "-")

    # NBSP -> space
    s = s.replace("\u00A0", " ")

    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def make_review_friendly(df: pd.DataFrame) -> pd.DataFrame:
    """Replace real tabs/newlines inside cells so the TSV opens cleanly."""
    return df.replace(
        {
            "\t": " ⟂TAB⟂ ",
            "\r\n": " ⟂NL⟂ ",
            "\n": " ⟂NL⟂ ",
            "\r": " ⟂NL⟂ ",
        },
        regex=True
    )


# --------------------
# MAIN
# --------------------
def main():
    if not IN_TSV.exists():
        raise FileNotFoundError(f"Cannot find input file: {IN_TSV}")

    df = pd.read_csv(IN_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Validate required columns
    for c in (COL_ORCID, COL_AID, NAME_COL):
        if c not in df.columns:
            raise KeyError(f"Missing column '{c}' in {IN_TSV.name}. Found: {list(df.columns)}")

    # Normalise identifiers
    df[COL_ORCID] = norm_series(df[COL_ORCID])
    df[COL_AID] = norm_series(df[COL_AID])

    # Cleaned author name (keeps original too)
    df[NAME_COL] = norm_series(df[NAME_COL])
    df[NAME_CLEAN_COL] = df[NAME_COL].apply(normalise_name)

    # Optional: make TSV easy to inspect
    if MAKE_TSV_REVIEW_FRIENDLY:
        df = make_review_friendly(df)

    df.to_csv(OUT_TSV, sep="\t", index=False, encoding="utf-8")
    print("Wrote:", OUT_TSV)


if __name__ == "__main__":
    main()
