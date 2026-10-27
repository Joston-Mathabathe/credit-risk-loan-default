# Model Card: Credit Default Classification

## Intended use
Portfolio and educational demonstration of an end-to-end binary classification workflow for credit-risk analytics.

## Not intended for
Real-world automated lending decisions, credit scoring, customer eligibility decisions or production deployment.

## Data
5,000 synthetic loan applications generated for this repository (17.6% default rate). No real customer records are included.

## Models
- Logistic Regression (selected): `class_weight="balanced"`
- Decision Tree: `max_depth=6`, `min_samples_leaf=20`
- Random Forest: 300 trees, `max_depth=10`, `min_samples_leaf=10`

Preprocessing: median imputation and standardisation for numeric features; most-frequent imputation and one-hot encoding for categorical features. Train/test split 80/20, stratified, seed 42.

## Evaluation
- Hold-out (20%): accuracy, precision, recall, F1, ROC-AUC, average precision, confusion matrix.
- 5-fold stratified cross-validation: ROC-AUC 0.794 ± 0.022 for the selected model (hold-out ROC-AUC 0.831).
- Probability calibration: Brier score 0.168 (uncalibrated) to 0.111 (sigmoid-calibrated).
- Sensitivity: dropping `interest_rate` changes hold-out ROC-AUC from 0.831 to 0.825.
- Decision threshold: chosen from an illustrative cost ratio on out-of-fold training predictions; see `reports/threshold_analysis.csv`.

## Business use (illustrative)
Calibrated probabilities are grouped into four risk tiers (Low, Medium, High, Very High) with recommended actions. A back-test on historical outcomes, using assumed loss given default (45%) and margin (4%), is in `reports/policy_scenarios.csv`. These figures illustrate method, not real bank economics.

## Limitations
- Synthetic data does not represent any specific bank, population, geography or lending book; relationships are simulated.
- Single fixed hyperparameter configuration; no tuning.
- Cost ratios used for threshold selection are assumptions, not real loss figures.
- `credit_score` and `interest_rate` are correlated, so individual coefficients are not clean causal effects.
- The policy back-test ignores reject inference (outcomes exist only for approved loans), recoveries beyond the assumed loss rate, and customer lifetime value.
- No fairness or subgroup analysis has been performed.

## Before any real use
Representative data, independent validation, fairness assessment, explainability, monitoring, privacy controls and regulatory review would all be required.
