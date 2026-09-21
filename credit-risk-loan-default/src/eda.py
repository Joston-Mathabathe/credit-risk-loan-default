import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/loan_applications_clean.csv")

# Default distribution
df["default"].value_counts().sort_index().plot(kind="bar")
plt.title("Loan Default Distribution")
plt.xlabel("Default (0 = No, 1 = Yes)")
plt.ylabel("Number of Applications")
plt.tight_layout()
plt.savefig("visualisations/default_distribution.png", dpi=150)
plt.close()

# Default rate by credit score band
rate = df.groupby("credit_score_band", observed=True)["default"].mean()
rate.plot(kind="bar")
plt.title("Default Rate by Credit Score Band")
plt.xlabel("Credit Score Band")
plt.ylabel("Default Rate")
plt.tight_layout()
plt.savefig("visualisations/default_rate_credit_score.png", dpi=150)
plt.close()

# Default rate by loan purpose
rate = df.groupby("loan_purpose")["default"].mean().sort_values(ascending=False)
rate.plot(kind="bar")
plt.title("Default Rate by Loan Purpose")
plt.xlabel("Loan Purpose")
plt.ylabel("Default Rate")
plt.tight_layout()
plt.savefig("visualisations/default_rate_loan_purpose.png", dpi=150)
plt.close()

# Default rate by DTI band
df["dti_band"] = pd.cut(
    df["debt_to_income"],
    bins=[-0.01,.20,.40,.60,.80,1],
    labels=["0-20%","20-40%","40-60%","60-80%","80-100%"]
)
rate = df.groupby("dti_band", observed=True)["default"].mean()
rate.plot(kind="bar")
plt.title("Default Rate by Debt-to-Income Band")
plt.xlabel("Debt-to-Income Band")
plt.ylabel("Default Rate")
plt.tight_layout()
plt.savefig("visualisations/default_rate_dti.png", dpi=150)
plt.close()

print("EDA visualisations saved.")
