#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path

# --------------------
# CONFIG: PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

INPUT_TSV = BASE_PATH / "openalex_merged_titles_cleaned.tsv"
OUTPUT_TSV = BASE_PATH / "authors_table.tsv"

# --------------------
# CONFIG: COLUMN NAMES
# --------------------
WORK_ID_COL = "OpenAlex_ID"
AUTHORS_COL = "Authors"          # change to "Authors" if needed
SOURCE_FILE_COL = "source_file" # must exist in the input TSV


# --------------------
# HELPERS
# --------------------
def split_on_single_pipes(s: str):
    """
    Split authors on single '|' separators, but do NOT split '||' inside Institutions.
    """
    if not isinstance(s, str) or not s.strip():
        return []

    chunks = []
    buf = []
    n = len(s)

    for i, ch in enumerate(s):
        if ch == "|":
            prev_is_pipe = (i > 0 and s[i - 1] == "|")
            next_is_pipe = (i < n - 1 and s[i + 1] == "|")

            # single pipe = separator between authors
            if not prev_is_pipe and not next_is_pipe:
                chunk = "".join(buf).strip()
                if chunk:
                    chunks.append(chunk)
                buf = []
                continue

        buf.append(ch)

    last = "".join(buf).strip()
    if last:
        chunks.append(last)

    return chunks


def parse_author_block(author_block: str):
    """
    Parse one author's block:
      - Author name part is before the first ';'
      - Other fields are separated by ';'
      - Key/value are separated by ':'
    Keeps Institutions exactly as a single string (including '||' and '###').
    """
    out = {
        "author_name_full": None,         # e.g., "Jacob Torfing (Jacob Torfing)"
        "author_name_display": None,      # e.g., "Jacob Torfing"
        "author_name_raw": None,          # inside parentheses if present
        "Author_ID": None,
        "ORCID": None,
        "Position": None,
        "Countries": None,
        "Institutions": None,             # kept as-is
        "Affiliations": None,
    }

    if not isinstance(author_block, str) or not author_block.strip():
        return out

    parts = [p.strip() for p in author_block.split(";") if p.strip()]
    if not parts:
        return out

    # Name part
    name_part = parts[0]
    out["author_name_full"] = name_part

    # Extract display + raw name in parentheses, if present
    if "(" in name_part and ")" in name_part and name_part.rfind("(") < name_part.rfind(")"):
        display = name_part[: name_part.rfind("(")].strip()
        raw = name_part[name_part.rfind("(") + 1 : name_part.rfind(")")].strip()
        out["author_name_display"] = display if display else name_part.strip()
        out["author_name_raw"] = raw if raw else None
    else:
        out["author_name_display"] = name_part.strip()

    # Remaining key/value parts
    for p in parts[1:]:
        if ":" not in p:
            continue
        key, val = p.split(":", 1)
        key = key.strip()
        val = val.strip()

        k = key.lower()
        if k == "author_id":
            out["Author_ID"] = val
        elif k == "orcid":
            out["ORCID"] = val
        elif k == "position":
            out["Position"] = val
        elif k == "countries":
            out["Countries"] = val
        elif k == "institutions":
            out["Institutions"] = val
        elif k == "affiliations":
            out["Affiliations"] = val

    return out


# --------------------
# MAIN
# --------------------
def main():
    if not INPUT_TSV.exists():
        raise FileNotFoundError(f"Cannot find input file: {INPUT_TSV.resolve()}")

    df = pd.read_csv(INPUT_TSV, sep="\t", dtype=str, keep_default_na=False)

    # Validate required columns
    missing = [c for c in [WORK_ID_COL, AUTHORS_COL, SOURCE_FILE_COL] if c not in df.columns]
    if missing:
        raise KeyError(
            f"Missing column(s) {missing} in {INPUT_TSV.name}. Found columns: {list(df.columns)}"
        )

    rows = []

    for _, r in df.iterrows():
        work_id = (r.get(WORK_ID_COL) or "").strip()
        source_file = (r.get(SOURCE_FILE_COL) or "").strip()
        authors_str = r.get(AUTHORS_COL, "")

        for author_block in split_on_single_pipes(authors_str):
            parsed = parse_author_block(author_block)
            parsed["work_OpenAlex_ID"] = work_id
            parsed["source_file"] = source_file
            rows.append(parsed)

    out_df = pd.DataFrame(rows, columns=[
        "work_OpenAlex_ID",
        "source_file",
        "author_name_full",
        "author_name_display",
        "author_name_raw",
        "Author_ID",
        "ORCID",
        "Position",
        "Countries",
        "Institutions",
        "Affiliations",
    ])

    out_df.to_csv(OUTPUT_TSV, sep="\t", index=False, encoding="utf-8")
    print(f"Done. Wrote {len(out_df):,} author-rows to: {OUTPUT_TSV.resolve()}")


if __name__ == "__main__":
    main()
