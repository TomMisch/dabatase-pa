#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_openalex_journals.py

Merges all single-journal OpenAlex TSV files into one master TSV.

Input : *_openalex.tsv files in RAW_BASE
Output: openalex_merged.tsv (same folder)

Features:
- Unions columns across journals (no column loss)
- Adds `source_file` column for traceability
- Writes UTF-8 with LF line endings
"""

import os
import glob
import csv
import pandas as pd

# --------------------------------------------------
# PATHS (UPDATED)
# --------------------------------------------------
RAW_BASE = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
OUT_PATH = os.path.join(RAW_BASE, "openalex_merged.tsv")

pattern = os.path.join(RAW_BASE, "*_openalex.tsv")
files = sorted(glob.glob(pattern))

if not files:
    raise SystemExit(f"No files found matching: {pattern}")

print(f"Found {len(files)} journal files to merge.")

dfs = []
all_cols = set()

# --------------------------------------------------
# First pass: read files and collect all column names
# --------------------------------------------------
for f in files:
    print(f"Reading: {os.path.basename(f)}")
    df = pd.read_csv(
        f,
        sep="\t",
        dtype=str,
        na_filter=False,
        engine="python"
    )
    df["source_file"] = os.path.basename(f)
    dfs.append(df)
    all_cols.update(df.columns)

all_cols = list(all_cols)

# --------------------------------------------------
# Second pass: align columns and concatenate
# --------------------------------------------------
aligned = []
for df in dfs:
    aligned.append(df.reindex(columns=all_cols, fill_value=""))

merged = pd.concat(aligned, ignore_index=True)

print(f"✅ Merged rows: {len(merged):,}")
print(f"✅ Merged columns: {len(merged.columns):,}")

# --------------------------------------------------
# Save merged file
# --------------------------------------------------
merged.to_csv(
    OUT_PATH,
    sep="\t",
    index=False,
    encoding="utf-8",
    lineterminator="\n",
    quoting=csv.QUOTE_MINIMAL,
)

print(f"💾 Saved merged file to:\n{OUT_PATH}")
