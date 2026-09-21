import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, RocCurveDisplay, PrecisionRecallDisplay
)

df = pd.read_csv("data/processed/loan_applications_clean.csv")

X = df.drop(columns=["loan_id", "default"])
y = df["default"]

categorical_columns = ["employment_status", "loan_purpose", "credit_score_band", "income_band"]
numeric_columns = [
    "age", "annual_income", "credit_score", "debt_to_income",
    "loan_amount", "employment_tenure_years",
    "late_payments_12m", "existing_credit_accounts", "loan_to_income"
]

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_columns),
    ("categorical", categorical_pipeline, categorical_columns)
])

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(
        max_depth=6, min_samples_leaf=20,
        class_weight="balanced", random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=10, min_samples_leaf=10,
        class_weight="balanced", random_state=42
    )
}

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

results = []
trained_models = {}

for name, model in models.items():
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    results.append({
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "average_precision": average_precision_score(y_test, probabilities)
    })

    trained_models[name] = pipeline

results_df = pd.DataFrame(results)
results_df.to_csv("reports/model_comparison.csv", index=False)

best_model_name = results_df.sort_values("roc_auc", ascending=False).iloc[0]["model"]
best_model = trained_models[best_model_name]

predictions = best_model.predict(X_test)
probabilities = best_model.predict_proba(X_test)[:, 1]

pd.DataFrame(
    confusion_matrix(y_test, predictions),
    index=["Actual_No_Default", "Actual_Default"],
    columns=["Predicted_No_Default", "Predicted_Default"]
).to_csv("reports/confusion_matrix.csv")

with open("reports/classification_report.txt", "w") as file:
    file.write(classification_report(y_test, predictions, digits=4))

# ROC curve
RocCurveDisplay.from_predictions(y_test, probabilities)
plt.title("ROC Curve - Best Model")
plt.tight_layout()
plt.savefig("visualisations/roc_curve.png", dpi=150)
plt.close()

# Precision-recall curve
PrecisionRecallDisplay.from_predictions(y_test, probabilities)
plt.title("Precision-Recall Curve - Best Model")
plt.tight_layout()
plt.savefig("visualisations/precision_recall_curve.png", dpi=150)
plt.close()

print(results_df.round(4))
print("\nBest model by ROC-AUC:", best_model_name)
