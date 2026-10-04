-- ====================================================================
-- PROJECT: AP-TRIS
-- SCRIPT 06: Weekly Performance Report - Week over Week (WoW)
-- DIALECT: PostgreSQL (đã chạy thử trên DuckDB)
-- KỸ THUẬT: CTE, DATE_TRUNC theo tuần, window function LAG() để so sánh tuần trước
-- ====================================================================

WITH weekly AS (
    SELECT
        DATE_TRUNC('week', c.conversion_time + INTERVAL '7 hours') AS week_start,   -- tuần bắt đầu thứ Hai, giờ VN
        o.offer_name,
        COUNT(*)                                                    AS conversions,
        COUNT(*) FILTER (WHERE c.status = 'Approved')               AS approved,
        SUM(c.gross_margin_vnd)                                     AS margin_vnd
    FROM fact_conversions c
    JOIN dim_offers o ON o.offer_id = c.offer_id
    GROUP BY 1, 2
),
with_prev AS (
    SELECT
        *,
        ROUND(100.0 * approved / NULLIF(conversions, 0), 1)                         AS approval_rate_pct,
        LAG(ROUND(100.0 * approved / NULLIF(conversions, 0), 1))
            OVER (PARTITION BY offer_name ORDER BY week_start)                      AS approval_rate_prev_pct,
        LAG(margin_vnd) OVER (PARTITION BY offer_name ORDER BY week_start)          AS margin_prev_vnd
    FROM weekly
)
SELECT
    week_start,
    offer_name,
    conversions,
    approval_rate_pct,
    approval_rate_pct - approval_rate_prev_pct                                       AS approval_rate_wow_pp,
    margin_vnd,
    ROUND(100.0 * (margin_vnd - margin_prev_vnd) / NULLIF(margin_prev_vnd, 0), 1)    AS margin_wow_pct,
    CASE
        WHEN approval_rate_pct - approval_rate_prev_pct <= -5 THEN 'FLAG: approval rate drop'
        WHEN (margin_vnd - margin_prev_vnd) / NULLIF(margin_prev_vnd, 0) <= -0.20 THEN 'FLAG: margin drop'
        ELSE 'OK'
    END AS flag
FROM with_prev
WHERE week_start = (SELECT MAX(week_start) - INTERVAL '7 days' FROM weekly)   -- tuần đầy đủ gần nhất
ORDER BY margin_vnd DESC;
