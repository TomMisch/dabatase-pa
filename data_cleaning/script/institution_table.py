from pathlib import Path
import re
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

input_file = BASE_PATH / "authors_table_cleaned_with_publication_ID_and_author_ID.tsv"

output_file = BASE_PATH / "institutions_table_from_authors.tsv"

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
    "author_ID",
    "Institutions",
    "Affiliations"
]

for col in required_columns:
    if col not in authors.columns:
        raise ValueError(f"Column '{col}' not found in authors table.")

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def clean_value(value):
    """Clean a text value and convert empty strings to pd.NA."""
    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value == "" or value.lower() in ["nan", "none"]:
        return pd.NA

    return value


def ordinal_prefix(number):
    """Return the prefix for repeated institution/affiliation columns."""

    prefixes = {
        1: "",
        2: "Second_",
        3: "Third_",
        4: "Fourth_",
        5: "Fifth_",
        6: "Sixth_",
        7: "Seventh_",
        8: "Eighth_",
        9: "Ninth_",
        10: "Tenth_",
        11: "Eleventh_",
        12: "Twelfth_",
        13: "Thirteenth_",
        14: "Fourteenth_",
        15: "Fifteenth_"
    }

    return prefixes.get(number, f"{number}th_")


def clean_affiliation_text(value):
    """
    Clean one affiliation string.

    Example:
    2University of Melbourne, Victoria, Australia
    becomes:
    University of Melbourne, Victoria, Australia
    """

    value = clean_value(value)

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    # Remove leading numbering such as:
    # 1University of X
    # 2 University of X
    value = re.sub(r"^\s*\d+\s*", "", value)

    value = re.sub(r"\s+", " ", value).strip()

    if value == "":
        return pd.NA

    return value


def parse_single_institution(institution_text):
    """
    Parse one institution string.

    Example:
    The University of Queensland ### ID: https://openalex.org/I165143802 ### ROR: https://ror.org/00rqy9422 ### Type: education
    """

    result = {
        "Institution": pd.NA,
        "OpenAlex_Institution_ID": pd.NA,
        "ROR": pd.NA,
        "Type": pd.NA
    }

    institution_text = clean_value(institution_text)

    if pd.isna(institution_text):
        return result

    parts = [part.strip() for part in str(institution_text).split("###")]

    # First part is the institution name
    if len(parts) > 0:
        result["Institution"] = clean_value(parts[0])

    # Remaining parts are key-value pairs
    for part in parts[1:]:
        if ":" not in part:
            continue

        key, value = part.split(":", 1)

        key = key.strip().lower()
        value = clean_value(value)

        if key == "id":
            result["OpenAlex_Institution_ID"] = value
        elif key == "ror":
            result["ROR"] = value
        elif key == "type":
            result["Type"] = value

    return result


def parse_institutions_cell(institutions_cell):
    """
    Parse the full Institutions cell.

    Multiple institutions are separated by:
    ||
    """

    institutions_cell = clean_value(institutions_cell)

    if pd.isna(institutions_cell):
        return []

    institution_strings = [
        inst.strip()
        for inst in str(institutions_cell).split("||")
        if inst.strip() != ""
    ]

    return [
        parse_single_institution(inst)
        for inst in institution_strings
    ]


def parse_affiliations_cell(affiliations_cell):
    """
    Parse the Affiliations cell.

    Multiple affiliations may be separated by:
    #TAB#
    ||
    """

    affiliations_cell = clean_value(affiliations_cell)

    if pd.isna(affiliations_cell):
        return []

    affiliation_strings = [
        aff.strip()
        for aff in re.split(r"\s*(?:#TAB#|\|\|)\s*", str(affiliations_cell))
        if aff.strip() != ""
    ]

    cleaned_affiliations = []

    for aff in affiliation_strings:
        cleaned_aff = clean_affiliation_text(aff)

        if not pd.isna(cleaned_aff):
            cleaned_affiliations.append(cleaned_aff)

    return cleaned_affiliations


