from pathlib import Path
import pandas as pd

BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

input_file = BASE_PATH / "openalex_merged_titles_cleaned.tsv"

output_file = BASE_PATH / "openalex_merged_titles_cleaned_with_publication_ID.tsv"
mapping_file = BASE_PATH / "publication_ID_mapping.tsv"

df = pd.read_csv(input_file, sep="\t", dtype=str)

# Create a temporary numeric version of Year for correct chronological sorting
df["Year_sort"] = pd.to_numeric(df["Year"], errors="coerce")

# Sort oldest to newest.
# The second and third columns make the order reproducible when several publications have the same year.
df = df.sort_values(
    by=["Year_sort", "Title", "OpenAlex_ID"],
    ascending=[True, True, True],
    na_position="last"
).reset_index(drop=True)

# Add internal publication identifier as the first column
df.insert(
    0,
    "publication_ID",
    ["PA_PUB_" + str(i).zfill(7) for i in range(1, len(df) + 1)]
)

# Remove temporary sorting column
df = df.drop(columns=["Year_sort"])

# Save full publication file as TSV
df.to_csv(output_file, sep="\t", index=False)

# Save mapping file as TSV
mapping = df[["publication_ID", "OpenAlex_ID", "Title", "Year"]].copy()
mapping.to_csv(mapping_file, sep="\t", index=False)

print("Done.")
print(f"Saved publication file to: {output_file}")
print(f"Saved mapping file to: {mapping_file}")
print(f"Total publications assigned IDs: {len(df)}")

input("Press ENTER for assigning publication_ID to the authorship table")

from pathlib import Path
import pandas as pd

BASE_PATH = Path(
    r"C:\Users\e411394\OneDrive - London South Bank University\database_pa\data_retrieval\files\raw_data"
)

authors_file = BASE_PATH / "authors_table_cleaned.tsv"
mapping_file = BASE_PATH / "publication_ID_mapping.tsv"

output_file = BASE_PATH / "authors_table_cleaned_with_publication_ID.tsv"
unmatched_file = BASE_PATH / "authors_table_unmatched_publication_IDs.tsv"

# Read files
authors = pd.read_csv(authors_file, sep="\t", dtype=str)
mapping = pd.read_csv(mapping_file, sep="\t", dtype=str)

# Clean column names, especially to remove accidental spaces
authors.columns = authors.columns.str.strip()
mapping.columns = mapping.columns.str.strip()

# Basic checks
required_authors_col = "work_OpenAlex_ID"
required_mapping_cols = ["publication_ID", "OpenAlex_ID"]

if required_authors_col not in authors.columns:
    raise ValueError(f"Column '{required_authors_col}' not found in authors table.")

for col in required_mapping_cols:
    if col not in mapping.columns:
        raise ValueError(f"Column '{col}' not found in mapping file.")

# Clean OpenAlex ID values
authors["work_OpenAlex_ID"] = authors["work_OpenAlex_ID"].str.strip()
mapping["OpenAlex_ID"] = mapping["OpenAlex_ID"].str.strip()

# Keep only the necessary mapping columns
mapping_small = mapping[["publication_ID", "OpenAlex_ID"]].copy()

# Check that each OpenAlex_ID in the mapping has only one publication_ID
duplicates_in_mapping = mapping_small["OpenAlex_ID"].duplicated().sum()

if duplicates_in_mapping > 0:
    raise ValueError(
        f"The mapping file contains {duplicates_in_mapping} duplicated OpenAlex_ID values. "
        "Please fix this before merging."
    )

# Merge publication_ID into the authors table
authors_with_ids = authors.merge(
    mapping_small,
    how="left",
    left_on="work_OpenAlex_ID",
    right_on="OpenAlex_ID",
    validate="many_to_one"
)

# Drop duplicated OpenAlex_ID column from the mapping
authors_with_ids = authors_with_ids.drop(columns=["OpenAlex_ID"])

# Move publication_ID to the first column
publication_id_col = authors_with_ids.pop("publication_ID")
authors_with_ids.insert(0, "publication_ID", publication_id_col)

# Save final authors table
authors_with_ids.to_csv(output_file, sep="\t", index=False)

# Save unmatched rows, if any
unmatched = authors_with_ids[authors_with_ids["publication_ID"].isna()].copy()
unmatched.to_csv(unmatched_file, sep="\t", index=False)

# Print checks
print("Done.")
print(f"Rows in original authors table: {len(authors)}")
print(f"Rows in authors table with publication_ID: {len(authors_with_ids)}")

if len(authors) == len(authors_with_ids):
    print("OK: row count unchanged after merge.")
else:
    print("WARNING: row count changed after merge.")

print(f"Rows without publication_ID: {len(unmatched)}")

if len(unmatched) == 0:
    print("OK: every author row received a publication_ID.")
else:
    print(f"WARNING: some author rows did not receive a publication_ID.")
    print(f"Unmatched rows saved to: {unmatched_file}")

print(f"Saved final file to: {output_file}")
