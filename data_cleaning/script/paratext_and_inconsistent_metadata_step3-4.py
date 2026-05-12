#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import pandas as pd

# ---------------------------
# SET YOUR PATHS
# ---------------------------
MERGED_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged.tsv"

# Your .md file containing OpenAlex IDs (one per line or embedded in text)
IDS_MD = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\data_cleaning_recording_note.md"

# Output files (safe: we don't overwrite the merged file)
OUT_FILTERED_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_filtered.tsv"
OUT_REMOVED_TSV  = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_removed_rows.tsv"

COL_ID = "OpenAlex_ID"

# ---------------------------
# Helpers
# ---------------------------
OPENALEX_ID_RE = re.compile(r"https?://openalex\.org/W\d+", flags=re.IGNORECASE)

def read_ids_from_md(md_path: str) -> set[str]:
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    ids = set(m.group(0) for m in OPENALEX_ID_RE.finditer(text))
    # normalise scheme/case a bit (OpenAlex IDs are case-insensitive in practice, but keep consistent)
    ids = set(i.replace("http://", "https://").strip() for i in ids)
    return ids

def normalise_id(x: str) -> str:
    if not isinstance(x, str):
        return ""
    s = x.strip()
    s = s.replace("http://", "https://")
    return s

# ---------------------------
# Main
# ---------------------------
def main():
    if not os.path.exists(MERGED_TSV):
        raise SystemExit(f"Merged TSV not found:\n{MERGED_TSV}")
    if not os.path.exists(IDS_MD):
        raise SystemExit(f"MD file not found:\n{IDS_MD}")

    ids_to_remove = read_ids_from_md(IDS_MD)
    print(f"IDs loaded from MD: {len(ids_to_remove):,}")

    if len(ids_to_remove) == 0:
        raise SystemExit("No OpenAlex IDs were found in the .md file (pattern https://openalex.org/W##########).")

    print(f"Reading merged TSV:\n{MERGED_TSV}")
    df = pd.read_csv(MERGED_TSV, sep="\t", dtype=str, na_filter=False, engine="python")

    if COL_ID not in df.columns:
        raise SystemExit(f"Column '{COL_ID}' not found in merged TSV.")

    # normalise ID column before matching
    df[COL_ID] = df[COL_ID].apply(normalise_id)

    mask_remove = df[COL_ID].isin(ids_to_remove)

    n_total = len(df)
    n_remove = int(mask_remove.sum())
    n_keep = n_total - n_remove

    print(f"Total rows:   {n_total:,}")
    print(f"To remove:    {n_remove:,}")
    print(f"To keep:      {n_keep:,}")

    removed = df[mask_remove].copy()
    kept = df[~mask_remove].copy()

    # Save outputs
    kept.to_csv(
        OUT_FILTERED_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    removed.to_csv(
        OUT_REMOVED_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )

    print("\n✅ Done.")
    print(f"Filtered merged file saved to:\n{OUT_FILTERED_TSV}")
    print(f"Removed rows saved to:\n{OUT_REMOVED_TSV}")

if __name__ == "__main__":
    main()


input("Press ENTER to continue to Block 1...")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####### SCRIPT BLOCK TO FIND ANY OTHER PIECE OF LITERATURE WITHIN THE MERGED DATASET ##########


import os
import re
import csv
import pandas as pd

# --------------------
# SET YOUR PATHS
# --------------------
INPUT_TSV  = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_filtered.tsv"
OUTPUT_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\step_1\titles_flagged_by_keywords.tsv"

# --------------------
# KEYWORDS (your list)
# --------------------
EXACT_WORDS = [
    "book",
    "digest",
    "editorial",
    "editor",
    "note",
    "foreword",
    "afterword",
    "erratum",
    "errata",
    "corrigendum",
    "retraction",
    "addendum",
    "editors",
    "special issue",
    "announcement",
    "preface",
    "table of contents",
]

# Prefix patterns (your * wildcards)
PREFIXES = [
    "congratulation",  # matches congratulation, congratulations, congratulatory, etc.
    "commentar",       # matches commentary, commentaries, etc.
]

# Currency symbols to detect in title
CURRENCY_SYMBOLS = ["€", "$", "£"]

# Exact tokens required, including dot
EXACT_TOKENS_WITH_DOT = ["p.", "pp."]

# --------------------
# Build regex
# --------------------
# Word-boundary exact words (case-insensitive)
exact_words_re = r"\b(" + "|".join(map(re.escape, EXACT_WORDS)) + r")\b"

# Word-boundary prefix match: e.g., commentar + letters
prefix_re = r"\b(" + "|".join(map(re.escape, PREFIXES)) + r")[a-z]*\b"

# Currency: any occurrence of €, $, £
currency_re = "(" + "|".join(map(re.escape, CURRENCY_SYMBOLS)) + ")"

# Exact p. / pp. tokens (must include dot) with word boundaries around p/pp
p_tokens_re = r"\b(p\.|pp\.)\b"

# Combine into one compiled regex for quick "does it match?"
COMBINED = re.compile(
    "|".join([exact_words_re, prefix_re, currency_re, p_tokens_re]),
    flags=re.IGNORECASE
)

# Separate compiled patterns so we can report *which* terms were found
PATTERNS = [
    ("keyword", re.compile(exact_words_re, flags=re.IGNORECASE)),
    ("keyword_prefix", re.compile(prefix_re, flags=re.IGNORECASE)),
    ("currency", re.compile(currency_re)),
    ("page_token", re.compile(p_tokens_re, flags=re.IGNORECASE)),
]

def extract_matches(title: str) -> str:
    """Return a semicolon-separated list of matched items found in the title."""
    if not isinstance(title, str):
        return ""

    t = title.strip()
    if not t:
        return ""

    # ✅ SPECIAL RULE: title is exactly "introduction"
    if t.lower() == "introduction":
        return "introduction_only"

    found = set()

    # Quick pre-check
    if not COMBINED.search(t):
        return ""

    for label, pat in PATTERNS:
        for m in pat.finditer(t):
            val = m.group(0)
            # Normalise reporting:
            # - keywords as lowercase
            # - currencies as-is
            if label in ("keyword", "keyword_prefix", "page_token"):
                found.add(val.lower())
            else:
                found.add(val)

    return "; ".join(sorted(found))

def main():
    if not os.path.exists(INPUT_TSV):
        raise SystemExit(f"Input TSV not found:\n{INPUT_TSV}")

    os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)

    print(f"Reading: {INPUT_TSV}")
    df = pd.read_csv(INPUT_TSV, sep="\t", dtype=str, na_filter=False, engine="python")

    if "Title" not in df.columns:
        raise SystemExit("Column 'Title' not found in input file.")

    print(f"Rows loaded: {len(df):,}")

    df["__matched__"] = df["Title"].apply(extract_matches)
    flagged = df[df["__matched__"] != ""]

    print(f"Flagged rows: {len(flagged):,}")

    flagged.to_csv(
        OUTPUT_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )

    print(f"Saved flagged records to:\n{OUTPUT_TSV}")

