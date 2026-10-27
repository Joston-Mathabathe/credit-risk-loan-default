"""Exploratory analysis and charts."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/loan_applications_clean.csv"
OUT = ROOT / "visualisations"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

summary = {
    "rows": len(df),
    "default_rate": df["default"].mean(),
    "average_loan": df["loan_amount"].mean(),
    "average_credit_score": df["credit_score"].mean()
}
print(summary)

fig, ax = plt.subplots(figsize=(7, 5))
sns.countplot(data=df, x="default", hue="default", legend=False, ax=ax)
ax.set_title("Loan Default Distribution")
ax.set_xlabel("Default (0 = No, 1 = Yes)")
ax.set_ylabel("Number of Loans")
fig.tight_layout()
fig.savefig(OUT / "default_distribution.png", dpi=160)
plt.close(fig)

default_by_score = df.groupby("credit_score_band", observed=False)["default"].mean().reset_index()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=default_by_score, x="credit_score_band", y="default", hue="credit_score_band", legend=False, ax=ax)
ax.set_title("Observed Default Rate by Credit Score Band")
ax.set_ylabel("Default rate")
ax.set_xlabel("Credit score band")
fig.tight_layout()
fig.savefig(OUT / "default_rate_credit_score.png", dpi=160)
plt.close(fig)

default_by_purpose = df.groupby("loan_purpose")["default"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 5))
default_by_purpose.plot(kind="bar", ax=ax)
ax.set_title("Observed Default Rate by Loan Purpose")
ax.set_ylabel("Default rate")
ax.set_xlabel("Loan purpose")
plt.xticks(rotation=35, ha="right")
fig.tight_layout()
fig.savefig(OUT / "default_rate_loan_purpose.png", dpi=160)
plt.close(fig)
