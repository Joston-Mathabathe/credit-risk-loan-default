-- Credit Risk / Loan Default Analysis
-- Table name assumed: loan_applications

-- 1. Overall default rate
SELECT
    COUNT(*) AS applications,
    SUM(default) AS defaults,
    ROUND(100.0 * AVG(default), 2) AS default_rate_pct
FROM loan_applications;

-- 2. Default rate by credit score band
SELECT
    credit_score_band,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(default), 2) AS default_rate_pct
FROM loan_applications
GROUP BY credit_score_band
ORDER BY credit_score_band;

-- 3. Default rate by loan purpose
SELECT
    loan_purpose,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(default), 2) AS default_rate_pct
FROM loan_applications
GROUP BY loan_purpose
ORDER BY default_rate_pct DESC;

-- 4. Default rate by debt-to-income band
SELECT
    CASE
        WHEN debt_to_income < 0.20 THEN '0-20%'
        WHEN debt_to_income < 0.40 THEN '20-40%'
        WHEN debt_to_income < 0.60 THEN '40-60%'
        WHEN debt_to_income < 0.80 THEN '60-80%'
        ELSE '80-100%'
    END AS dti_band,
    COUNT(*) AS applications,
    ROUND(100.0 * AVG(default), 2) AS default_rate_pct
FROM loan_applications
GROUP BY 1
ORDER BY 1;

-- 5. Applications with multiple risk indicators
SELECT
    loan_id,
    credit_score,
    debt_to_income,
    loan_amount,
    late_payments_12m,
    default
FROM loan_applications
WHERE credit_score < 600
  AND debt_to_income > 0.50
ORDER BY debt_to_income DESC;
