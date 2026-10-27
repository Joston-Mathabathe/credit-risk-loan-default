"""Train, evaluate, cross-validate, calibrate and threshold-tune loan default models.

Outputs
-------
reports/   model_comparison.csv, classification_report.txt, confusion_matrix.csv,
           cross_validation.csv, logistic_odds_ratios.csv, sensitivity_no_interest_rate.csv,
           calibration.csv, threshold_analysis.csv, project_summary.json
visualisations/  roc_curve.png, precision_recall_curve.png, odds_ratios.png,
                 calibration_curve.png, threshold_cost_curve.png
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss,
    classification_report, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, RocCurveDisplay, PrecisionRecallDisplay,
)
from sklearn.model_selection import (
    StratifiedKFold, cross_val_predict, cross_validate, train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 42
# ASSUMPTION (illustrative, synthetic data): missing a defaulter costs 5x more than
# wrongly declining a good borrower. Sensitivity to this ratio is reported below.
MAIN_FN_COST = 5
COST_RATIOS = [1, 3, 5, 10]

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/loan_applications_clean.csv"
OUT = ROOT / "reports"
FIG = ROOT / "visualisations"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

df = pd.read_csv(DATA)
target = "default"
drop_cols = ["loan_id", "customer_id", target]
X = df.drop(columns=drop_cols)
y = df[target]


def split_columns(frame):
    numeric = frame.select_dtypes(include=[np.number]).columns.tolist()
    categorical = [c for c in frame.columns if c not in numeric]
    return numeric, categorical


def make_preprocessor(frame):
    numeric, categorical = split_columns(frame)
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                          ("scaler", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])


def make_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1500, class_weight="balanced", random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=20, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_leaf=10,
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    }


def make_pipe(model, frame=X):
    return Pipeline([("preprocessor", make_preprocessor(frame)), ("model", model)])


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE)

# ------------------------------------------------------------------ 1. Hold-out evaluation
results, fitted = [], {}
for name, model in make_models().items():
    pipe = make_pipe(model).fit(X_train, y_train)
    pred = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]
    results.append({
        "model": name,
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, proba),
        "average_precision": average_precision_score(y_test, proba),
    })
    fitted[name] = (pipe, pred, proba)

results_df = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
results_df.to_csv(OUT / "model_comparison.csv", index=False)

best_name = results_df.iloc[0]["model"]
best_pipe, best_pred, best_proba = fitted[best_name]

cm = confusion_matrix(y_test, best_pred)
pd.DataFrame(cm, index=["Actual Non-default", "Actual Default"],
             columns=["Predicted Non-default", "Predicted Default"]
             ).to_csv(OUT / "confusion_matrix.csv")
with open(OUT / "classification_report.txt", "w") as f:
    f.write(f"Selected model by ROC-AUC: {best_name}\n\n")
    f.write(classification_report(y_test, best_pred, zero_division=0))

for display, fname, title in [
    (RocCurveDisplay, "roc_curve.png", f"ROC Curve - {best_name}"),
    (PrecisionRecallDisplay, "precision_recall_curve.png", f"Precision-Recall Curve - {best_name}"),
]:
    fig, ax = plt.subplots(figsize=(7, 5))
    display.from_predictions(y_test, best_proba, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(FIG / fname, dpi=160)
    plt.close(fig)

# ------------------------------------------------------------------ 2. Cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scoring = {"roc_auc": "roc_auc", "average_precision": "average_precision",
           "precision": "precision", "recall": "recall"}
cv_rows = []
for name, model in make_models().items():
    cv = cross_validate(make_pipe(model), X, y, cv=skf, scoring=scoring, n_jobs=1)
    row = {"model": name}
    for metric in scoring:
        scores = cv[f"test_{metric}"]
        row[f"{metric}_mean"] = scores.mean()
        row[f"{metric}_std"] = scores.std()
    cv_rows.append(row)
cv_df = pd.DataFrame(cv_rows).sort_values("roc_auc_mean", ascending=False)
cv_df.to_csv(OUT / "cross_validation.csv", index=False)

# ------------------------------------------------------------------ 3. Drivers of default (odds ratios)
lr_pipe = fitted["Logistic Regression"][0]
names = lr_pipe.named_steps["preprocessor"].get_feature_names_out()
names = [n.split("__", 1)[1] for n in names]  # strip "num__" / "cat__" prefixes
coefs = lr_pipe.named_steps["model"].coef_[0]
odds = pd.DataFrame({"feature": names, "coefficient": coefs, "odds_ratio": np.exp(coefs)})
odds["abs_coef"] = odds["coefficient"].abs()
odds = odds.sort_values("abs_coef", ascending=False).drop(columns="abs_coef")
odds.to_csv(OUT / "logistic_odds_ratios.csv", index=False)

top = odds.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(top["feature"], top["odds_ratio"],
        color=["#c0392b" if v > 1 else "#2e86c1" for v in top["odds_ratio"]])
ax.axvline(1, color="black", linewidth=0.8)
ax.set_xlabel("Odds ratio (per 1 SD for numeric features; vs other levels for categories)")
ax.set_title("Top 10 drivers of default - Logistic Regression")
fig.tight_layout()
fig.savefig(FIG / "odds_ratios.png", dpi=160)
plt.close(fig)

# ------------------------------------------------------------------ 4. Sensitivity: drop interest_rate
# Interest rate is usually set AFTER risk assessment, so it may not be available (or may be
# partly a consequence of risk) at application time. Check the model does not depend on it.
X_nr = X.drop(columns=["interest_rate"])
Xtr_nr, Xte_nr, ytr_nr, yte_nr = train_test_split(
    X_nr, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE)
nr_pipe = make_pipe(make_models()["Logistic Regression"], X_nr).fit(Xtr_nr, ytr_nr)
nr_proba = nr_pipe.predict_proba(Xte_nr)[:, 1]
pd.DataFrame([
    {"variant": "All features", "roc_auc": roc_auc_score(y_test, best_proba)},
    {"variant": "Without interest_rate", "roc_auc": roc_auc_score(yte_nr, nr_proba)},
]).to_csv(OUT / "sensitivity_no_interest_rate.csv", index=False)

# ------------------------------------------------------------------ 5. Probability calibration
# class_weight="balanced" inflates predicted probabilities, so recalibrate before using them
# as probabilities of default (PD).
cal_model = CalibratedClassifierCV(
    make_pipe(make_models()["Logistic Regression"]), method="sigmoid", cv=5).fit(X_train, y_train)
cal_proba = cal_model.predict_proba(X_test)[:, 1]
raw_proba = fitted["Logistic Regression"][2]
pd.DataFrame([
    {"variant": "Logistic Regression (balanced, uncalibrated)",
     "brier_score": brier_score_loss(y_test, raw_proba),
     "mean_predicted_pd": raw_proba.mean(), "observed_default_rate": y_test.mean()},
    {"variant": "Logistic Regression (sigmoid-calibrated)",
     "brier_score": brier_score_loss(y_test, cal_proba),
     "mean_predicted_pd": cal_proba.mean(), "observed_default_rate": y_test.mean()},
]).to_csv(OUT / "calibration.csv", index=False)

fig, ax = plt.subplots(figsize=(6.5, 6))
for label, p in [("Uncalibrated (balanced)", raw_proba), ("Calibrated", cal_proba)]:
    frac, mean_pred = calibration_curve(y_test, p, n_bins=10, strategy="quantile")
    ax.plot(mean_pred, frac, marker="o", label=label)
ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
ax.set_xlabel("Mean predicted probability of default")
ax.set_ylabel("Observed default rate")
ax.set_title("Calibration curve - Logistic Regression")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "calibration_curve.png", dpi=160)
plt.close(fig)

# ------------------------------------------------------------------ 6. Cost-based threshold
# Thresholds are chosen on out-of-fold predictions from the TRAINING set only, then applied
# once to the untouched test set.
oof = cross_val_predict(
    CalibratedClassifierCV(make_pipe(make_models()["Logistic Regression"]), method="sigmoid", cv=5),
    X_train, y_train, cv=skf, method="predict_proba")[:, 1]
y_tr, y_te = y_train.to_numpy(), y_test.to_numpy()
grid = np.round(np.arange(0.02, 0.91, 0.01), 2)


def confusion_counts(y_true, proba, t):
    pred = proba >= t
    fp = int(((pred == 1) & (y_true == 0)).sum())
    fn = int(((pred == 0) & (y_true == 1)).sum())
    tp = int(((pred == 1) & (y_true == 1)).sum())
    return tp, fp, fn


def evaluate(y_true, proba, t, ratio):
    tp, fp, fn = confusion_counts(y_true, proba, t)
    return {"threshold": t, "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn), "false_positives": fp, "false_negatives": fn,
            "total_cost_units": fp + ratio * fn}


rows = []
base_tp, base_fp, base_fn = confusion_counts(y_te, raw_proba, 0.5)
curve_main = None
for ratio in COST_RATIOS:
    costs = np.array([(lambda c: c[1] + ratio * c[2])(confusion_counts(y_tr, oof, t)) for t in grid])
    t_best = float(grid[int(np.argmin(costs))])
    row = {"fn_to_fp_cost_ratio": ratio, **evaluate(y_te, cal_proba, t_best, ratio),
           "baseline_cost_at_0.5": base_fp + ratio * base_fn}
    rows.append(row)
    if ratio == MAIN_FN_COST:
        curve_main = costs
thr_df = pd.DataFrame(rows)
thr_df["cost_reduction_pct"] = (1 - thr_df["total_cost_units"] / thr_df["baseline_cost_at_0.5"]) * 100
thr_df.to_csv(OUT / "threshold_analysis.csv", index=False)

fig, ax = plt.subplots(figsize=(7.5, 5))
ax.plot(grid, curve_main)
best_t = float(thr_df.loc[thr_df.fn_to_fp_cost_ratio == MAIN_FN_COST, "threshold"].iloc[0])
ax.axvline(best_t, color="red", linestyle="--", label=f"Chosen threshold = {best_t:.2f}")
ax.set_xlabel("Decision threshold on predicted probability of default")
ax.set_ylabel(f"Total cost on training folds (FP + {MAIN_FN_COST} x FN)")
ax.set_title("Cost-based threshold selection")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "threshold_cost_curve.png", dpi=160)
plt.close(fig)

# ------------------------------------------------------------------ Summary
summary = {
    "dataset_rows": int(len(df)),
    "default_rate": round(float(y.mean()), 4),
    "best_model_by_roc_auc": best_name,
    "best_model_roc_auc": round(float(results_df.iloc[0]["roc_auc"]), 4),
    "cv_roc_auc_mean_std_best_model": [
        round(float(cv_df.loc[cv_df.model == best_name, "roc_auc_mean"].iloc[0]), 4),
        round(float(cv_df.loc[cv_df.model == best_name, "roc_auc_std"].iloc[0]), 4)],
    "calibration_brier_uncalibrated_vs_calibrated": [
        round(float(brier_score_loss(y_test, raw_proba)), 4),
        round(float(brier_score_loss(y_test, cal_proba)), 4)],
    "threshold_by_fn_to_fp_cost_ratio": {
        str(int(r.fn_to_fp_cost_ratio)): float(r.threshold) for r in thr_df.itertuples()},
}
with open(OUT / "project_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

pd.set_option("display.width", 200)
print("\nHold-out results\n", results_df.round(3).to_string(index=False))
print("\n5-fold CV\n", cv_df.round(3).to_string(index=False))
print("\nTop drivers\n", odds.head(10).round(3).to_string(index=False))
print("\nCalibration\n", pd.read_csv(OUT / "calibration.csv").round(3).to_string(index=False))
print("\nThreshold analysis\n", thr_df.round(3).to_string(index=False))
print("\n", json.dumps(summary, indent=2))