if __name__ == "__main__":
    main()

input("Press ENTER to continue to Intermediate step 2...")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import pandas as pd

# --------------------------------------------------
# PATHS
# --------------------------------------------------
MERGED_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_filtered.tsv"

FLAGGED_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\step_1\titles_flagged_by_keywords.tsv"

OUT_CLEAN_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_titles_cleaned.tsv"

COL_ID = "OpenAlex_ID"

# --------------------------------------------------
# MANUAL WHITELIST (IDs you do NOT want to delete)
# --------------------------------------------------
KEEP_OPENALEX_IDS = {
  "https://openalex.org/W2047648862","https://openalex.org/W2097653146","https://openalex.org/W2043362155","https://openalex.org/W2063373610","https://openalex.org/W1548433737","https://openalex.org/W2107485800","https://openalex.org/W2040937697","https://openalex.org/W1983233679","https://openalex.org/W1967412428","https://openalex.org/W4206601893","https://openalex.org/W1993650909","https://openalex.org/W2014667281","https://openalex.org/W2166991210","https://openalex.org/W2124140621","https://openalex.org/W2888832443","https://openalex.org/W2506765362","https://openalex.org/W21119460282","https://openalex.org/W2063518261","https://openalex.org/W1994854113","https://openalex.org/W2168261758","https://openalex.org/W2292293894","https://openalex.org/W2047648862","https://openalex.org/W2810970046"  
}

