-- ============================================================
-- RevOps Case Study | Unit4-style Analysis
-- Script 01: Funnel Conversion Analysis
-- ============================================================

-- 1. Overall funnel summary
SELECT
    segment,
    COUNT(*)                                                        AS total_leads,
    SUM(CASE WHEN became_opportunity THEN 1 ELSE 0 END)            AS opportunities,
    SUM(CASE WHEN closed_won THEN 1 ELSE 0 END)                    AS closed_won,
    ROUND(
        100.0 * SUM(CASE WHEN became_opportunity THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS lead_to_opp_pct,
    ROUND(
        100.0 * SUM(CASE WHEN closed_won THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN became_opportunity THEN 1 ELSE 0 END), 0), 1
    )                                                               AS opp_to_close_pct,
    ROUND(
        100.0 * SUM(CASE WHEN closed_won THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                               AS overall_win_rate_pct
FROM leads_pipeline
GROUP BY segment
ORDER BY total_leads DESC;


-- 2. Revenue by segment & source
SELECT
    segment,
    source,
    COUNT(*)                                                        AS won_deals,
    ROUND(SUM(deal_value_eur), 0)                                  AS total_revenue_eur,
    ROUND(AVG(deal_value_eur), 0)                                  AS avg_deal_size_eur
FROM leads_pipeline
WHERE closed_won = TRUE
GROUP BY segment, source
ORDER BY total_revenue_eur DESC;


-- 3. Sales velocity (days from lead to close) by segment
SELECT
    segment,
    ROUND(AVG(
        julianday(close_date) - julianday(created_date)
    ), 0)                                                           AS avg_days_to_close,
    ROUND(AVG(deal_value_eur), 0)                                  AS avg_deal_eur,
    COUNT(*)                                                        AS deals
FROM leads_pipeline
WHERE closed_won = TRUE
GROUP BY segment;


-- 4. Monthly pipeline trend (created vs won)
SELECT
    strftime('%Y-%m', created_date)                                AS month,
    COUNT(*)                                                        AS leads_created,
    SUM(CASE WHEN became_opportunity THEN 1 ELSE 0 END)            AS opportunities,
    SUM(CASE WHEN closed_won THEN 1 ELSE 0 END)                    AS closed_won,
    ROUND(COALESCE(SUM(deal_value_eur), 0), 0)                    AS revenue_eur
FROM leads_pipeline
GROUP BY month
ORDER BY month;
