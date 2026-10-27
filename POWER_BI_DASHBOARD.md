# Power BI Dashboard Specification

> **Status:** this is a specification and DAX measure set. A built `.pbix` report is listed under future improvements in the README. Add the `.pbix` and a screenshot here once built.

## Dashboard: Credit Risk Portfolio

This document provides a specification for a Power BI dashboard that can be built from `data/processed/loan_applications_clean.csv`.

## Page 1 — Executive Overview

### KPI cards
- Total loans
- Total loan value
- Average loan amount
- Average credit score
- Observed default rate

### Visuals
- Default rate by credit score band
- Default rate by loan purpose
- Default rate by employment status
- Loan value by purpose

## Page 2 — Borrower Risk

Recommended visuals:
- Default rate by income band
- Default rate by DTI band
- Default rate by previous defaults
- Credit score distribution by default status

Suggested slicers:
- Employment status
- Loan purpose
- Home ownership
- Application channel

## Page 3 — Loan Portfolio

Recommended visuals:
- Loan amount distribution
- Average loan amount by purpose
- Loan term distribution
- Interest rate distribution
- Loan-to-income ratio distribution

## Page 4 — Model Performance

Use model outputs from `reports/model_comparison.csv`.

Recommended visuals:
- Model comparison table
- ROC curve
- Precision-recall curve
- Confusion matrix

## Page 5 - Risk Tiers and Policy

Use `reports/risk_tiers.csv` and `reports/policy_scenarios.csv`.

Recommended visuals:
- Predicted PD versus observed default rate by tier
- Share of loans versus share of credit losses by tier
- Policy comparison table (losses avoided, margin forgone, net benefit)
- Slicer for loss-given-default assumption (from `reports/policy_sensitivity.csv`)

## Dashboard principles

- Keep the dashboard focused on decision-support questions.
- Clearly distinguish observed historical default rates from model predictions.
- Avoid presenting the model as an automatic credit-approval system.
- Include a small note that the underlying data is synthetic.

## DAX measures

```DAX
Total Loans = COUNTROWS(loan_applications_clean)

Total Loan Value = SUM(loan_applications_clean[loan_amount])

Average Loan Amount = AVERAGE(loan_applications_clean[loan_amount])

Average Credit Score = AVERAGE(loan_applications_clean[credit_score])

Defaults = CALCULATE(COUNTROWS(loan_applications_clean), loan_applications_clean[default] = 1)

Default Rate = DIVIDE([Defaults], [Total Loans])

Default Rate vs Portfolio =
    [Default Rate] - CALCULATE([Default Rate], ALL(loan_applications_clean))
```

## Build steps

1. Run `python src/run_all.py` to generate `data/processed/loan_applications_clean.csv`.
2. In Power BI Desktop: Get Data > Text/CSV > load that file.
3. Set `credit_score_band` and `income_band` sort order (Poor, Fair, Good, Very Good; Low to High) with "Sort by column" helper columns.
4. Add the DAX measures above, then build the pages described earlier.
5. Add a footnote on every page: "Synthetic data. Not for real lending decisions."
6. Export screenshots to `visualisations/` and the report to the repo root as `credit_risk_dashboard.pbix`.
