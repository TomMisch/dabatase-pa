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

input_file = BASE_PATH / "institutions_table_from_authors_cleaned.tsv"

output_file = BASE_PATH / "institution_consistency_checks.xlsx"

# ------------------------------------------------------------
# Read institution table
# ------------------------------------------------------------

df = pd.read_csv(input_file, sep="\t", dtype=str)
df.columns = df.columns.str.strip()

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def clean_value(value):
    """Clean values and convert empty/nan/none strings to pd.NA."""
    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value == "" or value.lower() in ["nan", "none", "<na>"]:
        return pd.NA

    return value


def normalise_text(value):
    """Normalise institution names for comparison."""
    value = clean_value(value)

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalise_id(value):
    """Normalise IDs/URLs for comparison."""
    value = clean_value(value)

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()
    value = value.rstrip("/")

    return value


def position_label_from_prefix(prefix):
    """Convert column prefix into a readable position label."""
    if prefix == "":
        return "First"

    return prefix.rstrip("_")


# ------------------------------------------------------------
# Detect institution column groups
# ------------------------------------------------------------

institution_columns = []

for col in df.columns:
    if col == "Institution":
        institution_columns.append(col)
    elif col.endswith("_Institution") and not col.endswith("OpenAlex_Institution"):
        institution_columns.append(col)

# Sort columns in logical order: First, Second, Third, etc.
known_order = {
    "Institution": 1,
    "Second_Institution": 2,
    "Third_Institution": 3,
    "Fourth_Institution": 4,
    "Fifth_Institution": 5,
    "Sixth_Institution": 6,
    "Seventh_Institution": 7,
    "Eighth_Institution": 8,
    "Ninth_Institution": 9,
    "Tenth_Institution": 10,
    "Eleventh_Institution": 11,
    "Twelfth_Institution": 12,
    "Thirteenth_Institution": 13,
    "Fourteenth_Institution": 14,
    "Fifteenth_Institution": 15,
}

institution_columns = sorted(
    institution_columns,
    key=lambda x: known_order.get(x, 999)
)

if len(institution_columns) == 0:
    raise ValueError("No Institution columns found in the institution table.")

# ------------------------------------------------------------
# Convert wide institution table into a long table
# ------------------------------------------------------------

long_records = []

for _, row in df.iterrows():

    for institution_col in institution_columns:

        if institution_col == "Institution":
            prefix = ""
        else:
            prefix = institution_col.replace("Institution", "")

        position_label = position_label_from_prefix(prefix)

        openalex_col = f"{prefix}OpenAlex_Institution_ID"
        ror_col = f"{prefix}ROR"
        type_col = f"{prefix}Type"
        affiliation_col = f"{prefix}Affiliation"

        institution = clean_value(row[institution_col]) if institution_col in df.columns else pd.NA
        openalex_id = clean_value(row[openalex_col]) if openalex_col in df.columns else pd.NA
        ror = clean_value(row[ror_col]) if ror_col in df.columns else pd.NA
        institution_type = clean_value(row[type_col]) if type_col in df.columns else pd.NA
        affiliation = clean_value(row[affiliation_col]) if affiliation_col in df.columns else pd.NA

        # Skip completely empty institution slots
        if (
            pd.isna(institution)
            and pd.isna(openalex_id)
            and pd.isna(ror)
            and pd.isna(institution_type)
            and pd.isna(affiliation)
        ):
            continue

        long_records.append({
            "publication_ID": row["publication_ID"] if "publication_ID" in df.columns else pd.NA,
            "author_ID": row["author_ID"] if "author_ID" in df.columns else pd.NA,
            "affiliation_position": position_label,
            "Institution": institution,
            "OpenAlex_Institution_ID": openalex_id,
            "ROR": ror,
            "Type": institution_type,
            "Affiliation": affiliation,
            "Institution_norm": normalise_text(institution),
            "OpenAlex_Institution_ID_norm": normalise_id(openalex_id),
            "ROR_norm": normalise_id(ror)
        })

long_df = pd.DataFrame(long_records)

if len(long_df) == 0:
    raise ValueError("No institution data found after reshaping the table.")

# ------------------------------------------------------------
# Function to run consistency checks
# ------------------------------------------------------------

def run_consistency_check(
    data,
    check_number,
    check_description,
    key_column,
    key_norm_column,
    value_column,
    value_norm_column
):
    """
    Finds cases where the same key has more than one distinct value.

    Example:
    Same ROR -> more than one OpenAlex_Institution_ID
    """

    working = data[
        data[key_norm_column].notna()
        & data[value_norm_column].notna()
    ].copy()

    if len(working) == 0:
        return pd.DataFrame()

    grouped = (
        working
        .groupby(key_norm_column)[value_norm_column]
        .nunique()
        .reset_index(name="number_of_distinct_values")
    )

    problematic_keys = grouped[
        grouped["number_of_distinct_values"] > 1
    ][key_norm_column]

    problems = working[
        working[key_norm_column].isin(problematic_keys)
    ].copy()

    if len(problems) == 0:
        return pd.DataFrame()

    # Create summary columns for each problematic key
    value_summary = (
        problems
        .groupby(key_norm_column)[value_column]
        .apply(lambda x: " || ".join(sorted(set([str(v) for v in x.dropna()]))))
        .reset_index(name="conflicting_values")
    )

    position_summary = (
        problems
        .groupby(key_norm_column)["affiliation_position"]
        .apply(lambda x: " || ".join(sorted(set([str(v) for v in x.dropna()]))))
        .reset_index(name="positions_involved")
    )

    problem_counts = (
        problems
        .groupby(key_norm_column)
        .size()
        .reset_index(name="number_of_rows_involved")
    )

    problems = problems.merge(value_summary, on=key_norm_column, how="left")
    problems = problems.merge(position_summary, on=key_norm_column, how="left")
    problems = problems.merge(problem_counts, on=key_norm_column, how="left")

    problems.insert(0, "check_number", check_number)
    problems.insert(1, "check_description", check_description)
    problems.insert(2, "key_column", key_column)
    problems.insert(3, "key_value", problems[key_column])
    problems.insert(4, "conflicting_column", value_column)

    output_columns = [
        "check_number",
        "check_description",
        "key_column",
        "key_value",
        "conflicting_column",
        "conflicting_values",
        "number_of_rows_involved",
        "positions_involved",
        "affiliation_position",
        "publication_ID",
        "author_ID",
        "Institution",
        "OpenAlex_Institution_ID",
        "ROR",
        "Type",
        "Affiliation"
    ]

    return problems[output_columns].sort_values(
        by=[
            "check_number",
            "key_value",
            "affiliation_position",
            "publication_ID",
            "author_ID"
        ],
        na_position="last"
    )


