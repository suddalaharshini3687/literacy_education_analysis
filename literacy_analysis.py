import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "output"
OUTPUT.mkdir(exist_ok=True)

literacy_file = BASE / "Table29.6-States(1).xls"
enrollment_file = BASE / "UDISE_2021_22_Table_5.17_2 (1).csv"

lit_raw = pd.read_excel(literacy_file, header=None)
enr = pd.read_csv(enrollment_file)

# Find literacy table headers
header_row = None
for i in range(min(15, len(lit_raw))):
    row_text = " ".join(lit_raw.iloc[i].astype(str)).lower()
    if "2011" in row_text and "rural" in row_text and "urban" in row_text:
        header_row = i
        break

if header_row is None:
    raise ValueError("Could not find literacy table header row.")

lit = lit_raw.iloc[header_row + 1:].copy()
lit.columns = lit_raw.iloc[header_row].astype(str).str.strip()
state_col = lit.columns[0]

names = lit[state_col].astype(str).str.strip()
lit = lit[
    names.ne("")
    & names.str.lower().ne("nan")
    & ~names.str.lower().str.fullmatch(r"all india|india")
].copy()


def find_column(columns, *terms):
    for col in columns:
        name = str(col).lower()
        if all(term.lower() in name for term in terms):
            return col
    raise ValueError(f"Column not found: {terms}")


# Q1: Average literacy rate across states/UTs
rural_person = find_column(lit.columns, "2011", "rural", "person")
urban_person = find_column(lit.columns, "2011", "urban", "person")

for col in [rural_person, urban_person]:
    lit[col] = pd.to_numeric(lit[col], errors="coerce")

lit["Average_Rural_Urban"] = lit[
    [rural_person, urban_person]
].mean(axis=1)

q1_average = lit["Average_Rural_Urban"].mean()

(OUTPUT / "q1_average_literacy.txt").write_text(
    "Method: Average rural and urban Person literacy rates per state/UT, "
    "then average across states/UTs, excluding India aggregate.\n"
    f"Average 2011 literacy rate: {q1_average:.2f}%\n",
    encoding="utf-8"
)


# Q2: Gender-related enrollment columns; exclude India total
state_col_enr = enr.columns[0]
state_names = enr[state_col_enr].astype(str).str.strip()

enr_states = enr[
    state_names.ne("")
    & state_names.str.lower().ne("nan")
    & ~state_names.str.lower().str.fullmatch(r"all india|india")
].copy()

gender_cols = [
    c for c in enr.columns[1:]
    if re.search(r"\b(boys|girls|male|female)\b", str(c), re.I)
]

if not gender_cols:
    raise ValueError("No gender-related enrollment columns found.")

enr_states[[state_col_enr] + gender_cols].to_csv(
    OUTPUT / "q2_gender_filtered.csv", index=False
)


# Q3: Count missing and non-numeric enrollment cells
numeric = enr.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
original = enr.iloc[:, 1:].astype("string")
nonblank = original.apply(lambda c: c.str.strip().ne("").fillna(False))

missing_count = int(
    (numeric.isna() & nonblank).sum().sum()
    + enr.iloc[:, 1:].isna().sum().sum()
)

pd.DataFrame([{
    "numeric_cells_checked": int(numeric.size),
    "missing_or_non_numeric_values": missing_count,
    "action": "No automatic imputation; inspect source data before handling missing values."
}]).to_csv(OUTPUT / "q3_missing_enrollment.csv", index=False)


# Q4: Enrollment by age group and region
age_groups = ["<6", "6-10", "11-13", "14-15", "16-17", ">17"]
age_columns = {}

for age in age_groups:
    matches = [
        c for c in enr.columns
        if age in str(c)
        and re.search(r"\bAll\s*-\s*Total\b", str(c), re.I)
    ]
    if matches:
        age_columns[age] = matches[0]


def get_region(state):
    s = str(state).lower().strip()

    mapping = {
        "North": [
            "jammu", "kashmir", "himachal", "punjab", "haryana",
            "delhi", "uttarakhand", "uttar pradesh", "rajasthan",
            "chandigarh", "ladakh"
        ],
        "South": [
            "andhra", "telangana", "karnataka", "kerala",
            "tamil", "puducherry", "lakshadweep"
        ],
        "East": [
            "bihar", "jharkhand", "odisha", "orissa", "west bengal"
        ],
        "West": [
            "gujarat", "maharashtra", "goa", "dadra", "daman", "diu"
        ],
        "Northeast": [
            "assam", "arunachal", "manipur", "meghalaya",
            "mizoram", "nagaland", "sikkim", "tripura"
        ],
        "Central": ["madhya pradesh", "chhattisgarh"],
        "Islands": ["andaman", "nicobar"]
    }

    for region, keywords in mapping.items():
        if any(word in s for word in keywords):
            return region

    return "Unclassified"


q4_rows = []

for _, row in enr_states.iterrows():
    state = str(row[state_col_enr]).strip()
    for age, col in age_columns.items():
        q4_rows.append({
            "State_UT": state,
            "Region": get_region(state),
            "Age_Group": age,
            "Enrollment": pd.to_numeric(row[col], errors="coerce")
        })

q4_detail = pd.DataFrame(q4_rows)

if not q4_detail.empty:
    q4_summary = q4_detail.groupby(
        ["Region", "Age_Group"], as_index=False
    )["Enrollment"].sum(min_count=1)
else:
    q4_summary = pd.DataFrame(
        columns=["Region", "Age_Group", "Enrollment"]
    )

q4_summary.to_csv(OUTPUT / "q4_age_region_enrollment.csv", index=False)


# Q5: Gender-wise literacy comparison
male_rural = find_column(lit.columns, "2011", "rural", "male")
female_rural = find_column(lit.columns, "2011", "rural", "female")
male_urban = find_column(lit.columns, "2011", "urban", "male")
female_urban = find_column(lit.columns, "2011", "urban", "female")

for col in [male_rural, female_rural, male_urban, female_urban]:
    lit[col] = pd.to_numeric(lit[col], errors="coerce")

male_average = pd.concat(
    [lit[male_rural], lit[male_urban]], axis=1
).mean(axis=1).mean()

female_average = pd.concat(
    [lit[female_rural], lit[female_urban]], axis=1
).mean(axis=1).mean()

comparison = pd.DataFrame({
    "Gender": ["Male", "Female"],
    "Average_Literacy_Rate": [male_average, female_average]
})

comparison.to_csv(
    OUTPUT / "q5_gender_literacy_summary.csv", index=False
)

plt.figure(figsize=(7, 5))
plt.bar(comparison["Gender"], comparison["Average_Literacy_Rate"])
plt.title("Gender-wise Literacy Comparison (2011)")
plt.xlabel("Gender")
plt.ylabel("Average literacy rate (%)")
plt.tight_layout()
plt.savefig(OUTPUT / "q5_gender_wise_literacy.png", dpi=300)
plt.close()


# Summary of outputs
pd.DataFrame({
    "Question": ["Q1", "Q2", "Q3", "Q4", "Q5"],
    "Output": [
        "q1_average_literacy.txt",
        "q2_gender_filtered.csv",
        "q3_missing_enrollment.csv",
        "q4_age_region_enrollment.csv",
        "q5_gender_wise_literacy.png"
    ]
}).to_csv(OUTPUT / "analysis_summary.csv", index=False)

print("Analysis completed. Check the output folder.")
