# Business Analysis & Decision Framework

## 1. Business Problem

Loan default creates financial and operational risk for a lending institution. The business needs to assess applicants consistently and identify factors associated with higher default risk.

This project treats credit risk as a **business decision-support problem**, not only a machine-learning problem.

The analysis asks:

- Which applicant characteristics are associated with loan default?
- How does risk differ across credit-score and debt-to-income groups?
- Which loan purposes show different default patterns?
- How can predictive analytics support responsible lending decisions?
- What are the trade-offs between identifying more potential defaults and incorrectly flagging lower-risk applicants?

## 2. Business Objective

The objective is to use applicant data and predictive analytics to support:

1. Better understanding of credit-risk patterns.
2. More consistent risk assessment.
3. Early identification of potentially high-risk applications.
4. Management reporting and monitoring.
5. Evidence-based lending and risk-management discussions.

The model is a decision-support tool. It should not automatically determine whether a real customer receives a loan.

## 3. Stakeholders

| Stakeholder | Information needed | Potential use |
|---|---|---|
| Credit/Risk Team | Risk indicators and default patterns | Risk assessment and policy monitoring |
| Lending Team | Applicant risk characteristics | Support lending decisions |
| Finance/Management | Default trends and portfolio KPIs | Monitor financial risk |
| Data/Analytics Team | Model performance and data quality | Improve analytical solutions |
| Customer/Relationship Teams | Customer-level risk insights | Support appropriate customer engagement |

## 4. Key Business KPIs

The project monitors:

- Overall default rate
- Default rate by credit-score band
- Default rate by debt-to-income band
- Default rate by loan purpose
- Average loan amount
- Average annual income
- Average debt-to-income ratio
- Percentage of applications in higher-risk groups
- Model precision
- Model recall
- Model F1-score
- ROC-AUC

These KPIs connect technical analysis to business performance and risk monitoring.

## 5. Risk Indicators

The analysis considers indicators such as:

### Credit score
Lower credit scores can indicate greater credit risk. The project groups scores into bands so that management can compare risk patterns more easily.

### Debt-to-income ratio
A higher debt-to-income ratio may indicate greater repayment pressure. It is therefore useful when analysing affordability and default patterns.

### Loan amount relative to income
The `loan_to_income` feature provides an additional view of the size of the requested loan relative to the applicant's income.

### Loan purpose
Default patterns can be compared across different stated purposes to identify portfolio segments that may require further investigation.

## 6. Decision-Support Framework

A practical business workflow could be:

**Application data → Data quality checks → Risk analysis → Model prediction → Human review → Lending decision → Portfolio monitoring**

The model should support the process rather than replace human judgement.

For a real banking environment, the final decision would also depend on factors and controls not represented in this synthetic project, including the institution's credit policy, affordability assessment, regulatory requirements, customer circumstances, data quality, and model governance.

## 7. Precision vs Recall: Business Meaning

In credit-risk modelling, the choice of evaluation metric has a business meaning.

- **Recall:** Of customers who actually defaulted, how many did the model identify?
- **Precision:** Of customers the model flagged as potential defaulters, how many actually defaulted?

A business may care about recall when missing a potentially high-risk application has a significant cost. However, increasing recall can also produce more false positives, which may lead to additional reviews or incorrectly flag lower-risk applicants.

Therefore, the threshold should be selected using business costs, risk appetite, policy requirements and operational capacity rather than choosing a threshold only because it produces the highest technical metric.

## 8. Example Management Questions

A manager could ask:

1. Which applicant segments have the highest observed default rates?
2. Are high-risk segments becoming larger over time?
3. Are there particular loan purposes requiring additional monitoring?
4. How many applications would require manual review if a risk threshold were introduced?
5. What would be the operational impact of increasing the number of applications flagged for review?
6. How reliable is the model on unseen data?
7. What additional data would improve the analysis?
8. How should model performance be monitored after implementation?

## 9. Business Recommendations from This Synthetic Analysis

The project can support recommendations such as:

- Monitor default rates across credit-score and debt-to-income segments.
- Use risk bands to prioritise applications for further assessment rather than relying only on a single score.
- Track model precision and recall alongside portfolio KPIs.
- Investigate segments with unusually high observed default rates before changing lending policy.
- Keep human review and responsible-lending controls in the decision process.
- Reassess model performance periodically if this approach were used with real data.

These are **decision-support recommendations**, not claims about an actual bank portfolio.

## 10. Limitations

This dataset is synthetic and does not represent customers of a real bank.

The results should therefore be used to demonstrate analytical reasoning, not to make claims about actual default rates, customer behaviour, or lending policy.

A real implementation would require representative historical data, stronger validation, fairness and bias assessment, model governance, monitoring, regulatory compliance and appropriate stakeholder approval.