# ------------------------------------------------------------
# Run the six checks
# ------------------------------------------------------------

checks = []

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=1,
        check_description="Same ROR has more than one OpenAlex_Institution_ID",
        key_column="ROR",
        key_norm_column="ROR_norm",
        value_column="OpenAlex_Institution_ID",
        value_norm_column="OpenAlex_Institution_ID_norm"
    )
)

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=2,
        check_description="Same OpenAlex_Institution_ID has more than one ROR",
        key_column="OpenAlex_Institution_ID",
        key_norm_column="OpenAlex_Institution_ID_norm",
        value_column="ROR",
        value_norm_column="ROR_norm"
    )
)

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=3,
        check_description="Same ROR has more than one Institution",
        key_column="ROR",
        key_norm_column="ROR_norm",
        value_column="Institution",
        value_norm_column="Institution_norm"
    )
)

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=4,
        check_description="Same Institution has more than one ROR",
        key_column="Institution",
        key_norm_column="Institution_norm",
        value_column="ROR",
        value_norm_column="ROR_norm"
    )
)

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=5,
        check_description="Same OpenAlex_Institution_ID has more than one Institution",
        key_column="OpenAlex_Institution_ID",
        key_norm_column="OpenAlex_Institution_ID_norm",
        value_column="Institution",
        value_norm_column="Institution_norm"
    )
)

checks.append(
    run_consistency_check(
        data=long_df,
        check_number=6,
        check_description="Same Institution has more than one OpenAlex_Institution_ID",
        key_column="Institution",
        key_norm_column="Institution_norm",
        value_column="OpenAlex_Institution_ID",
        value_norm_column="OpenAlex_Institution_ID_norm"
    )
)

# Replace empty checks with empty dataframes with the right structure
problem_columns = [
    "check_number",
    "check_description",
    "key_column",
    "key_value",
    "conflicting_column",
    "conflicting_values",
    "number_of_rows_involved",
    "positions_involved",
    "affiliation_position",
    "publication_ID",
    "author_ID",
    "Institution",
    "OpenAlex_Institution_ID",
    "ROR",
    "Type",
    "Affiliation"
]

checks = [
    check if len(check) > 0 else pd.DataFrame(columns=problem_columns)
    for check in checks
]

all_problems = pd.concat(checks, ignore_index=True)

# ------------------------------------------------------------
# Create summary table
# ------------------------------------------------------------

summary_records = []

for i, check_df in enumerate(checks, start=1):

    if len(check_df) == 0:
        problem_keys = 0
        problem_rows = 0
    else:
        problem_keys = check_df[["check_number", "key_column", "key_value"]].drop_duplicates().shape[0]
        problem_rows = len(check_df)

    summary_records.append({
        "check_number": i,
        "check_description": [
            "Same ROR has more than one OpenAlex_Institution_ID",
            "Same OpenAlex_Institution_ID has more than one ROR",
            "Same ROR has more than one Institution",
            "Same Institution has more than one ROR",
            "Same OpenAlex_Institution_ID has more than one Institution",
            "Same Institution has more than one OpenAlex_Institution_ID"
        ][i - 1],
        "number_of_problematic_keys": problem_keys,
        "number_of_rows_involved": problem_rows
    })

summary = pd.DataFrame(summary_records)

# ------------------------------------------------------------
# Save everything to one Excel workbook
# ------------------------------------------------------------

sheet_names = [
    "Check_1_ROR_to_OpenAlex",
    "Check_2_OpenAlex_to_ROR",
    "Check_3_ROR_to_Institution",
    "Check_4_Institution_to_ROR",
    "Check_5_OpenAlex_to_Institution",
    "Check_6_Institution_to_OpenAlex"
]

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

    summary.to_excel(writer, sheet_name="Summary", index=False)
    all_problems.to_excel(writer, sheet_name="All_Problems", index=False)

    for check_df, sheet_name in zip(checks, sheet_names):
        check_df.to_excel(writer, sheet_name=sheet_name, index=False)

# ------------------------------------------------------------
# Print checks
# ------------------------------------------------------------

print("Done.")

print(f"\nInstitution slots detected:")
for col in institution_columns:
    print(f"- {col}")

print(f"\nRows in original institution table: {len(df)}")
print(f"Rows in long institution table: {len(long_df)}")

print("\nSummary of problems:")
print(summary.to_string(index=False))

print(f"\nTotal problem rows across all checks: {len(all_problems)}")
print(f"\nSaved Excel file to: {output_file}")