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

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
MAPPING_TSV = BASE_PATH / "author_id_substitutions.tsv"

# --------------------
# CONFIG
# --------------------
AUTHOR_ID_COL = "Author_ID"

OLD_COL = "OLD Author_ID"
NEW_COL = "NEW Author_ID"

# OPTIONAL: old Author_IDs to NOT replace (keep as-is), even if present in mapping file
EXCLUDE_OLD_IDS = {
    # "https://openalex.org/A0000000000",
}

# If True: error if mapping contains old_id not found in table
STRICT_UNUSED_OLD_IDS = False


def norm_cell(x):
    if x is None:
        return None
    x = str(x).strip()
    if x in ("", "nan", "None"):
        return None
    return x


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not MAPPING_TSV.exists():
        raise FileNotFoundError(f"Cannot find mapping file: {MAPPING_TSV}")

    # --------------------
    # READ AUTHORS TABLE
    # --------------------
    df = pd.read_csv(AUTHORS_TSV, sep="\t", dtype=str, keep_default_na=False)

    if AUTHOR_ID_COL not in df.columns:
        raise KeyError(f"Missing '{AUTHOR_ID_COL}' in {AUTHORS_TSV.name}")

    df[AUTHOR_ID_COL] = df[AUTHOR_ID_COL].map(norm_cell)

    # --------------------
    # READ MAPPING FILE (WITH HEADER)
    # --------------------
    map_df = pd.read_csv(MAPPING_TSV, sep="\t", dtype=str, keep_default_na=False)

    for c in (OLD_COL, NEW_COL):
        if c not in map_df.columns:
            raise KeyError(
                f"Mapping file must contain columns '{OLD_COL}' and '{NEW_COL}'. "
                f"Found: {list(map_df.columns)}"
            )

    map_df = map_df[[OLD_COL, NEW_COL]].copy()
    map_df[OLD_COL] = map_df[OLD_COL].map(norm_cell)
    map_df[NEW_COL] = map_df[NEW_COL].map(norm_cell)
    map_df = map_df.dropna(subset=[OLD_COL, NEW_COL])

    # Apply exclusions
    if EXCLUDE_OLD_IDS:
        map_df = map_df[~map_df[OLD_COL].isin(EXCLUDE_OLD_IDS)].copy()

    mapping = dict(zip(map_df[OLD_COL], map_df[NEW_COL]))

    # --------------------
    # APPLY SUBSTITUTIONS
    # --------------------
    before_ids = set(df[AUTHOR_ID_COL].dropna().unique())

    mask = df[AUTHOR_ID_COL].isin(mapping.keys())
    n_rows_changed = int(mask.sum())

    df.loc[mask, AUTHOR_ID_COL] = df.loc[mask, AUTHOR_ID_COL].map(
        lambda x: mapping.get(x, x)
    )

    unused_old_ids = sorted(set(mapping.keys()) - before_ids)

    # --------------------
    # WRITE UPDATED TABLE (OVERWRITE, NO BACKUP)
    # --------------------
    df.to_csv(
        AUTHORS_TSV,
        sep="\t",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\n"   # <-- fixed parameter name
    )

    # --------------------
    # REPORT
    # --------------------
    print("\n=== Author_ID substitution complete (NO BACKUP) ===")
    print("Updated file:", AUTHORS_TSV)
    print("Mapping file:", MAPPING_TSV)
    print("Mappings loaded (after exclusions):", len(mapping))
    print("Rows updated:", n_rows_changed)

    if unused_old_ids:
        print("\nWARNING: These OLD Author_IDs were not found in the table:")
        for x in unused_old_ids[:50]:
            print(" -", x)
        if len(unused_old_ids) > 50:
            print(f" ... and {len(unused_old_ids) - 50} more")
        if STRICT_UNUSED_OLD_IDS:
            raise ValueError("Unused OLD Author_IDs found (STRICT mode).")
    else:
        print("\nAll OLD Author_IDs were found in the table (good).")


if __name__ == "__main__":
    main()

input("Press ENTER for polishing inconsistencies of the Check 3a and 3b")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
SUBS_TSV = BASE_PATH / "check_3a3b_substitutions.tsv"

OUT_UNUSED_RULES = BASE_PATH / "author_checks" / "check3a_rules_unused.tsv"
OUT_UNUSED_RULES.parent.mkdir(parents=True, exist_ok=True)

# --------------------
# COLUMNS
# --------------------
COL_WORK = "work_OpenAlex_ID"
COL_NAME_CLEAN = "author_name_display_clean"

