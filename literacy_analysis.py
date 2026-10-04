import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# File locations
# ---------------------------------------------------------
BASE = Path(__file__).resolve().parent

literacy_file = BASE / "Table29.6-States(1).xls"
enrollment_file = BASE / "UDISE_2021_22_Table_5.17_2 (1).csv"

OUTPUT = BASE / "output"
OUTPUT.mkdir(exist_ok=True)

# ---------------------------------------------------------
# Read datasets
# ---------------------------------------------------------
literacy = pd.read_excel(literacy_file, header=None)
enrollment = pd.read_csv(enrollment_file, header=None)

print("Literacy dataset shape:", literacy.shape)
print("Enrollment dataset shape:", enrollment.shape)

# ---------------------------------------------------------
# Q1: Average 2011 literacy rate
# ---------------------------------------------------------
# The literacy table contains 2011 Rural and Urban Person values.
# We calculate the average of Rural and Urban Person literacy
# for each state/UT and then calculate the overall mean.

# Find the row containing the column headings
header_row = None

for i in range(min(15, len(literacy))):
    row_text = " ".join(
        literacy.iloc[i].astype(str).str.lower().tolist()
    )
    if "2011" in row_text and "rural" in row_text:
        header_row = i
        break

if header_row is None:
    header_row = 4

headers = literacy.iloc[header_row].astype(str).tolist()

# Locate useful columns
rural_col = None
urban_col = None

for i, value in enumerate(headers):
    value_lower = value.lower()

    if "2011" in value_lower and "rural" in value_lower and "person" in value_lower:
        rural_col = i

    if "2011" in value_lower and "urban" in value_lower and "person" in value_lower:
        urban_col = i

# If exact names are not found, use likely columns from the table.
if rural_col is None or urban_col is None:
    print("Could not automatically identify Rural/Urban Person columns.")
    print("Please inspect the literacy dataset columns.")
else:
    rural_values = pd.to_numeric(
        literacy.iloc[header_row + 1:, rural_col],
        errors="coerce"
    )

    urban_values = pd.to_numeric(
        literacy.iloc[header_row + 1:, urban_col],
        errors="coerce"
    )

    state_average = (rural_values + urban_values) / 2

    average_literacy = state_average.mean()

    with open(OUTPUT / "q1_average_literacy.txt", "w") as f:
        f.write(
            f"Average 2011 literacy rate: "
            f"{average_literacy:.2f}%\n"
        )

    print(f"Q1 Average 2011 literacy rate: {average_literacy:.2f}%")

# ---------------------------------------------------------
# Q2: Gender-wise filtering
# ---------------------------------------------------------
# Keep rows containing gender information from the enrollment data.

gender_rows = enrollment[
    enrollment.apply(
        lambda row: row.astype(str).str.contains(
            "boys|girls|male|female",
            case=False,
            regex=True
        ).any(),
        axis=1
    )
]

gender_rows.to_csv(
    OUTPUT / "q2_gender_filtered.csv",
    index=False
)

print("Q2 gender-filtered data saved.")

# ---------------------------------------------------------
# Q3: Missing enrollment values
# ---------------------------------------------------------
numeric_enrollment = enrollment.apply(
    pd.to_numeric,
    errors="coerce"
)

missing_before = int(numeric_enrollment.isna().sum().sum())

# Median imputation is used only if numeric missing values exist.
filled_enrollment = numeric_enrollment.copy()

for column in filled_enrollment.columns:
    median_value = filled_enrollment[column].median()

    if pd.notna(median_value):
        filled_enrollment[column] = filled_enrollment[column].fillna(
            median_value
        )

missing_after = int(filled_enrollment.isna().sum().sum())

missing_summary = pd.DataFrame({
    "missing_values_before": [missing_before],
    "missing_values_after": [missing_after]
})

missing_summary.to_csv(
    OUTPUT / "q3_missing_enrollment.csv",
    index=False
)

print("Q3 missing values before:", missing_before)
print("Q3 missing values after:", missing_after)

# ---------------------------------------------------------
# Q4: Age-group and region grouping
# ---------------------------------------------------------
# Search the enrollment header row.
header_index = 0

for i in range(min(5, len(enrollment))):
    row_text = " ".join(
        enrollment.iloc[i].astype(str).str.lower().tolist()
    )

    if "state" in row_text or "ut" in row_text:
        header_index = i
        break

enrollment_clean = enrollment.iloc[header_index + 1:].copy()
enrollment_clean.columns = enrollment.iloc[header_index].astype(str)

# Possible age-group keywords
age_groups = ["<6", "6-10", "11-13", "14-15", "16-17", ">17"]

