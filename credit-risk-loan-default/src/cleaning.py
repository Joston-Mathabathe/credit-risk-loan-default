import pandas as pd
import numpy as np

df = pd.read_csv("data/raw/loan_applications.csv")

numeric_columns = [
    "age", "annual_income", "credit_score", "debt_to_income",
    "loan_amount", "employment_tenure_years",
    "late_payments_12m", "existing_credit_accounts", "default"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

for column in ["annual_income", "credit_score", "debt_to_income", "loan_amount"]:
    df[column] = df[column].fillna(df[column].median())

df["credit_score"] = df["credit_score"].clip(300, 850)
df["debt_to_income"] = df["debt_to_income"].clip(0, 1)

df["credit_score_band"] = pd.cut(
    df["credit_score"],
    bins=[299, 579, 669, 739, 799, 850],
    labels=["Poor", "Fair", "Good", "Very Good", "Excellent"]
)

df["income_band"] = pd.qcut(
    df["annual_income"], 4,
    labels=["Low", "Lower-Middle", "Upper-Middle", "High"],
    duplicates="drop"
)

df["loan_to_income"] = df["loan_amount"] / df["annual_income"]

df.to_csv("data/processed/loan_applications_clean.csv", index=False)
print("Cleaned dataset saved.")