OLD_COL = "OLD author_name_display_clean"
NEW_COL = "NEW author_name_display_clean"


def norm_text(x):
    """Normalise text for reliable matching without changing your table logic."""
    if x is None:
        return None
    x = str(x)

    # normalise common Excel/unicode whitespace
    x = x.replace("\u00A0", " ")  # NBSP -> space

    # collapse all whitespace to single spaces, then strip
    x = re.sub(r"\s+", " ", x).strip()

    if x in ("", "nan", "None"):
        return None
    return x


def read_tsv_fallback(path: Path, preferred="utf-8", fallback="latin1") -> pd.DataFrame:
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding=preferred)
    except UnicodeDecodeError:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding=fallback)


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not SUBS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {SUBS_TSV}")

    # Authors table: keep default utf-8 read (no change to your pipeline)
    df = read_tsv_fallback(AUTHORS_TSV, preferred="utf-8", fallback="utf-8-sig")

    # Substitutions: Excel often saves non-utf8; fall back to latin1
    subs = read_tsv_fallback(SUBS_TSV, preferred="utf-8", fallback="latin1")

    # Validate columns
    for c in (COL_WORK, COL_NAME_CLEAN):
        if c not in df.columns:
            raise KeyError(f"Missing '{c}' in {AUTHORS_TSV.name}. Found: {list(df.columns)}")

    for c in (COL_WORK, OLD_COL, NEW_COL):
        if c not in subs.columns:
            raise KeyError(f"Missing '{c}' in {SUBS_TSV.name}. Found: {list(subs.columns)}")

    # Normalise matching keys (in-memory only)
    df["_work_norm"] = df[COL_WORK].map(norm_text)
    df["_name_clean_norm"] = df[COL_NAME_CLEAN].map(norm_text)

    subs["_work_norm"] = subs[COL_WORK].map(norm_text)
    subs["_old_norm"] = subs[OLD_COL].map(norm_text)
    subs["_new_norm"] = subs[NEW_COL].map(norm_text)

    subs = subs.dropna(subset=["_work_norm", "_old_norm", "_new_norm"])

    # Apply substitutions
    n_changes = 0
    unused_rows = []

    for _, r in subs.iterrows():
        mask = (df["_work_norm"] == r["_work_norm"]) & (df["_name_clean_norm"] == r["_old_norm"])
        count = int(mask.sum())
        if count > 0:
            # write back NEW value into the real column (keep your structure unchanged)
            df.loc[mask, COL_NAME_CLEAN] = r[NEW_COL]
            n_changes += count
        else:
            unused_rows.append({
                COL_WORK: r[COL_WORK],
                OLD_COL: r[OLD_COL],
                NEW_COL: r[NEW_COL],
                "note": "No exact match found after whitespace/NBSP normalisation"
            })

    # Drop helper columns
    df = df.drop(columns=["_work_norm", "_name_clean_norm"], errors="ignore")

    # Overwrite authors table (no structural/logic changes)
    df.to_csv(AUTHORS_TSV, sep="\t", index=False, encoding="utf-8", lineterminator="\n")

    # Write unused rules for debugging (optional but helpful)
    pd.DataFrame(unused_rows).to_csv(OUT_UNUSED_RULES, sep="\t", index=False, encoding="utf-8")

    print("\n=== Check 3a polishing applied ===")
    print("Updated:", AUTHORS_TSV)
    print("Total rows updated:", n_changes)
    print("Unused substitution rules:", len(unused_rows))
    print("Unused rules file:", OUT_UNUSED_RULES)


if __name__ == "__main__":
    main()

input("Press ENTER for polishing inconsistencies of the Check 4a")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
CHECK4A_TSV = BASE_PATH / "check_4a.tsv"

# --------------------
# COLUMNS
# --------------------
COL_NAME = "author_name_display_clean"
COL_ORCID = "ORCID"

OLD_ORCID_COL = "old_ORCID_ID"
NEW_ORCID_COL = "new_ORCID_ID"


def norm_text(x):
    if x is None:
        return None
    x = str(x).replace("\u00A0", " ")
    x = re.sub(r"\s+", " ", x).strip()
    if x in ("", "nan", "None"):
        return None
    return x


def norm_orcid_for_matching(x):
    """Used only for matching, not for writing."""
    if x is None:
        return None
    x = str(x).replace("\u00A0", " ").strip()
    if x in ("", "nan", "None"):
        return None
    x = re.sub(r"^https?://orcid\.org/", "", x, flags=re.I)
    return x.upper()