# Find columns containing age-group labels.
age_columns = {}

for age in age_groups:
    matching = [
        col for col in enrollment_clean.columns
        if age.lower() in str(col).lower()
    ]

    if matching:
        age_columns[age] = matching

# State/UT column
state_column = None

for col in enrollment_clean.columns:
    col_text = str(col).lower()

    if "state" in col_text or "ut" in col_text:
        state_column = col
        break

if state_column is None:
    state_column = enrollment_clean.columns[0]

# Simple region classification
def get_region(state):
    state = str(state).lower()

    north = [
        "jammu", "kashmir", "himachal", "punjab", "haryana",
        "delhi", "uttarakhand", "uttar pradesh", "rajasthan"
    ]

    south = [
        "andhra", "telangana", "karnataka", "kerala",
        "tamil", "puducherry"
    ]

    east = [
        "bihar", "jharkhand", "odisha", "west bengal"
    ]

    west = [
        "gujarat", "maharashtra", "goa"
    ]

    northeast = [
        "assam", "arunachal", "manipur", "meghalaya",
        "mizoram", "nagaland", "sikkim", "tripura"
    ]

    if any(x in state for x in north):
        return "North"
    elif any(x in state for x in south):
        return "South"
    elif any(x in state for x in east):
        return "East"
    elif any(x in state for x in west):
        return "West"
    elif any(x in state for x in northeast):
        return "Northeast"
    else:
        return "Other"

if age_columns:
    q4_rows = []

    for age, columns in age_columns.items():
        for column in columns:
            values = pd.to_numeric(
                enrollment_clean[column],
                errors="coerce"
            )

            temp = pd.DataFrame({
                "State_UT": enrollment_clean[state_column].astype(str),
                "Age_Group": age,
                "Enrollment": values
            })

            temp["Region"] = temp["State_UT"].apply(get_region)

            q4_rows.append(temp)

    q4_data = pd.concat(q4_rows, ignore_index=True)

    q4_summary = (
        q4_data
        .groupby(["Region", "Age_Group"], as_index=False)["Enrollment"]
        .sum()
    )

else:
    q4_summary = pd.DataFrame(
        columns=["Region", "Age_Group", "Enrollment"]
    )

q4_summary.to_csv(
    OUTPUT / "q4_age_region_enrollment.csv",
    index=False
)

print("Q4 age-group and region data saved.")

# ---------------------------------------------------------
# Q5: Gender-wise literacy comparison
# ---------------------------------------------------------
# Search for Male/Female/Person columns in the literacy table.

male_col = None
female_col = None

for i, value in enumerate(headers):
    value_lower = value.lower()

    if "2011" in value_lower and "male" in value_lower:
        male_col = i

    if "2011" in value_lower and "female" in value_lower:
        female_col = i

if male_col is not None and female_col is not None:

    male_values = pd.to_numeric(
        literacy.iloc[header_row + 1:, male_col],
        errors="coerce"
    )

    female_values = pd.to_numeric(
        literacy.iloc[header_row + 1:, female_col],
        errors="coerce"
    )

    comparison = pd.DataFrame({
        "Gender": ["Male", "Female"],
        "Average_Literacy": [
            male_values.mean(),
            female_values.mean()
        ]
    })

    plt.figure(figsize=(7, 5))

    plt.bar(
        comparison["Gender"],
        comparison["Average_Literacy"]
    )

    plt.title("Gender-wise Literacy Comparison - 2011")
    plt.xlabel("Gender")
    plt.ylabel("Average Literacy Rate (%)")

    plt.tight_layout()

    plt.savefig(
        OUTPUT / "q5_gender_wise_literacy.png",
        dpi=300
    )

    plt.close()

    print("Q5 gender-wise graph saved.")

else:
    print("Could not identify Male/Female literacy columns.")

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------
summary = pd.DataFrame({
    "Question": ["Q1", "Q2", "Q3", "Q4", "Q5"],
    "Task": [
        "Average 2011 literacy rate",
        "Gender-wise filtering",
        "Missing enrollment values",
        "Age-group and region grouping",
        "Gender-wise literacy comparison"
    ],
    "Output": [
        "q1_average_literacy.txt",
        "q2_gender_filtered.csv",
        "q3_missing_enrollment.csv",
        "q4_age_region_enrollment.csv",
        "q5_gender_wise_literacy.png"
    ]
})

summary.to_csv(
    OUTPUT / "analysis_summary.csv",
    index=False
)

print("\nAnalysis completed.")
print("Check the output folder for results.")
