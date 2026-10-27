"""Data cleaning and feature engineering for the credit-risk project."""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "loan_applications.csv"
PROCESSED = ROOT / "data" / "processed" / "loan_applications_clean.csv"

def load_data(path=RAW):
    return pd.read_csv(path)

def clean_data(df):
    out = df.copy()
    numeric_cols = [
        "annual_income", "employment_length_years", "credit_score",
        "loan_amount", "loan_term_months", "interest_rate",
        "existing_loans", "previous_defaults", "debt_to_income_ratio"
    ]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
        out[col] = out[col].fillna(out[col].median())

    out["annual_income"] = out["annual_income"].clip(lower=0)
    out["loan_amount"] = out["loan_amount"].clip(lower=0)
    out["credit_score"] = out["credit_score"].clip(300, 850)
    out["debt_to_income_ratio"] = out["debt_to_income_ratio"].clip(0, 1)

    out["credit_score_band"] = pd.cut(
        out["credit_score"],
        bins=[0, 579, 669, 739, 850],
        labels=["Poor", "Fair", "Good", "Very Good"]
    )
    out["income_band"] = pd.qcut(
        out["annual_income"], q=4,
        labels=["Low", "Lower-Middle", "Upper-Middle", "High"],
        duplicates="drop"
    )
    out["loan_to_income_ratio"] = (
        out["loan_amount"] / out["annual_income"].replace(0, np.nan)
    ).fillna(0).round(4)

    return out

def main():
    df = clean_data(load_data())
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED, index=False)
    print(f"Saved {len(df):,} rows to {PROCESSED}")

if __name__ == "__main__":
    main()
