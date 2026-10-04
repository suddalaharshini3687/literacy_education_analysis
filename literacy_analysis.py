import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Reading the datasets
literacy = pd.read_excel("data/Table29.6-States-1.xls")
enrollment = pd.read_csv("data/UDISE_2021_22_Table_5.17_2.csv")


# Displaying the datasets
print("Literacy Data")
print(literacy.head())

print("\nEnrollment Data")
print(enrollment.head())


# Q1. Calculate average literacy rate

# Rural and Urban Person columns are used because
# they give the overall literacy rate without separating male and female.
literacy["Average"] = literacy[
    ["2011 - Rural - Person", "2011 - Urban - Person"]
].mean(axis=1)

avg_literacy = literacy["Average"].mean()

print("\nQ1: Average Literacy Rate =", round(avg_literacy, 2), "%")


# Q2. Gender-wise literacy rate

# Male Rural and Male Urban are selected to calculate
# the average literacy rate of males.
male = literacy[
    ["All India/State/Union Territory",
     "2011 - Rural - Male",
     "2011 - Urban - Male"]
]

# Female Rural and Female Urban are selected to calculate
# the average literacy rate of females.
female = literacy[
    ["All India/State/Union Territory",
     "2011 - Rural - Female",
     "2011 - Urban - Female"]
]


male_avg = male[
    ["2011 - Rural - Male", "2011 - Urban - Male"]
].mean().mean()

female_avg = female[
    ["2011 - Rural - Female", "2011 - Urban - Female"]
].mean().mean()

print("\nQ2: Gender-wise Literacy Rate")
print("Male =", round(male_avg, 2), "%")
print("Female =", round(female_avg, 2), "%")


# Q3. Missing values and median

print("\nQ3: Missing Enrollment Values and Median")

# isnull() is used to find empty or missing values
# in the enrollment dataset.
missing = enrollment.isnull().sum().sum()

print("Number of missing values =", missing)

if missing > 0:
    print("Missing values are present in the dataset.")
else:
    print("There are no missing values.")


# Numerical columns are selected because median
# can be calculated only on numerical enrollment data.
numeric_data = enrollment.select_dtypes(include=np.number)

median_enrollment = numeric_data.median().median()

print("Median Enrollment =", round(median_enrollment, 2))


# Q4. Age-wise enrollment

print("\nQ4: Age-wise Enrollment")

# These attributes are selected because they represent
# different age groups of students and help us compare
# enrollment across age categories.
age_columns = [
    "Enrolment of Age Group < 6 years - All - Total",
    "Enrolment of Age Group 6-10 years - All - Total",
    "Enrolment of Age Group 11-13 Years - All - Total",
    "Enrolment of Age Group 14-15 Years - All - Total",
    "Enrolment of Age Group 16-17 years - All - Total",
    "Enrolment of Age Group >17 years - All - Total"
]

for column in age_columns:

    # Convert values into numbers and ignore invalid values.
    total = pd.to_numeric(
        enrollment[column],
        errors="coerce"
    ).sum()

    print(column, "=", total)


# Q5. Gender-wise literacy graph

# Male and Female are used as categories
# and their average literacy rates are used as values.
gender = ["Male", "Female"]
values = [male_avg, female_avg]

plt.figure(figsize=(7, 5))

plt.bar(gender, values)

plt.title("Gender-wise Literacy Comparison")
plt.xlabel("Gender")
plt.ylabel("Average Literacy Rate (%)")

# Literacy rate cannot normally exceed 100%.
plt.ylim(0, 100)

plt.savefig("gender_literacy_comparison.png")

plt.show()


# Seaborn graph

# Seaborn is used to create a simple statistical bar graph.
plt.figure(figsize=(7, 5))

sns.barplot(x=gender, y=values)

plt.title("Male vs Female Literacy Rate")
plt.xlabel("Gender")
plt.ylabel("Average Literacy Rate (%)")

plt.ylim(0, 100)

plt.savefig("gender_literacy_seaborn.png")

plt.show()


# NumPy analysis

# NumPy array is used for numerical calculations.
literacy_values = np.array(values)

print("\nNumPy Analysis")

print(
    "Highest Gender Literacy Rate =",
    round(np.max(literacy_values), 2),
    "%"
)

print(
    "Lowest Gender Literacy Rate =",
    round(np.min(literacy_values), 2),
    "%"
)

print("\nAnalysis completed successfully.")