# ------------------------------------------------------------
# Parse institutions and affiliations for each row
# ------------------------------------------------------------

records = []
max_affiliations = 0
mismatch_count = 0

for _, row in authors.iterrows():

    institutions = parse_institutions_cell(row["Institutions"])
    affiliations = parse_affiliations_cell(row["Affiliations"])

    max_items = max(
        len(institutions),
        len(affiliations)
    )

    max_affiliations = max(max_affiliations, max_items)

    if len(institutions) != len(affiliations):
        mismatch_count += 1

    record = {
        "publication_ID": row["publication_ID"],
        "author_ID": row["author_ID"]
    }

    optional_columns = [
        "OpenAlex_Author_ID",
        "author_name_display_clean",
        "author_name_full",
        "author_position"
    ]

    for col in optional_columns:
        if col in authors.columns:
            record[col] = row[col]

    for i in range(1, max_items + 1):

        prefix = ordinal_prefix(i)

        if i <= len(institutions):
            institution_data = institutions[i - 1]
        else:
            institution_data = {
                "Institution": pd.NA,
                "OpenAlex_Institution_ID": pd.NA,
                "ROR": pd.NA,
                "Type": pd.NA
            }

        affiliation_value = affiliations[i - 1] if i <= len(affiliations) else pd.NA

        record[f"{prefix}Institution"] = institution_data["Institution"]
        record[f"{prefix}OpenAlex_Institution_ID"] = institution_data["OpenAlex_Institution_ID"]
        record[f"{prefix}ROR"] = institution_data["ROR"]
        record[f"{prefix}Type"] = institution_data["Type"]
        record[f"{prefix}Affiliation"] = affiliation_value

    records.append(record)

institutions_table = pd.DataFrame(records)

# ------------------------------------------------------------
# Ensure stable column order
# ------------------------------------------------------------

base_columns = [
    "publication_ID",
    "author_ID"
]

optional_columns_present = [
    col for col in [
        "OpenAlex_Author_ID",
        "author_name_display_clean",
        "author_name_full",
        "author_position"
    ]
    if col in institutions_table.columns
]

institution_columns = []

for i in range(1, max_affiliations + 1):

    prefix = ordinal_prefix(i)

    institution_columns.extend([
        f"{prefix}Institution",
        f"{prefix}OpenAlex_Institution_ID",
        f"{prefix}ROR",
        f"{prefix}Type",
        f"{prefix}Affiliation"
    ])

institution_columns = [
    col for col in institution_columns
    if col in institutions_table.columns
]

final_columns = base_columns + optional_columns_present + institution_columns

institutions_table = institutions_table[final_columns]

# ------------------------------------------------------------
# Save institution table
# ------------------------------------------------------------

institutions_table.to_csv(output_file, sep="\t", index=False)

# ------------------------------------------------------------
# Checks
# ------------------------------------------------------------

print("Done.")

print(f"\nRows in authors table: {len(authors)}")
print(f"Rows in institution table: {len(institutions_table)}")

if len(authors) == len(institutions_table):
    print("OK: one institution-table row was created for each author-publication row.")
else:
    print("WARNING: row count changed.")
    print(f"Difference: {len(institutions_table) - len(authors)}")

print(f"\nMaximum number of institutions/affiliations found in one row: {max_affiliations}")

no_first_institution = (
    institutions_table["Institution"].isna().sum()
    if "Institution" in institutions_table.columns
    else len(institutions_table)
)

no_first_affiliation = (
    institutions_table["Affiliation"].isna().sum()
    if "Affiliation" in institutions_table.columns
    else len(institutions_table)
)

print(f"Rows with no first institution information: {no_first_institution}")
print(f"Rows with no first affiliation information: {no_first_affiliation}")

print(f"\nRows where institution/affiliation counts do not match: {mismatch_count}")

print(f"\nSaved institution table to: {output_file}")