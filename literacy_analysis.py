import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================
# EDAV PROJECT
# Analysis of Literacy Rates and Educational Enrollments
# by State and Gender
# ============================================================

# Create output folder
os.makedirs("output", exist_ok=True)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

literacy_file = "Table29.6-States(1).xls"
enrollment_file = "UDISE_2021_22_Table_5.17_2 (1).csv"

literacy = pd.read_excel(literacy_file)
enrollment = pd.read_csv(enrollment_file)

print("\n================ DATASET INFORMATION ================\n")

print("Literacy dataset shape:", literacy.shape)
print("Enrollment dataset shape:", enrollment.shape)

print("\nLiteracy columns:")
print(literacy.columns.tolist())

print("\nEnrollment columns:")
print(enrollment.columns.tolist())


# ------------------------------------------------------------
# Q1: CALCULATE AVERAGE LITERACY RATE
# ------------------------------------------------------------

print("\n================ Q1: AVERAGE LITERACY RATE ================\n")

# 2011 rural and urban literacy rates
rural_person = "2011 - Rural - Person"
urban_person = "2011 - Urban - Persons"

if rural_person in literacy.columns and urban_person in literacy.columns:

    literacy["2011_Average_Literacy"] = (
        literacy[rural_person] + literacy[urban_person]
    ) / 2

    average_literacy = literacy["2011_Average_Literacy"].mean()

    print("Average 2011 literacy rate:",
          round(average_literacy, 2), "%")

    print("\nState-wise average literacy:")
    print(
        literacy[
            ["All India/State/Union Territory",
             "2011_Average_Literacy"]
        ].to_string(index=False)
    )

else:
    print("Required literacy columns were not found.")


# ------------------------------------------------------------
# Q2: FILTER DATA BY GENDER
# ------------------------------------------------------------

print("\n================ Q2: GENDER-WISE ANALYSIS ================\n")

male_columns = [
    col for col in literacy.columns
    if "2011" in str(col) and "Male" in str(col)
]

female_columns = [
    col for col in literacy.columns
    if "2011" in str(col) and "Female" in str(col)
]

print("Male literacy columns:", male_columns)
print("Female literacy columns:", female_columns)

if male_columns and female_columns:

    literacy["Male_Average"] = literacy[male_columns].mean(axis=1)
    literacy["Female_Average"] = literacy[female_columns].mean(axis=1)

    print("\nAverage Male Literacy:",
          round(literacy["Male_Average"].mean(), 2), "%")

    print("Average Female Literacy:",
          round(literacy["Female_Average"].mean(), 2), "%")

else:
    print("Gender columns could not be identified.")


# ------------------------------------------------------------
# Q3: HANDLE MISSING ENROLLMENT VALUES
# ------------------------------------------------------------

print("\n================ Q3: MISSING ENROLLMENT VALUES ================\n")

missing_before = enrollment.isnull().sum()

print("Missing values before handling:")
print(missing_before)

total_missing = enrollment.isnull().sum().sum()

print("\nTotal missing enrollment values:",
      total_missing)

# Handle numeric missing values using column median
numeric_columns = enrollment.select_dtypes(
    include="number"
).columns

for column in numeric_columns:
    enrollment[column] = enrollment[column].fillna(
        enrollment[column].median()
    )

print("\nMissing values after handling:")
print(enrollment[numeric_columns].isnull().sum())

print("\nMissing enrollment values have been handled using median imputation for numeric columns.")


# ------------------------------------------------------------
# Q4: GROUP LITERACY / ENROLLMENT STATISTICS BY AGE
#     AND REGION
# ------------------------------------------------------------

print("\n================ Q4: AGE AND REGION ANALYSIS ================\n")

# Display columns so that age-related variables can be identified
print("Age-related enrollment columns:")

age_columns = []

for column in enrollment.columns:
    text = str(column).lower()

    if (
        "<6" in text
        or "6-10" in text
        or "6 – 10" in text
        or "11-13" in text
        or "11 – 13" in text
        or "14-15" in text
        or "14 – 15" in text
        or "16-17" in text
        or "16 – 17" in text
        or ">17" in text
    ):
        age_columns.append(column)

print(age_columns)

# Try to identify state column
state_column = None

for column in enrollment.columns:
    text = str(column).lower()

    if (
        "state" in text
        or "union territory" in text
        or "state/ut" in text
    ):
        state_column = column
        break

print("\nState column:", state_column)

# Region mapping for Indian states and UTs
region_map = {
    "Andhra Pradesh": "South",
    "Telangana": "South",
    "Karnataka": "South",
    "Kerala": "South",
    "Tamil Nadu": "South",
    "Goa": "West",
    "Maharashtra": "West",
    "Gujarat": "West",
    "Rajasthan": "West",
    "Madhya Pradesh": "Central",
    "Chhattisgarh": "Central",
    "Uttar Pradesh": "North",
    "Uttarakhand": "North",
    "Himachal Pradesh": "North",
    "Punjab": "North",
    "Haryana": "North",
    "Delhi": "North",
    "Jammu and Kashmir": "North",
    "Ladakh": "North",
    "Bihar": "East",
    "Jharkhand": "East",
    "Odisha": "East",
    "West Bengal": "East",
    "Assam": "Northeast",
    "Arunachal Pradesh": "Northeast",
    "Manipur": "Northeast",
    "Meghalaya": "Northeast",
    "Mizoram": "Northeast",
    "Nagaland": "Northeast",
    "Tripura": "Northeast",
    "Sikkim": "Northeast"
}

if state_column is not None:

    enrollment["Region"] = enrollment[state_column].astype(str).map(
        region_map
    )

    print("\nEnrollment grouped by region:")

    numeric_columns = enrollment.select_dtypes(
        include="number"
    ).columns

    region_summary = enrollment.groupby("Region")[
        list(numeric_columns)
    ].mean()

    print(region_summary)

    region_summary.to_csv(
        "output/region_enrollment_summary.csv"
    )

else:
    print(
        "State column was not automatically identified."
    )


# ------------------------------------------------------------
# Q5: PLOT GENDER-WISE LITERACY COMPARISON
# ------------------------------------------------------------

print("\n================ Q5: GENDER-WISE LITERACY GRAPH ================\n")

if "Male_Average" in literacy.columns and "Female_Average" in literacy.columns:

    gender_data = pd.DataFrame({
        "Gender": ["Male", "Female"],
        "Average Literacy Rate": [
            literacy["Male_Average"].mean(),
            literacy["Female_Average"].mean()
        ]
    })

    print(gender_data)

    plt.figure(figsize=(8, 6))

    plt.bar(
        gender_data["Gender"],
        gender_data["Average Literacy Rate"]
    )

    plt.title("Gender-wise Literacy Comparison - 2011")
    plt.xlabel("Gender")
    plt.ylabel("Average Literacy Rate (%)")

    plt.tight_layout()

    plt.savefig(
        "output/gender_literacy_comparison.png",
        dpi=300
    )

    plt.close()

    print(
        "\nGraph saved as: "
        "output/gender_literacy_comparison.png"
    )


# ------------------------------------------------------------
# SAVE LITERACY ANALYSIS
# ------------------------------------------------------------

literacy.to_csv(
    "output/literacy_analysis_results.csv",
    index=False
)

print("\n============================================================")
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("============================================================")

print("\nGenerated output files:")
print("- output/literacy_analysis_results.csv")
print("- output/region_enrollment_summary.csv")
print("- output/gender_literacy_comparison.png")