def normalise_id(x: str) -> str:
    if not isinstance(x, str):
        return ""
    s = x.strip()
    return s.replace("http://", "https://")

def main():
    for path in [MERGED_TSV, FLAGGED_TSV]:
        if not os.path.exists(path):
            raise SystemExit(f"File not found:\n{path}")

    print("Reading merged file…")
    merged = pd.read_csv(
        MERGED_TSV,
        sep="\t",
        dtype=str,
        na_filter=False,
        engine="python"
    )

    print("Reading flagged titles file…")
    flagged = pd.read_csv(
        FLAGGED_TSV,
        sep="\t",
        dtype=str,
        na_filter=False,
        engine="python"
    )

    if COL_ID not in merged.columns:
        raise SystemExit(f"Column '{COL_ID}' not found in merged file.")
    if COL_ID not in flagged.columns:
        raise SystemExit(f"Column '{COL_ID}' not found in flagged file.")

    # Normalise OpenAlex_IDs
    merged[COL_ID] = merged[COL_ID].apply(normalise_id)
    flagged[COL_ID] = flagged[COL_ID].apply(normalise_id)

    keep_ids = {normalise_id(i) for i in KEEP_OPENALEX_IDS}
    flagged_ids = set(flagged[COL_ID]) - {""}

    print(f"Flagged OpenAlex_IDs: {len(flagged_ids):,}")
    print(f"Whitelisted OpenAlex_IDs: {len(keep_ids):,}")

    ids_to_remove = flagged_ids - keep_ids
    print(f"OpenAlex_IDs to remove: {len(ids_to_remove):,}")

    cleaned = merged[~merged[COL_ID].isin(ids_to_remove)].copy()

    print(f"Rows before: {len(merged):,}")
    print(f"Rows after:  {len(cleaned):,}")

    cleaned.to_csv(
        OUT_CLEAN_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )

    print("\n✅ Done.")
    print(f"Cleaned merged file saved to:\n{OUT_CLEAN_TSV}")

if __name__ == "__main__":
    main()


input("Press ENTER to continue to Block 2...")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import pandas as pd

# --------------------
# SET PATHS
# --------------------
INPUT_TSV  = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_titles_cleaned.tsv"
OUTPUT_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\step_1\inconsistent_data.tsv"

YEAR_MIN = 1980
YEAR_MAX = 2024
DOI_PREFIX = "https://doi.org/"

def is_blank(x) -> bool:
    return (not isinstance(x, str)) or (x.strip() == "")

def parse_year_4digits(x: str):
    """Return int year if x is exactly a 4-digit year; else None."""
    if is_blank(x):
        return None
    s = str(x).strip()
    if re.fullmatch(r"\d{4}", s):
        return int(s)
    return None

def is_true_string(x: str) -> bool:
    """Treat TRUE/True/true as True (also accepts 1/yes)."""
    if is_blank(x):
        return False
    s = str(x).strip().lower()
    return s in {"true", "1", "yes"}

def build_issue(row: pd.Series) -> str:
    issues = []

    # 1) Is_Paratext == TRUE
    if "Is_Paratext" in row.index and is_true_string(row["Is_Paratext"]):
        issues.append("Is_Paratext=TRUE")

    # 2) Year outside 1980–2024 (or invalid format)
    if "Year" in row.index:
        raw_year = row["Year"]
        y = parse_year_4digits(raw_year)
        if y is None:
            # Only flag invalid format if Year is non-empty
            if not is_blank(raw_year):
                issues.append("Year invalid (not 4 digits)")
        else:
            if not (YEAR_MIN <= y <= YEAR_MAX):
                issues.append(f"Year out of range ({YEAR_MIN}-{YEAR_MAX})")

    # 3) Abstract empty
    if "Abstract" in row.index and is_blank(row["Abstract"]):
        issues.append("Abstract missing")

    # 4) DOI does not start with https://doi.org/ (missing DOI is OK)
    if "DOI" in row.index:
        doi = row["DOI"]
        if not is_blank(doi):
            if not str(doi).strip().startswith(DOI_PREFIX):
                issues.append(f"DOI not starting with {DOI_PREFIX}")

    return "; ".join(issues)