def read_tsv(path):
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="latin1")


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not CHECK4A_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {CHECK4A_TSV}")

    df = read_tsv(AUTHORS_TSV)
    corr = read_tsv(CHECK4A_TSV)

    # remove hidden spaces in headers
    df.columns = df.columns.str.strip()
    corr.columns = corr.columns.str.strip()

    # check columns
    for c in (COL_NAME, COL_ORCID):
        if c not in df.columns:
            raise KeyError(f"Missing '{c}' in {AUTHORS_TSV.name}")

    for c in (COL_NAME, OLD_ORCID_COL, NEW_ORCID_COL):
        if c not in corr.columns:
            raise KeyError(f"Missing '{c}' in {CHECK4A_TSV.name}")

    # helper columns for matching
    df["_name_norm"] = df[COL_NAME].map(norm_text)
    df["_orcid_norm"] = df[COL_ORCID].map(norm_orcid_for_matching)

    corr["_name_norm"] = corr[COL_NAME].map(norm_text)
    corr["_old_orcid_norm"] = corr[OLD_ORCID_COL].map(norm_orcid_for_matching)

    rows_updated = 0

    for _, r in corr.iterrows():
        name_norm = r["_name_norm"]
        old_orcid_norm = r["_old_orcid_norm"]
        new_orcid_to_write = str(r[NEW_ORCID_COL]).strip()

        if name_norm is None or old_orcid_norm is None:
            continue

        mask = (
            (df["_name_norm"] == name_norm) &
            (df["_orcid_norm"] == old_orcid_norm)
        )

        count = int(mask.sum())

        if count > 0:
            df.loc[mask, COL_ORCID] = new_orcid_to_write
            df.loc[mask, "_orcid_norm"] = norm_orcid_for_matching(new_orcid_to_write)
            rows_updated += count

    # remove helper columns
    df = df.drop(columns=["_name_norm", "_orcid_norm"], errors="ignore")

    # overwrite original file
    df.to_csv(
        AUTHORS_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n"
    )

    print("Check 4a completed.")
    print("Updated file:", AUTHORS_TSV)
    print("Rows updated:", rows_updated)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
CHECK4A_REST_TSV = BASE_PATH / "check_4a_rest.tsv"

# --------------------
# COLUMNS
# --------------------
COL_NAME = "author_name_display_clean"
COL_ORCID = "ORCID"


def norm_text(x):
    if x is None:
        return None
    x = str(x).replace("\u00A0", " ")
    x = re.sub(r"\s+", " ", x).strip()
    if x in ("", "nan", "None"):
        return None
    return x


def read_tsv(path):
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="latin1")


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not CHECK4A_REST_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {CHECK4A_REST_TSV}")

    df = read_tsv(AUTHORS_TSV)
    rest = read_tsv(CHECK4A_REST_TSV)

    # Remove hidden spaces from headers
    df.columns = df.columns.str.strip()
    rest.columns = rest.columns.str.strip()

    # Check columns
    for c in (COL_NAME, COL_ORCID):
        if c not in df.columns:
            raise KeyError(f"Missing '{c}' in {AUTHORS_TSV.name}")

    if COL_NAME not in rest.columns:
        raise KeyError(f"Missing '{COL_NAME}' in {CHECK4A_REST_TSV.name}")

    # Normalise names for matching
    df["_name_norm"] = df[COL_NAME].map(norm_text)
    rest["_name_norm"] = rest[COL_NAME].map(norm_text)

    # Keep only valid names
    names_to_clear = set(rest["_name_norm"].dropna())

    # Find matching rows
    mask = df["_name_norm"].isin(names_to_clear)
    rows_updated = int(mask.sum())

    # Delete ORCID
    df.loc[mask, COL_ORCID] = ""

    # Remove helper column
    df = df.drop(columns=["_name_norm"], errors="ignore")

    # Overwrite original file
    df.to_csv(
        AUTHORS_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n"
    )

    print("Check 4a rest completed.")
    print("Updated file:", AUTHORS_TSV)
    print("Rows with ORCID deleted:", rows_updated)


if __name__ == "__main__":
    main()

input("Press ENTER for polishing inconsistencies of the Check 4b")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
CHECK4B_TSV = BASE_PATH / "check_4b.tsv"

# --------------------
# COLUMNS
# --------------------
COL_NAME = "author_name_display_clean"
COL_AUTHOR_ID = "Author_ID"

OLD_ID_COL = "old_Author_ID"
NEW_ID_COL = "new_Author_ID"


def norm_text(x):
    if x is None:
        return None
    x = str(x).replace("\u00A0", " ")
    x = re.sub(r"\s+", " ", x).strip()
    if x in ("", "nan", "None"):
        return None
    return x


