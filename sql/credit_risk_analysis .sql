-- Credit Risk SQL Analysis
-- Designed for Microsoft SQL Server (T-SQL).
-- Import data/processed/loan_applications_clean.csv into a table called dbo.loan_applications.

/* ------------------------------------------------------------------
   0. Table definition and data load
   ------------------------------------------------------------------ */
-- Safe setup: create the table only if it does not already exist.
-- If SSMS Import Flat File already created dbo.loan_applications, this is skipped.
IF OBJECT_ID('dbo.loan_applications', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.loan_applications (
        loan_id                  VARCHAR(20)   NOT NULL PRIMARY KEY,
        customer_id              VARCHAR(20)   NOT NULL,
        age                      INT           NULL,
        annual_income            DECIMAL(18,2) NULL,
        employment_status        VARCHAR(50)   NULL,
        employment_length_years  DECIMAL(6,1)  NULL,
        credit_score             INT           NULL,
        loan_amount              DECIMAL(18,2) NULL,
        loan_term_months         INT           NULL,
        interest_rate            DECIMAL(6,2)  NULL,
        existing_loans           INT           NULL,
        previous_defaults        INT           NULL,
        debt_to_income_ratio     DECIMAL(8,3)  NULL,
        home_ownership           VARCHAR(50)   NULL,
        loan_purpose             VARCHAR(50)   NULL,
        application_channel      VARCHAR(50)   NULL,
        [default]                TINYINT       NOT NULL,
        credit_score_band        VARCHAR(30)   NULL,
        income_band              VARCHAR(30)   NULL,
        loan_to_income_ratio     DECIMAL(10,4) NULL
    );
END;
GO

-- Option A: BULK INSERT (path must be readable by the SQL Server service account).
-- Use CODEPAGE/FORMAT = 'CSV' (SQL Server 2017+). Adjust the path to your machine.
-- BULK INSERT dbo.loan_applications
-- FROM 'C:\data\processed\loan_applications_clean.csv'
-- WITH (FORMAT = 'CSV', FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0a', TABLOCK);
--
-- Option B: SSMS -> right-click database -> Tasks -> Import Flat File...
-- Note: Import Flat File creates a new table; use it BEFORE the setup block above,
-- or use BULK INSERT after creating the table. Do not run both imports.
GO

/* ------------------------------------------------------------------
   1. Portfolio overview
   Note: [default] is an INT/TINYINT, so it is cast to avoid integer
   division in AVG().
   ------------------------------------------------------------------ */
SELECT
    COUNT(*)                                              AS total_loans,
    ROUND(AVG(CAST(loan_amount  AS DECIMAL(18,2))), 2)    AS avg_loan_amount,
    ROUND(AVG(CAST(credit_score AS DECIMAL(10,2))), 1)    AS avg_credit_score,
    ROUND(AVG(CAST([default]    AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct
FROM dbo.loan_applications;

/* ------------------------------------------------------------------
   2. Default rate by credit score band
   ------------------------------------------------------------------ */
SELECT
    credit_score_band,
    COUNT(*) AS loans,
    ROUND(AVG(CAST([default] AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct
FROM dbo.loan_applications
GROUP BY credit_score_band
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------------
   3. Default rate by employment status
   ------------------------------------------------------------------ */
SELECT
    employment_status,
    COUNT(*) AS loans,
    ROUND(AVG(CAST([default] AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct
FROM dbo.loan_applications
GROUP BY employment_status
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------------
   4. Default rate by loan purpose
   ------------------------------------------------------------------ */
SELECT
    loan_purpose,
    COUNT(*) AS loans,
    ROUND(AVG(CAST([default] AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct,
    ROUND(AVG(CAST(loan_amount AS DECIMAL(18,2))), 2)     AS avg_loan_amount
FROM dbo.loan_applications
GROUP BY loan_purpose
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------------
   5. High debt-to-income borrowers
   T-SQL does not allow a SELECT alias in GROUP BY, so the CASE is
   computed in a derived table and grouped in the outer query.
   ------------------------------------------------------------------ */
SELECT
    dti_band,
    COUNT(*) AS loans,
    ROUND(AVG(CAST([default] AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct
FROM (
    SELECT
        [default],
        CASE
            WHEN debt_to_income_ratio < 0.30 THEN 'Low'
            WHEN debt_to_income_ratio < 0.50 THEN 'Moderate'
            WHEN debt_to_income_ratio < 0.70 THEN 'High'
            ELSE 'Very High'
        END AS dti_band
    FROM dbo.loan_applications
) AS banded
GROUP BY dti_band
ORDER BY default_rate_pct DESC;

/* ------------------------------------------------------------------
   6. Previous defaults and observed default rate
   ------------------------------------------------------------------ */
SELECT
    previous_defaults,
    COUNT(*) AS loans,
    ROUND(AVG(CAST([default] AS DECIMAL(10,4))) * 100, 2) AS default_rate_pct
FROM dbo.loan_applications
GROUP BY previous_defaults
ORDER BY previous_defaults;

/* ------------------------------------------------------------------
   7. Average loan-to-income ratio by default status
   ------------------------------------------------------------------ */
SELECT
    [default],
    ROUND(AVG(CAST(loan_to_income_ratio AS DECIMAL(18,6))), 3) AS avg_loan_to_income
FROM dbo.loan_applications
GROUP BY [default]
ORDER BY [default];
