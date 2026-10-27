-- Credit Risk SQL Analysis
-- Designed for PostgreSQL.
-- Import data/processed/loan_applications_clean.csv into a table called loan_applications.

-- 1. Portfolio overview
SELECT
    COUNT(*) AS total_loans,
    ROUND(AVG(loan_amount)::numeric, 2) AS avg_loan_amount,
    ROUND(AVG(credit_score)::numeric, 1) AS avg_credit_score,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct
FROM loan_applications;

-- 2. Default rate by credit score band
SELECT
    credit_score_band,
    COUNT(*) AS loans,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct
FROM loan_applications
GROUP BY credit_score_band
ORDER BY default_rate_pct DESC;

-- 3. Default rate by employment status
SELECT
    employment_status,
    COUNT(*) AS loans,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct
FROM loan_applications
GROUP BY employment_status
ORDER BY default_rate_pct DESC;

-- 4. Default rate by loan purpose
SELECT
    loan_purpose,
    COUNT(*) AS loans,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct,
    ROUND(AVG(loan_amount)::numeric, 2) AS avg_loan_amount
FROM loan_applications
GROUP BY loan_purpose
ORDER BY default_rate_pct DESC;

-- 5. High debt-to-income borrowers
SELECT
    CASE
        WHEN debt_to_income_ratio < 0.30 THEN 'Low'
        WHEN debt_to_income_ratio < 0.50 THEN 'Moderate'
        WHEN debt_to_income_ratio < 0.70 THEN 'High'
        ELSE 'Very High'
    END AS dti_band,
    COUNT(*) AS loans,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct
FROM loan_applications
GROUP BY dti_band
ORDER BY default_rate_pct DESC;

-- 6. Previous defaults and observed default rate
SELECT
    previous_defaults,
    COUNT(*) AS loans,
    ROUND(AVG(default)::numeric * 100, 2) AS default_rate_pct
FROM loan_applications
GROUP BY previous_defaults
ORDER BY previous_defaults;

-- 7. Average loan-to-income ratio by default status
SELECT
    default,
    ROUND(AVG(loan_to_income_ratio)::numeric, 3) AS avg_loan_to_income
FROM loan_applications
GROUP BY default
ORDER BY default;
