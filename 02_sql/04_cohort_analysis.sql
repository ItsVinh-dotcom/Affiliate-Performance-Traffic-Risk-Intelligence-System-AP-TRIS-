-- ====================================================================
-- PROJECT: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)
-- SCRIPT 04: Publisher Cohort Retention & Cumulative Value Analysis
-- OBJECTIVE: Theo dõi vòng đời (Lifecycle) và tỷ lệ giữ chân (Retention) của các lứa Publisher
-- DIALECT: PostgreSQL (DATE_TRUNC, TO_CHAR)
-- LƯU Ý: Dataset mô phỏng hiện chỉ có 2 tháng hoạt động (08-09/2026) nên kết quả mang tính minh họa.
-- ====================================================================

-- BƯỚC 1: XÁC ĐỊNH COHORT CỦA PUBLISHER DỰA VÀO THÁNG GIA NHẬP (JOIN MONTH)
WITH publisher_cohort AS (
    SELECT 
        publisher_id,
        DATE_TRUNC('month', join_date) AS cohort_month
    FROM dim_publishers
),

-- BƯỚC 2: TẬP HỢP HOẠT ĐỘNG PHÁT SINH CHUYỂN ĐỔI THEO TỪNG THÁNG
publisher_activity AS (
    SELECT 
        conv.publisher_id,
        DATE_TRUNC('month', conv.conversion_time) AS activity_month,
        COUNT(conv.conversion_id) AS monthly_conversions,
        SUM(conv.gross_margin_vnd) AS monthly_margin_vnd
    FROM fact_conversions conv
    WHERE conv.status = 'Approved'
    GROUP BY conv.publisher_id, DATE_TRUNC('month', conv.conversion_time)
),

-- BƯỚC 3: TÍNH TOÁN KHOẢNG CÁCH THÁNG (MONTH INDEX: 0, 1, 2, ...)
cohort_table AS (
    SELECT 
        pc.cohort_month,
        pa.activity_month,
        -- Số tháng kể từ khi Publisher onboard (Month 0, Month 1, Month 2...)
        (
            EXTRACT(YEAR FROM pa.activity_month) * 12 + EXTRACT(MONTH FROM pa.activity_month)
        ) - (
            EXTRACT(YEAR FROM pc.cohort_month) * 12 + EXTRACT(MONTH FROM pc.cohort_month)
        ) AS month_number,
        COUNT(DISTINCT pc.publisher_id) AS active_publishers,
        SUM(pa.monthly_conversions) AS total_approved_conversions,
        SUM(pa.monthly_margin_vnd) AS total_margin_generated
    FROM publisher_cohort pc
    JOIN publisher_activity pa ON pc.publisher_id = pa.publisher_id
    GROUP BY pc.cohort_month, pa.activity_month
),

-- BƯỚC 4: TỔNG HỢP QUY MÔ BAN ĐẦU CỦA MỖI COHORT (COHORT SIZE)
cohort_size AS (
    SELECT 
        DATE_TRUNC('month', join_date) AS cohort_month,
        COUNT(publisher_id) AS initial_publishers
    FROM dim_publishers
    GROUP BY DATE_TRUNC('month', join_date)
)

-- BƯỚC 5: TÍNH TỶ LỆ GIỮ CHÂN (RETENTION RATE %) VÀ GIÁ TRỊ TÍCH LŨY (LTV)
SELECT 
    TO_CHAR(ct.cohort_month, 'YYYY-MM') AS cohort,
    cs.initial_publishers AS cohort_size,
    ct.month_number,
    ct.active_publishers,
    -- Tỷ lệ Publisher vẫn hoạt động tạo ra đơn duyệt (%)
    ROUND(CAST(ct.active_publishers AS NUMERIC) / cs.initial_publishers * 100, 2) AS retention_rate_pct,
    ct.total_approved_conversions,
    ct.total_margin_generated AS net_margin_vnd,
    -- Lợi nhuận trung bình trên mỗi Publisher trong Cohort
    ROUND(CAST(ct.total_margin_generated AS NUMERIC) / cs.initial_publishers, 0) AS avg_margin_per_publisher_vnd
FROM cohort_table ct
JOIN cohort_size cs ON ct.cohort_month = cs.cohort_month
ORDER BY ct.cohort_month ASC, ct.month_number ASC;
