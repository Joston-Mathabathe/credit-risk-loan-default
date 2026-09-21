# Interview Preparation

## 60-second explanation
"I built a credit-risk project using synthetic loan application data. I cleaned the data, explored default patterns using variables such as credit score and debt-to-income ratio, created features such as credit-score bands and loan-to-income ratio, and then compared Logistic Regression, Decision Tree and Random Forest models. I evaluated the models using precision, recall, F1-score, ROC-AUC and Average Precision. The goal was to demonstrate how data science can support credit-risk analysis. Because the data is synthetic, I would not claim that the results represent a real bank."

## Why Logistic Regression?
It is a simple and interpretable classification baseline and can provide estimated probabilities.

## Why Decision Tree?
A decision tree can capture nonlinear relationships and is relatively easy to explain.

## Why Random Forest?
It combines many decision trees and can capture more complex patterns.

## Why not use accuracy only?
In credit-risk classification, missing a default can have different consequences from incorrectly flagging a non-default. Precision and recall therefore provide additional information.

## What is overfitting?
Overfitting occurs when a model learns patterns that work well on training data but do not generalise well to unseen data.

## What is train/test split?
The training data is used to fit the model while the test data is held back to evaluate performance on unseen examples.

## What would you do with real bank data?
I would first understand the business problem and data definitions, check data quality, prevent leakage, establish a baseline, train and validate the model, assess fairness and explainability, and work with stakeholders before deployment.


## Business Management Questions

### Q: What business problem were you solving?
**Answer:** I treated loan default as a credit-risk and decision-support problem. The aim was to identify patterns associated with default and use predictive analytics to support more informed risk assessment and portfolio monitoring.

### Q: How does your Business Management background add value?
**Answer:** My Business Management background helps me understand the business purpose behind the analysis. I can identify stakeholders, define useful KPIs, consider operational and financial implications, and translate technical findings into information that managers can use.

### Q: Who would use this analysis in a bank?
**Answer:** Credit and risk teams could use it to understand risk patterns, lending teams could use it as decision support, management could monitor portfolio KPIs, and data teams could use it to develop and monitor analytical solutions.

### Q: Why is accuracy not enough for a credit-risk model?
**Answer:** Accuracy can hide the type of errors the model is making. In credit risk, missing an actual default and incorrectly flagging a customer have different business consequences. That is why I also considered precision, recall, F1-score and ROC-AUC.

### Q: Would you allow the model to automatically approve or reject a loan?
**Answer:** No. In this portfolio project, the model is a decision-support tool. A real banking process would require credit policy, affordability assessment, governance, regulatory requirements, data-quality controls and human oversight.

### Q: What is the most important lesson from the project?
**Answer:** A good data science solution must solve a business problem. Building the model is only one part of the work. I also need to understand the stakeholders, define meaningful KPIs, interpret the results and communicate the implications clearly.
