# Credit Risk & Loan Default Prediction

## Project overview
This is a beginner-friendly banking data science portfolio project that investigates loan default risk using synthetic data.

The project demonstrates:
- Python
- pandas
- NumPy
- Matplotlib
- scikit-learn
- Jupyter Notebook
- SQL
- Power BI

## Business problem
A bank needs to understand which loan applications have characteristics associated with default and how predictive analytics can support credit-risk decision making.

## Dataset
The dataset contains 5,000 **synthetic** loan applications. It is not real bank data.

Important columns:
- `credit_score`
- `annual_income`
- `debt_to_income`
- `loan_amount`
- `employment_status`
- `loan_purpose`
- `late_payments_12m`
- `existing_credit_accounts`
- `default`

## Project workflow
1. Load the data
2. Inspect the data
3. Clean missing and invalid values
4. Create useful features
5. Explore default patterns
6. Run SQL analysis
7. Train classification models
8. Compare model performance
9. Interpret the results from a banking perspective
10. Design a Power BI dashboard

## Models
- Logistic Regression
- Decision Tree
- Random Forest

## Evaluation
- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Average Precision
- Confusion matrix

## How to run

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the scripts from the project folder:

```bash
python src/cleaning.py
python src/eda.py
python src/model.py
```

Then open:

```text
notebooks/credit_risk_analysis.ipynb
```

## Important portfolio note
The dataset and model results are synthetic. They are intended to demonstrate data science skills and should not be presented as evidence about real banking customers or real bank performance.

## What I learned
This project demonstrates how a data scientist can move from a business problem to:
business understanding → data cleaning → exploratory analysis → feature engineering → modelling → evaluation → business interpretation.

## Next step
The next portfolio project can build on the same skills with customer churn prediction.


## Business Management Layer

This project combines **Business Management + Data Science**.

The business problem is treated as a credit-risk and decision-support problem. The project identifies risk patterns, defines relevant business KPIs, considers stakeholders, evaluates model trade-offs, and translates analytical results into management-oriented insights.

See:
- `BUSINESS_ANALYSIS.md` — business problem, objectives, stakeholders, KPIs, decision framework and recommendations
- `BUSINESS_DECISION_TABLE.md` — examples of translating technical outputs into business questions
- `STAKEHOLDER_REQUIREMENTS.md` — stakeholder needs and business requirements

This makes the project suitable for demonstrating both technical capability and business understanding.
