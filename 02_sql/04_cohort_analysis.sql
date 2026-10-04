-- ====================================================================
-- PROJECT: AP-TRIS
-- SCRIPT 04: Publisher Cohort Retention (Logo retention, Revenue retention, LTV)
-- DIALECT: PostgreSQL (đã chạy thử trên DuckDB)
-- NGUỒN: publisher_registry (mọi publisher từng đăng ký)
--        + publisher_monthly_activity (đơn duyệt & lãi theo publisher × tháng)
-- KỸ THUẬT: CTE, DATE_TRUNC, tính chỉ số tháng, pivot bằng FILTER, window SUM() OVER
-- ====================================================================

-- QUERY 1: MA TRẬN RETENTION (mỗi dòng = 1 cohort tháng đăng ký, mỗi cột = M+k)
WITH cohort AS (
    SELECT publisher_id,
           traffic_channel,
           DATE_TRUNC('month', CAST(join_date AS DATE)) AS cohort_month
    FROM publisher_registry
),
activity AS (
    SELECT a.publisher_id,
           c.cohort_month,
           CAST(a.month || '-01' AS DATE) AS activity_month,
           a.gross_margin_vnd
    FROM publisher_monthly_activity a
    JOIN cohort c ON c.publisher_id = a.publisher_id
),
indexed AS (
    SELECT *,
           (EXTRACT(YEAR FROM activity_month) - EXTRACT(YEAR FROM cohort_month)) * 12
         + (EXTRACT(MONTH FROM activity_month) - EXTRACT(MONTH FROM cohort_month)) AS month_index
    FROM activity
    WHERE activity_month >= cohort_month          -- loại hoạt động trước ngày đăng ký (lỗi dữ liệu)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS registered FROM cohort GROUP BY cohort_month
)
SELECT
    s.cohort_month,
    s.registered,
    ROUND(100.0 * COUNT(DISTINCT i.publisher_id) FILTER (WHERE i.month_index = 0) / s.registered, 1) AS m0_pct,
    ROUND(100.0 * COUNT(DISTINCT i.publisher_id) FILTER (WHERE i.month_index = 1) / s.registered, 1) AS m1_pct,
    ROUND(100.0 * COUNT(DISTINCT i.publisher_id) FILTER (WHERE i.month_index = 2) / s.registered, 1) AS m2_pct,
    ROUND(100.0 * COUNT(DISTINCT i.publisher_id) FILTER (WHERE i.month_index = 3) / s.registered, 1) AS m3_pct,
    ROUND(100.0 * COUNT(DISTINCT i.publisher_id) FILTER (WHERE i.month_index = 6) / s.registered, 1) AS m6_pct
FROM cohort_size s
LEFT JOIN indexed i ON i.cohort_month = s.cohort_month
GROUP BY s.cohort_month, s.registered
ORDER BY s.cohort_month;
-- Lưu ý: ô của cohort còn quá "trẻ" (chưa đủ k tháng) sẽ ra 0 -> khi trình bày phải để trống, không phải churn.


-- QUERY 2: LTV TÍCH LŨY THEO KÊNH (lãi gộp cộng dồn trên mỗi publisher ĐĂNG KÝ, kể cả người không kích hoạt)
WITH cohort AS (
    SELECT publisher_id, traffic_channel, DATE_TRUNC('month', CAST(join_date AS DATE)) AS cohort_month
    FROM publisher_registry
    WHERE DATE_TRUNC('month', CAST(join_date AS DATE)) <= DATE '2026-06-01'   -- chỉ cohort đủ 3 tháng quan sát
),
indexed AS (
    SELECT c.traffic_channel,
           (EXTRACT(YEAR FROM CAST(a.month || '-01' AS DATE)) - EXTRACT(YEAR FROM c.cohort_month)) * 12
         + (EXTRACT(MONTH FROM CAST(a.month || '-01' AS DATE)) - EXTRACT(MONTH FROM c.cohort_month)) AS month_index,
           a.gross_margin_vnd
    FROM publisher_monthly_activity a
    JOIN cohort c ON c.publisher_id = a.publisher_id
),
by_month AS (
    SELECT traffic_channel, month_index, SUM(gross_margin_vnd) AS margin_vnd
    FROM indexed
    WHERE month_index BETWEEN 0 AND 3
    GROUP BY traffic_channel, month_index
),
registered AS (
    SELECT traffic_channel, COUNT(*) AS n FROM cohort GROUP BY traffic_channel
)
SELECT
    b.traffic_channel,
    b.month_index,
    ROUND(SUM(b.margin_vnd) OVER (PARTITION BY b.traffic_channel ORDER BY b.month_index) / r.n, 0)
        AS cumulative_ltv_per_registered_vnd
FROM by_month b
JOIN registered r ON r.traffic_channel = b.traffic_channel
ORDER BY b.traffic_channel, b.month_index;
