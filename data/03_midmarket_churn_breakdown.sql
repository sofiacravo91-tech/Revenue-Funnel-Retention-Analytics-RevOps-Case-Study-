-- ============================================================
-- RevOps Case Study | Unit4-style Analysis
-- Script 03: Mid-Market Churn Deep Dive
-- ============================================================
-- Context: Mid-Market overall churn is 14% — close to the 15%
-- risk threshold. This script breaks it down by region and
-- industry to identify where the problem is concentrated.
-- ============================================================


-- 1. Mid-Market churn by REGION
--    Business question: "Is churn evenly distributed or concentrated in one market?"
SELECT
    region,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END)                      AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churned THEN arr_eur ELSE 0 END), 0)      AS arr_at_risk_eur
FROM customers_retention
WHERE segment = 'Mid-Market'
GROUP BY region
ORDER BY churn_rate_pct DESC;

-- KEY FINDING:
-- AMER: 21% churn — more than double EMEA (9%)
-- The 14% average masks a critical problem in AMER
-- Recommended action: urgent CS review of all AMER Mid-Market accounts


-- 2. Mid-Market churn by INDUSTRY
--    Business question: "Are certain verticals structurally more likely to churn?"
SELECT
    industry,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END)                      AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churned THEN arr_eur ELSE 0 END), 0)      AS arr_at_risk_eur
FROM customers_retention
WHERE segment = 'Mid-Market'
GROUP BY industry
ORDER BY churn_rate_pct DESC;

-- KEY FINDING:
-- Education: 29% churn — nearly double the segment average
-- Public Sector: 6% churn — the healthiest vertical
-- Recommended action: investigate Education accounts before next renewal cycle


-- 3. COMBINED: AMER x Industry cross-analysis
--    Business question: "Is AMER churn driven by Education, or is it broader?"
--    Strategic question: "Do we have one problem or two separate problems?"
SELECT
    region,
    industry,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END)                      AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churned THEN arr_eur ELSE 0 END), 0)      AS arr_at_risk_eur
FROM customers_retention
WHERE segment = 'Mid-Market'
GROUP BY region, industry
HAVING total_customers >= 2
ORDER BY churn_rate_pct DESC;

-- THIS IS THE KEY QUESTION:
-- If AMER churn is concentrated in Education → one targeted problem to solve
-- If AMER churn is spread across industries → systemic issue (pricing? support? product fit?)
-- This distinction changes the recommended action entirely
-- → Bring this to CS + Sales leadership before drawing conclusions
