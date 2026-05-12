from pathlib import Path
import pandas as pd

# ------------------------------------------------------------
# Base path
# ------------------------------------------------------------

BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

# ------------------------------------------------------------
# Input and output files
# ------------------------------------------------------------

input_file = BASE_PATH / "authors_table_cleaned_with_publication_ID.tsv"

output_file = BASE_PATH / "authors_table_cleaned_with_publication_ID_and_author_ID.tsv"
mapping_file = BASE_PATH / "author_ID_mapping.tsv"
unmatched_file = BASE_PATH / "authors_without_internal_author_ID.tsv"

# ------------------------------------------------------------
# Read authors table
# ------------------------------------------------------------

authors = pd.read_csv(input_file, sep="\t", dtype=str)

# Clean column names, especially accidental trailing spaces
authors.columns = authors.columns.str.strip()

# ------------------------------------------------------------
# Check required columns
# ------------------------------------------------------------

required_columns = [
    "publication_ID",
    "Author_ID",
    "author_name_display_clean",
    "author_name_full"
]

for col in required_columns:
    if col not in authors.columns:
        raise ValueError(f"Column '{col}' not found in authors table.")

# If an old internal author_ID column already exists, remove it
if "author_ID" in authors.columns:
    authors = authors.drop(columns=["author_ID"])

# Rename OpenAlex Author_ID column to avoid confusion
authors = authors.rename(columns={"Author_ID": "OpenAlex_Author_ID"})

# ------------------------------------------------------------
# Clean relevant values
# ------------------------------------------------------------

authors["OpenAlex_Author_ID"] = authors["OpenAlex_Author_ID"].astype("string").str.strip()
authors["author_name_display_clean"] = authors["author_name_display_clean"].astype("string").str.strip()
authors["author_name_full"] = authors["author_name_full"].astype("string").str.strip()

# Convert empty strings to missing values
authors.loc[authors["OpenAlex_Author_ID"] == "", "OpenAlex_Author_ID"] = pd.NA
authors.loc[authors["author_name_display_clean"] == "", "author_name_display_clean"] = pd.NA
authors.loc[authors["author_name_full"] == "", "author_name_full"] = pd.NA

# ------------------------------------------------------------
# Recover missing cleaned names from author_name_full
# Example: "None (William Hogg)" -> "William Hogg"
# ------------------------------------------------------------

authors["author_name_recovered_from_full"] = pd.NA

missing_clean_name_mask = (
    authors["author_name_display_clean"].isna() &
    authors["author_name_full"].notna()
)

# Extract text inside parentheses when author_name_full has the form: None (Name)
authors.loc[missing_clean_name_mask, "author_name_recovered_from_full"] = (
    authors.loc[missing_clean_name_mask, "author_name_full"]
    .str.extract(r"^\s*None\s*\((.*?)\)\s*$", expand=False)
)

# If the pattern was not exactly "None (...)", use the whole author_name_full as fallback
still_missing_recovered = (
    missing_clean_name_mask &
    authors["author_name_recovered_from_full"].isna()
)

authors.loc[still_missing_recovered, "author_name_recovered_from_full"] = authors.loc[
    still_missing_recovered,
    "author_name_full"
]

# Clean recovered names
authors["author_name_recovered_from_full"] = (
    authors["author_name_recovered_from_full"]
    .astype("string")
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
)

authors.loc[
    authors["author_name_recovered_from_full"] == "",
    "author_name_recovered_from_full"
] = pd.NA

# ------------------------------------------------------------
# Create the name used for internal ID assignment
# Priority:
# 1. author_name_display_clean
# 2. recovered name from author_name_full
# ------------------------------------------------------------

authors["author_name_for_internal_ID"] = authors["author_name_display_clean"]

authors.loc[
    authors["author_name_for_internal_ID"].isna(),
    "author_name_for_internal_ID"
] = authors.loc[
    authors["author_name_for_internal_ID"].isna(),
    "author_name_recovered_from_full"
]

# Clean the final name-for-ID column
authors["author_name_for_internal_ID"] = (
    authors["author_name_for_internal_ID"]
    .astype("string")
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
)

authors.loc[
    authors["author_name_for_internal_ID"] == "",
    "author_name_for_internal_ID"
] = pd.NA

# Count recovered names, but do not save a separate file
recovered_rows_count = (
    authors["author_name_display_clean"].isna() &
    authors["author_name_recovered_from_full"].notna()
).sum()

# ------------------------------------------------------------
# 1. Create internal IDs for authors WITH OpenAlex Author_ID
# ------------------------------------------------------------

openalex_authors = (
    authors[authors["OpenAlex_Author_ID"].notna()]
    [["OpenAlex_Author_ID", "author_name_for_internal_ID"]]
    .drop_duplicates(subset=["OpenAlex_Author_ID"])
    .sort_values(by="OpenAlex_Author_ID")
    .reset_index(drop=True)
)

openalex_authors["ID_assignment_method"] = "OpenAlex_Author_ID"

# ------------------------------------------------------------
# 2. Create internal IDs for authors WITHOUT OpenAlex Author_ID
#    using author_name_for_internal_ID
# ------------------------------------------------------------

