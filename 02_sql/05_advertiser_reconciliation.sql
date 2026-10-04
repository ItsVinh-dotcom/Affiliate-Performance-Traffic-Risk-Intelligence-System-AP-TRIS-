-- ====================================================================
-- PROJECT: AP-TRIS
-- SCRIPT 05: Monthly Advertiser Reconciliation (Đối soát tháng với Advertiser)
-- DIALECT: PostgreSQL (đã chạy thử trên DuckDB)
-- NGUỒN: fact_conversions (tracking của sàn) + advertiser_reports (file advertiser gửi về)
-- KHÓA GHÉP: click_id của sàn = sub_id trong file advertiser
-- Lưu ý: timestamp tracking lưu theo UTC -> cộng 7 giờ để chốt tháng theo giờ VN
-- ====================================================================

WITH platform AS (
    SELECT
        c.click_id,
        c.conversion_id,
        c.publisher_id,
        c.offer_id,
        o.advertiser_name,
        CASE WHEN c.status = 'Fraud' THEN 'Rejected' ELSE c.status END AS plat_status,
        CASE WHEN c.status = 'Approved' THEN o.advertiser_revenue_vnd ELSE 0 END AS plat_revenue_vnd
    FROM fact_conversions c
    JOIN dim_offers o ON o.offer_id = c.offer_id
    WHERE DATE_TRUNC('month', c.conversion_time + INTERVAL '7 hours') = DATE '2026-09-01'
),
advertiser AS (
    SELECT sub_id AS click_id, advertiser_name, offer_id, adv_status, adv_revenue_vnd
    FROM advertiser_reports
    WHERE DATE_TRUNC('month', lead_time) = DATE '2026-09-01'
),
matched AS (
    -- FULL OUTER JOIN: giữ cả đơn chỉ có ở sàn và đơn chỉ có ở advertiser
    SELECT
        COALESCE(p.advertiser_name, a.advertiser_name) AS advertiser_name,
        COALESCE(p.click_id, a.click_id)               AS click_id,
        p.conversion_id,
        p.publisher_id,
        p.plat_status,
        a.adv_status,
        COALESCE(p.plat_revenue_vnd, 0) AS plat_revenue_vnd,
        COALESCE(a.adv_revenue_vnd, 0)  AS adv_revenue_vnd,
        CASE
            WHEN a.click_id IS NULL               THEN 'MISSING_AT_ADVERTISER'
            WHEN p.click_id IS NULL               THEN 'MISSING_IN_TRACKING'
            WHEN p.plat_status = 'Pending'        THEN 'PENDING_FINALISED'
            WHEN p.plat_status <> a.adv_status    THEN 'STATUS_MISMATCH'
            WHEN p.plat_revenue_vnd <> a.adv_revenue_vnd THEN 'AMOUNT_MISMATCH'
            ELSE 'MATCHED'
        END AS recon_status
    FROM platform p
    FULL OUTER JOIN advertiser a ON a.click_id = p.click_id
)
-- Tổng hợp theo advertiser: doanh thu sàn ghi nhận vs doanh thu advertiser xác nhận
SELECT
    advertiser_name,
    COUNT(conversion_id)                                              AS platform_leads,
    COUNT(adv_status)                                                 AS advertiser_leads,
    SUM(plat_revenue_vnd)                                             AS platform_revenue_vnd,
    SUM(CASE WHEN recon_status = 'PENDING_FINALISED' THEN adv_revenue_vnd ELSE 0 END) AS pending_finalised_vnd,
    SUM(adv_revenue_vnd)                                              AS billable_revenue_vnd,
    SUM(CASE WHEN recon_status <> 'PENDING_FINALISED'
             THEN adv_revenue_vnd - plat_revenue_vnd ELSE 0 END)      AS unexplained_variance_vnd,
    ROUND(100.0 * SUM(CASE WHEN recon_status <> 'PENDING_FINALISED'
             THEN adv_revenue_vnd - plat_revenue_vnd ELSE 0 END)
          / NULLIF(SUM(plat_revenue_vnd), 0), 2)                      AS unexplained_variance_pct,
    COUNT(*) FILTER (WHERE recon_status = 'MISSING_AT_ADVERTISER')    AS missing_at_advertiser,
    COUNT(*) FILTER (WHERE recon_status = 'MISSING_IN_TRACKING')      AS missing_in_tracking,
    COUNT(*) FILTER (WHERE recon_status = 'STATUS_MISMATCH')          AS status_mismatch,
    COUNT(*) FILTER (WHERE recon_status = 'AMOUNT_MISMATCH')          AS amount_mismatch
FROM matched
GROUP BY advertiser_name
ORDER BY billable_revenue_vnd DESC;