def main():
    if not os.path.exists(INPUT_TSV):
        raise SystemExit(f"Input file not found:\n{INPUT_TSV}")

    os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)

    print(f"Reading: {INPUT_TSV}")
    df = pd.read_csv(INPUT_TSV, sep="\t", dtype=str, na_filter=False, engine="python")
    print(f"Loaded rows: {len(df):,} | cols: {len(df.columns):,}")

    # Create issue column
    df["__issue__"] = df.apply(build_issue, axis=1)

    # Keep only rows with any issues
    flagged = df[df["__issue__"] != ""].copy()

    print(f"Flagged rows (inconsistent): {len(flagged):,}")

    flagged.to_csv(
        OUTPUT_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )

    print(f"Saved to:\n{OUTPUT_TSV}")

if __name__ == "__main__":
    main()

input("Press ENTER to continue to Block 3...")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import pandas as pd

# --------------------------------------------------
# PATHS
# --------------------------------------------------
INPUT_TSV = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data\openalex_merged_titles_cleaned.tsv"

OUTPUT_DUPES = r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_cleaning\files\step_1\duplicates_openalex_merged_titles_cleaned.tsv"

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
COL_DOI = "DOI"
COL_ID = "OpenAlex_ID"
COL_TITLE = "Title"
COL_YEAR = "Year"

# "range of + or - Year" → interpreted as ±1 year window by default.
YEAR_TOLERANCE = 1  # change to 0 for same-year only, 2 for ±2 years, etc.

def is_blank(x) -> bool:
    return (not isinstance(x, str)) or (x.strip() == "")

def parse_year(x):
    """Return int year if exactly 4 digits, else None."""
    if is_blank(x):
        return None
    s = str(x).strip()
    return int(s) if re.fullmatch(r"\d{4}", s) else None