def read_tsv(path):
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="latin1")


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not CHECK4B_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {CHECK4B_TSV}")

    df = read_tsv(AUTHORS_TSV)
    corr = read_tsv(CHECK4B_TSV)

    # Remove hidden spaces from headers
    df.columns = df.columns.str.strip()
    corr.columns = corr.columns.str.strip()

    # Check columns
    for c in (COL_NAME, COL_AUTHOR_ID):
        if c not in df.columns:
            raise KeyError(f"Missing '{c}' in {AUTHORS_TSV.name}")

    for c in (COL_NAME, OLD_ID_COL, NEW_ID_COL):
        if c not in corr.columns:
            raise KeyError(f"Missing '{c}' in {CHECK4B_TSV.name}")

    # Helper columns for matching
    df["_name_norm"] = df[COL_NAME].map(norm_text)
    df["_author_id_norm"] = df[COL_AUTHOR_ID].map(norm_text)

    corr["_name_norm"] = corr[COL_NAME].map(norm_text)
    corr["_old_id_norm"] = corr[OLD_ID_COL].map(norm_text)

    rows_updated = 0

    for _, r in corr.iterrows():
        name_norm = r["_name_norm"]
        old_id_norm = r["_old_id_norm"]
        new_id_to_write = str(r[NEW_ID_COL]).strip()

        if name_norm is None or old_id_norm is None:
            continue

        mask = (
            (df["_name_norm"] == name_norm) &
            (df["_author_id_norm"] == old_id_norm)
        )

        count = int(mask.sum())

        if count > 0:
            df.loc[mask, COL_AUTHOR_ID] = new_id_to_write
            df.loc[mask, "_author_id_norm"] = norm_text(new_id_to_write)
            rows_updated += count

    # Remove helper columns
    df = df.drop(columns=["_name_norm", "_author_id_norm"], errors="ignore")

    # Overwrite original file
    df.to_csv(
        AUTHORS_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n"
    )

    print("Check 4b completed.")
    print("Updated file:", AUTHORS_TSV)
    print("Rows updated:", rows_updated)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

# --------------------
# PATHS
# --------------------
BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

AUTHORS_TSV = BASE_PATH / "authors_table_cleaned.tsv"
CHECK4B_REST_TSV = BASE_PATH / "check_4b_rest.tsv"

# --------------------
# COLUMNS
# --------------------
COL_NAME = "author_name_display_clean"
COL_AUTHOR_ID = "Author_ID"


def norm_text(x):
    if x is None:
        return None
    x = str(x).replace("\u00A0", " ")
    x = re.sub(r"\s+", " ", x).strip()
    if x in ("", "nan", "None"):
        return None
    return x


def read_tsv(path):
    try:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, encoding="latin1")


def main():
    if not AUTHORS_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {AUTHORS_TSV}")
    if not CHECK4B_REST_TSV.exists():
        raise FileNotFoundError(f"Cannot find: {CHECK4B_REST_TSV}")

    df = read_tsv(AUTHORS_TSV)
    rest = read_tsv(CHECK4B_REST_TSV)

    # Remove hidden spaces from headers
    df.columns = df.columns.str.strip()
    rest.columns = rest.columns.str.strip()

    # Check columns
    for c in (COL_NAME, COL_AUTHOR_ID):
        if c not in df.columns:
            raise KeyError(f"Missing '{c}' in {AUTHORS_TSV.name}")

    if COL_NAME not in rest.columns:
        raise KeyError(f"Missing '{COL_NAME}' in {CHECK4B_REST_TSV.name}")

    # Normalise names for matching
    df["_name_norm"] = df[COL_NAME].map(norm_text)
    rest["_name_norm"] = rest[COL_NAME].map(norm_text)

    names_to_clear = set(rest["_name_norm"].dropna())

    # Find matching rows
    mask = df["_name_norm"].isin(names_to_clear)
    rows_updated = int(mask.sum())

    # Delete Author_ID
    df.loc[mask, COL_AUTHOR_ID] = ""

    # Remove helper column
    df = df.drop(columns=["_name_norm"], errors="ignore")

    # Overwrite original file
    df.to_csv(
        AUTHORS_TSV,
        sep="\t",
        index=False,
        encoding="utf-8",
        lineterminator="\n"
    )

    print("Check 4b rest completed.")
    print("Updated file:", AUTHORS_TSV)
    print("Rows with Author_ID deleted:", rows_updated)


if __name__ == "__main__":
    main()