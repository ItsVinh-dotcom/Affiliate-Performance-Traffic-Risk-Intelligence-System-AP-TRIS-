-- ====================================================================
-- PROJECT: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)
-- SCRIPT 03: Fraud Detection & Traffic Quality Intelligence (SQL)
-- OBJECTIVE: Phát hiện gian lận traffic (Bot clicks, Lead ảo, IP Farm) để bảo vệ ngân sách sàn & Advertiser
-- ====================================================================

-- --------------------------------------------------------------------
-- DETECTION 1: ULTRA-FAST TIME-TO-CONVERT (Phát hiện Bot Script điền form tự động)
-- Người dùng thật mất ít nhất 20-30s để đọc trang và điền họ tên, SĐT, OTP
-- Nếu Time-to-Convert < 5 giây -> 99% là Tool/Bot chạy ngầm
-- --------------------------------------------------------------------
SELECT 
    conv.publisher_id,
    p.publisher_name,
    p.traffic_channel,
    COUNT(conv.conversion_id) AS total_bot_conversions,
    ROUND(AVG(conv.time_to_convert_seconds), 1) AS avg_ttc_seconds,
    COUNT(CASE WHEN conv.status = 'Approved' THEN 1 END) AS mistakenly_approved_count,
    SUM(conv.publisher_payout_vnd) AS potential_lost_payout_vnd
FROM fact_conversions conv
JOIN dim_publishers p ON conv.publisher_id = p.publisher_id
WHERE conv.time_to_convert_seconds < 5
GROUP BY conv.publisher_id, p.publisher_name, p.traffic_channel
HAVING COUNT(conv.conversion_id) >= 5
ORDER BY total_bot_conversions DESC;

-- --------------------------------------------------------------------
-- DETECTION 2: IP CLUSTERING & CLICK FARM ABUSE (Gian lận trùng lặp địa chỉ IP)
-- Phát hiện 1 địa chỉ IP sinh ra nhiều đơn chuyển đổi bất thường trong ngày
-- --------------------------------------------------------------------
WITH ip_stats AS (
    SELECT 
        c.user_ip,
        c.publisher_id,
        c.offer_id,
        CAST(c.click_time AS DATE) AS activity_date,
        COUNT(DISTINCT c.click_id) AS clicks_from_ip,
        COUNT(DISTINCT conv.conversion_id) AS conversions_from_ip
    FROM fact_clicks c
    JOIN fact_conversions conv ON c.click_id = conv.click_id
    GROUP BY c.user_ip, c.publisher_id, c.offer_id, CAST(c.click_time AS DATE)
)
SELECT 
    i.activity_date,
    i.publisher_id,
    p.publisher_name,
    i.user_ip,
    i.offer_id,
    o.offer_name,
    i.clicks_from_ip,
    i.conversions_from_ip,
    -- Cảnh báo mức độ rủi ro (Risk Flag)
    CASE 
        WHEN i.conversions_from_ip >= 5 THEN 'CRITICAL: High Frequency IP Farm'
        WHEN i.conversions_from_ip >= 3 THEN 'WARNING: Suspicious Repeat Submissions'
        ELSE 'MONITOR'
    END AS risk_severity
FROM ip_stats i
JOIN dim_publishers p ON i.publisher_id = p.publisher_id
JOIN dim_offers o ON i.offer_id = o.offer_id
WHERE i.conversions_from_ip >= 3
ORDER BY i.conversions_from_ip DESC;

-- --------------------------------------------------------------------
-- DETECTION 3: PUBLISHER QUALITY ANOMALY MONITOR (Tỷ lệ rớt đơn cao bất thường)
-- So sánh tỷ lệ duyệt của từng Publisher với trung bình toàn sàn
-- Nếu Publisher có > 20 đơn nhưng Approval Rate < 15% -> Dấu hiệu spam lead / số rác
-- --------------------------------------------------------------------
WITH pub_metrics AS (
    SELECT 
        p.publisher_id,
        p.publisher_name,
        p.traffic_channel,
        COUNT(conv.conversion_id) AS total_conversions,
        COUNT(CASE WHEN conv.status = 'Approved' THEN 1 END) AS approved_count,
        COUNT(CASE WHEN conv.status IN ('Rejected', 'Fraud') THEN 1 END) AS rejected_count,
        ROUND(
            CAST(COUNT(CASE WHEN conv.status = 'Approved' THEN 1 END) AS NUMERIC) / 
            NULLIF(COUNT(conv.conversion_id), 0) * 100, 
            2
        ) AS pub_approval_rate_pct
    FROM dim_publishers p
    JOIN fact_conversions conv ON p.publisher_id = conv.publisher_id
    GROUP BY p.publisher_id, p.publisher_name, p.traffic_channel
),
network_avg AS (
    SELECT 
        ROUND(
            CAST(COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS NUMERIC) / 
            NULLIF(COUNT(conversion_id), 0) * 100, 
            2
        ) AS network_avg_approval_rate_pct
    FROM fact_conversions
)
SELECT 
    pm.publisher_id,
    pm.publisher_name,
    pm.traffic_channel,
    pm.total_conversions,
    pm.approved_count,
    pm.rejected_count,
    pm.pub_approval_rate_pct,
    na.network_avg_approval_rate_pct,
    -- Chênh lệch so với chuẩn sàn
    ROUND(pm.pub_approval_rate_pct - na.network_avg_approval_rate_pct, 2) AS variance_from_benchmark_pct,
    CASE 
        WHEN pm.total_conversions >= 20 AND pm.pub_approval_rate_pct < 15 THEN 'ACTION REQUIRED: Block or Audit Publisher'
        WHEN pm.total_conversions >= 10 AND pm.pub_approval_rate_pct < 25 THEN 'WATCHLIST: Review Traffic Source'
        ELSE 'NORMAL'
    END AS recommendation
FROM pub_metrics pm
CROSS JOIN network_avg na
ORDER BY pm.rejected_count DESC;
