"""Turn calibrated default probabilities into a risk-based credit policy and a financial case.

Method
------
1. Get out-of-fold calibrated probabilities of default (PD) for all 5,000 loans, so no loan
   is scored by a model that saw its own outcome.
2. Group loans into four risk tiers by PD.
3. Back-test two simple decline policies against the historical outcomes.

ASSUMPTIONS (illustrative: the data is synthetic; currency units are labelled "R" for readability)
- Loss given default (LGD): 45% of the loan amount.
- Net margin on a performing loan: 4% a year of the average outstanding balance, taken as
  50% of the principal, over the loan term. (Margin is after funding and operating cost.)
Both are varied in reports/policy_sensitivity.csv.

Outputs: reports/risk_tiers.csv, policy_scenarios.csv, policy_sensitivity.csv,
         visualisations/risk_tiers.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42
LGD = 0.45
NET_MARGIN = 0.04
AVG_BALANCE_SHARE = 0.5
TIER_CUTS = [0.10, 0.25, 0.40]
TIER_LABELS = ["Low", "Medium", "High", "Very High"]
TIER_ACTION = {
    "Low": "Approve",
    "Medium": "Approve with standard conditions / risk-based pricing",
    "High": "Manual underwriting review",
    "Very High": "Decline (or require security / guarantor)",
}

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/loan_applications_clean.csv"
OUT = ROOT / "reports"
FIG = ROOT / "visualisations"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
y = df["default"]
X = df.drop(columns=["loan_id", "customer_id", "default"])
numeric = X.select_dtypes(include=[np.number]).columns.tolist()
categorical = [c for c in X.columns if c not in numeric]

pipe = Pipeline([
    ("preprocessor", ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                          ("scaler", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])),
    ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=RANDOM_STATE)),
])
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
df["pd"] = cross_val_predict(
    CalibratedClassifierCV(pipe, method="sigmoid", cv=5), X, y, cv=skf, method="predict_proba")[:, 1]
df["tier"] = pd.cut(df["pd"], [0] + TIER_CUTS + [1.01], labels=TIER_LABELS, right=False)


def economics(frame, lgd=LGD, margin=NET_MARGIN):
    loss = lgd * frame["loan_amount"] * frame["default"]
    revenue = margin * AVG_BALANCE_SHARE * frame["loan_amount"] * frame["loan_term_months"] / 12
    return loss, revenue * (1 - frame["default"])  # margin only counted on performing loans


# ------------------------------------------------------------------ risk tiers
loss_all, _ = economics(df)
df["realised_loss"] = loss_all
df["expected_loss"] = LGD * df["pd"] * df["loan_amount"]

tiers = df.groupby("tier", observed=False).agg(
    loans=("default", "size"),
    loan_value_Rm=("loan_amount", lambda s: s.sum() / 1e6),
    predicted_pd=("pd", "mean"),
    observed_default_rate=("default", "mean"),
    expected_loss_Rm=("expected_loss", lambda s: s.sum() / 1e6),
    realised_loss_Rm=("realised_loss", lambda s: s.sum() / 1e6),
).reset_index()
tiers["share_of_loans_pct"] = tiers["loans"] / tiers["loans"].sum() * 100
tiers["share_of_loan_value_pct"] = tiers["loan_value_Rm"] / tiers["loan_value_Rm"].sum() * 100
tiers["share_of_realised_loss_pct"] = tiers["realised_loss_Rm"] / tiers["realised_loss_Rm"].sum() * 100
tiers["recommended_action"] = tiers["tier"].map(TIER_ACTION)
tiers.to_csv(OUT / "risk_tiers.csv", index=False)

# ------------------------------------------------------------------ policy back-test
def backtest(declined_mask, lgd=LGD, margin=NET_MARGIN):
    d = df[declined_mask]
    loss, revenue = economics(d, lgd, margin)
    return {
        "loans_declined": int(len(d)),
        "share_of_loans_declined_pct": len(d) / len(df) * 100,
        "defaults_avoided": int(d["default"].sum()),
        "good_loans_declined": int((d["default"] == 0).sum()),
        "losses_avoided_Rm": loss.sum() / 1e6,
        "margin_forgone_Rm": revenue.sum() / 1e6,
        "net_benefit_Rm": (loss.sum() - revenue.sum()) / 1e6,
    }


policies = {
    "A: decline Very High tier (PD >= 40%)": df["tier"] == "Very High",
    "B: decline High and Very High tiers (PD >= 25%)": df["tier"].isin(["High", "Very High"]),
}
scen = pd.DataFrame([{"policy": k, **backtest(v)} for k, v in policies.items()])
scen["portfolio_realised_loss_Rm"] = df["realised_loss"].sum() / 1e6
scen.to_csv(OUT / "policy_scenarios.csv", index=False)

rows = []
for name, mask in policies.items():
    for lgd in (0.30, 0.45, 0.60):
        for margin in (0.02, 0.04, 0.06):
            rows.append({"policy": name, "lgd": lgd, "net_margin": margin,
                         "net_benefit_Rm": backtest(mask, lgd, margin)["net_benefit_Rm"]})
sens = pd.DataFrame(rows)
sens.to_csv(OUT / "policy_sensitivity.csv", index=False)

# ------------------------------------------------------------------ chart
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
x = np.arange(len(tiers))
w = 0.38
axes[0].bar(x - w / 2, tiers["predicted_pd"] * 100, w, label="Predicted PD")
axes[0].bar(x + w / 2, tiers["observed_default_rate"] * 100, w, label="Observed default rate")
axes[0].set_xticks(x, tiers["tier"])
axes[0].set_ylabel("%")
axes[0].set_title("Risk tiers: predicted vs observed default rate")
axes[0].legend()
axes[1].bar(x - w / 2, tiers["share_of_loans_pct"], w, label="Share of loans")
axes[1].bar(x + w / 2, tiers["share_of_realised_loss_pct"], w, label="Share of credit losses")
axes[1].set_xticks(x, tiers["tier"])
axes[1].set_ylabel("%")
axes[1].set_title("Where the losses sit")
axes[1].legend()
fig.tight_layout()
fig.savefig(FIG / "risk_tiers.png", dpi=160)
plt.close(fig)

pd.set_option("display.width", 220)
print("\nRisk tiers\n", tiers.round(2).drop(columns="recommended_action").to_string(index=False))
print("\nPolicy scenarios\n", scen.round(2).to_string(index=False))
print("\nSensitivity (net benefit R m)\n", sens.pivot_table(
    index=["policy", "lgd"], columns="net_margin", values="net_benefit_Rm").round(1).to_string())