def find_exact_duplicates(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Return rows that are exact duplicates on col (non-empty only), annotated."""
    if col not in df.columns:
        raise SystemExit(f"Required column missing: {col}")

    s = df[col].fillna("").map(lambda v: v.strip())
    non_empty = s != ""
    dup_mask = s.duplicated(keep=False) & non_empty

    out = df[dup_mask].copy()
    if out.empty:
        return out

    out["__match_rule__"] = f"duplicate_{col}"
    out["__group_key__"] = s[dup_mask].values
    out["__group_size__"] = out.groupby("__group_key__")["__group_key__"].transform("size")
    return out

def find_title_year_window_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return rows where Title is identical and there exists at least one other row
    with the same Title and Year within ± YEAR_TOLERANCE.
    Non-empty Title and valid 4-digit Year only.
    """
    for c in [COL_TITLE, COL_YEAR]:
        if c not in df.columns:
            raise SystemExit(f"Required column missing: {c}")

    work = df.copy()
    work["__year_int__"] = work[COL_YEAR].apply(parse_year)

    # only consider rows with non-empty title and valid year
    mask = ~work[COL_TITLE].map(is_blank) & work["__year_int__"].notna()
    work = work[mask].copy()
    if work.empty:
        return pd.DataFrame()

    # group by Title and find rows that have another year within tolerance
    flagged_idx = set()

    for title, grp in work.groupby(COL_TITLE, sort=False):
        if len(grp) < 2:
            continue
        years = grp["__year_int__"].tolist()
        idxs = grp.index.tolist()

        # check if any pair is within tolerance
        # if yes, flag all rows that participate in at least one such pair
        for i in range(len(years)):
            for j in range(i + 1, len(years)):
                if abs(years[i] - years[j]) <= YEAR_TOLERANCE:
                    flagged_idx.add(idxs[i])
                    flagged_idx.add(idxs[j])

    out = df.loc[list(flagged_idx)].copy() if flagged_idx else pd.DataFrame()
    if out.empty:
        return out

    # annotate group key as Title
    out["__match_rule__"] = f"duplicate_Title_within_±{YEAR_TOLERANCE}_Year"
    out["__group_key__"] = out[COL_TITLE]
    out["__group_size__"] = out.groupby("__group_key__")["__group_key__"].transform("size")
    return out

def merge_reasons(parts):
    """Combine multiple duplicate outputs, collapsing repeated rows and merging reasons."""
    if not parts:
        return pd.DataFrame()

    # Add a stable row id to merge reasons even if the same row appears under multiple rules
    combined = pd.concat([p for p in parts if p is not None and not p.empty], ignore_index=False)
    if combined.empty:
        return combined

    # Use index from original DF as row identifier
    combined["__row_index__"] = combined.index

    # Aggregate match rules per row
    # For __group_key__/__group_size__ we keep the first; match_rule becomes semicolon list
    agg = (
        combined.groupby("__row_index__", sort=False)
        .agg({
            "__match_rule__": lambda s: "; ".join(sorted(set(map(str, s)))),
            "__group_key__": "first",
            "__group_size__": "first",
        })
        .reset_index()
    )

    # Rebuild final rows using the first occurrence of each row
    base = combined.drop_duplicates(subset="__row_index__").copy()
    base = base.drop(columns=["__match_rule__", "__group_key__", "__group_size__"], errors="ignore")
    out = base.merge(agg, on="__row_index__", how="left")

    # Put diagnostics first
    diag = ["__match_rule__", "__group_key__", "__group_size__", "__row_index__"]
    cols = diag + [c for c in out.columns if c not in diag]
    return out[cols]

def main():
    if not os.path.exists(INPUT_TSV):
        raise SystemExit(f"Input TSV not found:\n{INPUT_TSV}")

    os.makedirs(os.path.dirname(OUTPUT_DUPES), exist_ok=True)

    print(f"Reading: {INPUT_TSV}")
    df = pd.read_csv(INPUT_TSV, sep="\t", dtype=str, na_filter=False, engine="python")
    print(f"Rows loaded: {len(df):,} | Columns: {len(df.columns):,}")

    # 1) Duplicate DOI
    dup_doi = find_exact_duplicates(df, COL_DOI)
    print(f"Duplicate DOI rows: {len(dup_doi):,}")

    # 2) Duplicate OpenAlex_ID
    dup_id = find_exact_duplicates(df, COL_ID)
    print(f"Duplicate OpenAlex_ID rows: {len(dup_id):,}")

    # 3) Same Title with Year within ± tolerance
    dup_title_year = find_title_year_window_duplicates(df)
    print(f"Title duplicates within ±{YEAR_TOLERANCE} year(s): {len(dup_title_year):,}")

    # Combine (same row may appear in multiple checks)
    out = merge_reasons([dup_doi, dup_id, dup_title_year])

    if out.empty:
        print("✅ No duplicates found under the specified rules.")
        # still write an empty file with headers so the pipeline is reproducible
        empty = df.head(0).copy()
        empty.insert(0, "__match_rule__", "")
        empty.insert(1, "__group_key__", "")
        empty.insert(2, "__group_size__", "")
        empty.insert(3, "__row_index__", "")
        empty.to_csv(OUTPUT_DUPES, sep="\t", index=False, encoding="utf-8", lineterminator="\n")
        print(f"Saved empty duplicates file with headers:\n{OUTPUT_DUPES}")
        return

    out.to_csv(
        OUTPUT_DUPES,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )

    print(f"\n💾 Saved duplicates to:\n{OUTPUT_DUPES}")
    print(f"Total rows exported: {len(out):,}")

if __name__ == "__main__":
    main()

input("Press ENTER to continue to Intermediate step 3...")
