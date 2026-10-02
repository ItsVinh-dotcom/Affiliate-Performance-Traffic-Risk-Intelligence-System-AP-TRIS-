-- ====================================================================
-- PROJECT: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)
-- SCRIPT 02: Core Affiliate Marketing KPI Analytics
-- METRICS: Clicks, Conversions, CR (%), Approval Rate (%), EPC, Gross Margin, Net ROI
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: EXECUTIVE CAMPAIGN PERFORMANCE REPORT (Báo cáo tổng hợp theo Offer)
-- Đánh giá hiệu quả từng chiến dịch: Ngân hàng, Tài chính và CPO
-- --------------------------------------------------------------------
WITH click_summary AS (
    SELECT 
        offer_id,
        COUNT(click_id) AS total_clicks
    FROM fact_clicks
    GROUP BY offer_id
),
conversion_summary AS (
    SELECT 
        offer_id,
        COUNT(conversion_id) AS total_conversions,
        COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS approved_conversions,
        COUNT(CASE WHEN status = 'Rejected' THEN 1 END) AS rejected_conversions,
        COUNT(CASE WHEN status = 'Fraud' THEN 1 END) AS fraud_conversions,
        SUM(advertiser_revenue_vnd) AS total_revenue_vnd,
        SUM(publisher_payout_vnd) AS total_payout_vnd,
        SUM(gross_margin_vnd) AS total_gross_margin_vnd
    FROM fact_conversions
    GROUP BY offer_id
)
SELECT 
    o.offer_id,
    o.offer_name,
    o.vertical,
    o.payout_model,
    o.advertiser_name,
    COALESCE(c.total_clicks, 0) AS total_clicks,
    COALESCE(conv.total_conversions, 0) AS total_conversions,
    -- Conversion Rate (CR%): Tỷ lệ từ Click chuyển thành Form đăng ký
    ROUND(CAST(COALESCE(conv.total_conversions, 0) AS NUMERIC) / NULLIF(c.total_clicks, 0) * 100, 2) AS cr_pct,
    COALESCE(conv.approved_conversions, 0) AS approved_conversions,
    -- Approval Rate (%): Tỷ lệ đơn/hồ sơ được ngân hàng thẩm định duyệt thành công
    ROUND(CAST(COALESCE(conv.approved_conversions, 0) AS NUMERIC) / NULLIF(conv.total_conversions, 0) * 100, 2) AS approval_rate_pct,
    -- Benchmark so với tỷ lệ duyệt kỳ vọng
    ROUND(o.expected_approval_rate * 100, 2) AS benchmark_approval_rate_pct,
    COALESCE(conv.total_revenue_vnd, 0) AS gross_revenue_vnd,
    COALESCE(conv.total_payout_vnd, 0) AS publisher_payout_vnd,
    COALESCE(conv.total_gross_margin_vnd, 0) AS gross_margin_vnd,
    -- Gross Margin (%): Biên lợi nhuận gộp mà sàn giữ lại
    ROUND(CAST(COALESCE(conv.total_gross_margin_vnd, 0) AS NUMERIC) / NULLIF(conv.total_revenue_vnd, 0) * 100, 2) AS margin_pct,
    -- EPC (Earnings Per Click - VNĐ): Thu nhập trung bình trên mỗi click cho Publisher
    ROUND(CAST(COALESCE(conv.total_payout_vnd, 0) AS NUMERIC) / NULLIF(c.total_clicks, 0), 0) AS epc_vnd
FROM dim_offers o
LEFT JOIN click_summary c ON o.offer_id = c.offer_id
LEFT JOIN conversion_summary conv ON o.offer_id = conv.offer_id
ORDER BY gross_margin_vnd DESC;

-- --------------------------------------------------------------------
-- QUERY 2: TOP PUBLISHER SCORECARD & RANKING (Xếp hạng đối tác phân phối)
-- Ứng dụng Window Functions (DENSE_RANK, PERCENT_RANK) để phân nhóm Publisher
-- --------------------------------------------------------------------
WITH pub_clicks AS (
    SELECT publisher_id, COUNT(click_id) AS total_clicks
    FROM fact_clicks
    GROUP BY publisher_id
),
pub_conversions AS (
    SELECT 
        publisher_id,
        COUNT(conversion_id) AS total_conversions,
        COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS approved_conversions,
        SUM(advertiser_revenue_vnd) AS total_revenue_generated,
        SUM(publisher_payout_vnd) AS total_commission_earned,
        SUM(gross_margin_vnd) AS total_platform_profit
    FROM fact_conversions
    GROUP BY publisher_id
)
SELECT 
    p.publisher_id,
    p.publisher_name,
    p.traffic_channel,
    p.tier,
    COALESCE(pc.total_clicks, 0) AS total_clicks,
    COALESCE(pconv.total_conversions, 0) AS total_conversions,
    COALESCE(pconv.approved_conversions, 0) AS approved_conversions,
    ROUND(CAST(COALESCE(pconv.approved_conversions, 0) AS NUMERIC) / NULLIF(pconv.total_conversions, 0) * 100, 2) AS approval_rate_pct,
    COALESCE(pconv.total_commission_earned, 0) AS total_commission_earned_vnd,
    COALESCE(pconv.total_platform_profit, 0) AS platform_profit_vnd,
    -- Xếp hạng Publisher theo Lợi nhuận mang về cho Sàn
    DENSE_RANK() OVER (ORDER BY COALESCE(pconv.total_platform_profit, 0) DESC) AS profit_rank,
    -- Đóng góp % vào tổng lợi nhuận toàn sàn
    ROUND(
        CAST(COALESCE(pconv.total_platform_profit, 0) AS NUMERIC) / 
        NULLIF(SUM(COALESCE(pconv.total_platform_profit, 0)) OVER (), 0) * 100, 
        2
    ) AS profit_contribution_pct
FROM dim_publishers p
LEFT JOIN pub_clicks pc ON p.publisher_id = pc.publisher_id
LEFT JOIN pub_conversions pconv ON p.publisher_id = pconv.publisher_id
WHERE COALESCE(pc.total_clicks, 0) > 0
ORDER BY profit_rank ASC
LIMIT 20;

-- --------------------------------------------------------------------
-- QUERY 3: TRAFFIC CHANNEL COMPARISON (So sánh hiệu quả các kênh kéo khách)
-- TikTok vs Facebook Ads vs Google Ads vs SEO Blog
-- --------------------------------------------------------------------
SELECT 
    p.traffic_channel,
    COUNT(DISTINCT p.publisher_id) AS active_publishers,
    COUNT(c.click_id) AS total_clicks,
    COUNT(conv.conversion_id) AS total_conversions,
    ROUND(CAST(COUNT(conv.conversion_id) AS NUMERIC) / NULLIF(COUNT(c.click_id), 0) * 100, 2) AS cr_pct,
    ROUND(
        CAST(COUNT(CASE WHEN conv.status = 'Approved' THEN 1 END) AS NUMERIC) / 
        NULLIF(COUNT(conv.conversion_id), 0) * 100, 
        2
    ) AS channel_approval_rate_pct,
    SUM(conv.gross_margin_vnd) AS total_margin_vnd,
    ROUND(CAST(SUM(conv.publisher_payout_vnd) AS NUMERIC) / NULLIF(COUNT(c.click_id), 0), 0) AS avg_epc_vnd
FROM dim_publishers p
LEFT JOIN fact_clicks c ON p.publisher_id = c.publisher_id
LEFT JOIN fact_conversions conv ON c.click_id = conv.click_id
GROUP BY p.traffic_channel
ORDER BY total_margin_vnd DESC;
