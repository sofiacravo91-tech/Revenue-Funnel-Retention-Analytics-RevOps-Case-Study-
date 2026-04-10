-- ============================================================
-- RevOps Case Study | Unit4-style Analysis
-- Script 02: Retention & Churn Analysis
-- ============================================================

-- 1. Churn rate by segment
SELECT
    segment,
    COUNT(*)                                                        AS total_customers,
    SUM(CASE WHEN churned THEN 1 ELSE 0 END)                      AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN churned THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churned THEN arr_eur ELSE 0 END), 0)      AS arr_at_risk_eur
FROM customers_retention
GROUP BY segment
ORDER BY churn_rate_pct DESC;


-- 2. Cohort retention overview
SELECT
    cohort,
    COUNT(*)                                                        AS customers,
    SUM(CASE WHEN churned = FALSE THEN 1 ELSE 0 END)              AS retained,
    ROUND(
        100.0 * SUM(CASE WHEN churned = FALSE THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS retention_rate_pct,
    ROUND(AVG(arr_eur), 0)                                         AS avg_arr_eur
FROM customers_retention
GROUP BY cohort
ORDER BY cohort;


-- 3. Churn risk signals — customers showing disengagement
--    Business question: "Which customers should we call this week?"
SELECT
    customer_id,
    segment,
    arr_eur,
    nps_score,
    support_tickets_6m,
    last_login_days_ago,
    -- Risk score: weighted flag (ambiguous threshold — open for discussion)
    CASE
        WHEN last_login_days_ago > 60
         AND nps_score <= 5
         AND support_tickets_6m >= 5  THEN 'High Risk'
        WHEN last_login_days_ago > 45
          OR nps_score <= 4            THEN 'Medium Risk'
        ELSE                                'Low Risk'
    END                                                             AS churn_risk_flag
FROM customers_retention
WHERE churned = FALSE
ORDER BY arr_eur DESC, last_login_days_ago DESC;


-- 4. ARR concentration — top 20% customers
--    Strategic question: "Are we too dependent on a few accounts?"
SELECT
    segment,
    COUNT(*)                                                        AS customer_count,
    ROUND(SUM(arr_eur), 0)                                        AS total_arr_eur,
    ROUND(AVG(arr_eur), 0)                                        AS avg_arr_eur,
    ROUND(MAX(arr_eur), 0)                                        AS max_arr_eur
FROM customers_retention
GROUP BY segment
ORDER BY total_arr_eur DESC;