name_only_authors = (
    authors[
        (authors["OpenAlex_Author_ID"].isna()) &
        (authors["author_name_for_internal_ID"].notna())
    ][["author_name_for_internal_ID"]]
    .drop_duplicates()
    .sort_values(by="author_name_for_internal_ID")
    .reset_index(drop=True)
)

name_only_authors["OpenAlex_Author_ID"] = pd.NA
name_only_authors["ID_assignment_method"] = "name_without_OpenAlex_Author_ID"

# Reorder columns to match openalex_authors
name_only_authors = name_only_authors[
    ["OpenAlex_Author_ID", "author_name_for_internal_ID", "ID_assignment_method"]
]

# ------------------------------------------------------------
# 3. Combine author entities and assign internal author_IDs
# ------------------------------------------------------------

author_entities = pd.concat(
    [openalex_authors, name_only_authors],
    ignore_index=True
)

author_entities.insert(
    0,
    "author_ID",
    ["PA_AUTH_" + str(i).zfill(7) for i in range(1, len(author_entities) + 1)]
)

# Save permanent author mapping file
author_entities.to_csv(mapping_file, sep="\t", index=False)

# ------------------------------------------------------------
# 4. Merge internal author_IDs back into the full authors table
# ------------------------------------------------------------

# First merge by OpenAlex_Author_ID
openalex_mapping = author_entities[
    author_entities["OpenAlex_Author_ID"].notna()
][["OpenAlex_Author_ID", "author_ID"]].copy()

authors_with_ids = authors.merge(
    openalex_mapping,
    how="left",
    on="OpenAlex_Author_ID",
    validate="many_to_one"
)

# Then merge by author_name_for_internal_ID for rows without OpenAlex_Author_ID
name_mapping = author_entities[
    author_entities["ID_assignment_method"] == "name_without_OpenAlex_Author_ID"
][["author_name_for_internal_ID", "author_ID"]].copy()

name_mapping = name_mapping.rename(columns={"author_ID": "author_ID_from_name"})

authors_with_ids = authors_with_ids.merge(
    name_mapping,
    how="left",
    on="author_name_for_internal_ID",
    validate="many_to_one"
)

# Fill author_ID from name only when OpenAlex_Author_ID is missing
fill_from_name_mask = (
    authors_with_ids["OpenAlex_Author_ID"].isna() &
    authors_with_ids["author_ID"].isna()
)

authors_with_ids.loc[fill_from_name_mask, "author_ID"] = authors_with_ids.loc[
    fill_from_name_mask,
    "author_ID_from_name"
]

# Remove temporary helper column
authors_with_ids = authors_with_ids.drop(columns=["author_ID_from_name"])

# ------------------------------------------------------------
# 5. Move author_ID near the beginning
# ------------------------------------------------------------

author_id_col = authors_with_ids.pop("author_ID")

publication_index = authors_with_ids.columns.get_loc("publication_ID")
authors_with_ids.insert(publication_index + 1, "author_ID", author_id_col)

# ------------------------------------------------------------
# 6. Save final authors table
# ------------------------------------------------------------

authors_with_ids.to_csv(output_file, sep="\t", index=False)

# Save rows still without internal author_ID, if any
unmatched = authors_with_ids[authors_with_ids["author_ID"].isna()].copy()
unmatched.to_csv(unmatched_file, sep="\t", index=False)

# ------------------------------------------------------------
# 7. Checks
# ------------------------------------------------------------

print("Done.")

print(f"\nRows in original authors table: {len(authors)}")
print(f"Rows in final authors table: {len(authors_with_ids)}")

if len(authors) == len(authors_with_ids):
    print("OK: row count unchanged after merge.")
else:
    print("WARNING: row count changed after merge.")
    print(f"Difference: {len(authors_with_ids) - len(authors)}")

print(f"\nRows where name was recovered from author_name_full: {recovered_rows_count}")

print(f"\nUnique OpenAlex authors assigned internal IDs: {openalex_authors['OpenAlex_Author_ID'].nunique()}")
print(f"Unique name-only authors assigned internal IDs: {len(name_only_authors)}")
print(f"Total internal author_IDs created: {author_entities['author_ID'].nunique()}")

print(f"\nDuplicate internal author_IDs in mapping file: {author_entities['author_ID'].duplicated().sum()}")
print(f"Duplicate OpenAlex_Author_IDs in mapping file: {author_entities['OpenAlex_Author_ID'].dropna().duplicated().sum()}")
print(f"Duplicate name-only entries in mapping file: {name_only_authors['author_name_for_internal_ID'].duplicated().sum()}")

print(f"\nRows still without internal author_ID: {len(unmatched)}")

if len(unmatched) == 0:
    print("OK: every authorship row received an internal author_ID.")
else:
    print("WARNING: some rows still did not receive an internal author_ID.")
    print(f"Rows without internal author_ID saved to: {unmatched_file}")

print(f"\nSaved final authors table to: {output_file}")
print(f"Saved author mapping file to: {mapping_file}")
print(f"Saved unmatched rows file to: {unmatched_file}")