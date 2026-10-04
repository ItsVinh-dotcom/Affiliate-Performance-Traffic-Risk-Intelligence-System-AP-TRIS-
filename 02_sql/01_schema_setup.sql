-- ====================================================================
-- PROJECT: Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)
-- SCRIPT 01: Star Schema & Table Definitions (DDL)
-- DIALECT: PostgreSQL
-- ====================================================================

-- 1. DIMENSION TABLE: PUBLISHERS (Đối tác phân phối traffic / KOC / Media Buyer)
CREATE TABLE IF NOT EXISTS dim_publishers (
    publisher_id VARCHAR(50) PRIMARY KEY,
    publisher_name VARCHAR(255) NOT NULL,
    traffic_channel VARCHAR(100),       -- TikTok Creator, Facebook Media Buyer, Google Ads, SEO Blog, etc.
    tier VARCHAR(50),                   -- Platinum, Gold, Silver, Bronze
    status VARCHAR(50) DEFAULT 'Active',-- Active, Flagged, Suspended
    join_date DATE NOT NULL,
    is_fraud_suspect BOOLEAN DEFAULT FALSE
);

-- 2. DIMENSION TABLE: OFFERS / CAMPAIGNS (Chiến dịch từ Advertiser / Ngân hàng / Nhãn hàng)
CREATE TABLE IF NOT EXISTS dim_offers (
    offer_id VARCHAR(50) PRIMARY KEY,
    offer_name VARCHAR(255) NOT NULL,
    vertical VARCHAR(100),              -- Finance & Banking, Beauty & Cosmetics, Health & Wellness, E-commerce
    payout_model VARCHAR(50),           -- CPA, CPL, CPO, CPS, CPI
    advertiser_name VARCHAR(255),       -- VPBank, Techcombank, Shopee, etc.
    advertiser_revenue_vnd NUMERIC(15, 2), -- Doanh thu sàn thu từ Advertiser trên mỗi đơn duyệt
    publisher_payout_vnd NUMERIC(15, 2),   -- Hoa hồng sàn trả cho Publisher trên mỗi đơn duyệt
    expected_approval_rate NUMERIC(5, 4)   -- Tỷ lệ duyệt kỳ vọng chuẩn ngành
);

-- 3. FACT TABLE: CLICKS (Lượt truy cập vào link tiếp thị)
CREATE TABLE IF NOT EXISTS fact_clicks (
    click_id VARCHAR(100) PRIMARY KEY,
    click_time TIMESTAMP NOT NULL,
    publisher_id VARCHAR(50) NOT NULL REFERENCES dim_publishers(publisher_id),
    offer_id VARCHAR(50) NOT NULL REFERENCES dim_offers(offer_id),
    device_type VARCHAR(50),            -- Mobile, Desktop, Tablet
    user_ip VARCHAR(50) NOT NULL
);

-- 4. FACT TABLE: CONVERSIONS (Chuyển đổi: Đơn đăng ký, Mở tài khoản, Đặt hàng)
CREATE TABLE IF NOT EXISTS fact_conversions (
    conversion_id VARCHAR(100) PRIMARY KEY,
    click_id VARCHAR(100) NOT NULL,
    conversion_time TIMESTAMP NOT NULL,
    publisher_id VARCHAR(50) NOT NULL REFERENCES dim_publishers(publisher_id),
    offer_id VARCHAR(50) NOT NULL REFERENCES dim_offers(offer_id),
    time_to_convert_seconds INT,        -- Số giây từ lúc Click đến lúc hoàn tất form (Key metric phát hiện bot)
    status VARCHAR(50) NOT NULL,        -- Approved, Rejected, Pending, Fraud
    rejection_reason VARCHAR(255),      -- Duplicate Phone, Invalid eKYC, Bad Debt History, Bot Traffic
    advertiser_revenue_vnd NUMERIC(15, 2) DEFAULT 0,
    publisher_payout_vnd NUMERIC(15, 2) DEFAULT 0,
    gross_margin_vnd NUMERIC(15, 2) DEFAULT 0
);

-- 5. PERFORMANCE INDEXES (Tối ưu hóa tốc độ truy vấn trên tập dữ liệu hàng triệu dòng)
CREATE INDEX IF NOT EXISTS idx_clicks_time_pub_offer ON fact_clicks(click_time, publisher_id, offer_id);
CREATE INDEX IF NOT EXISTS idx_conversions_pub_status ON fact_conversions(publisher_id, status, conversion_time);
CREATE INDEX IF NOT EXISTS idx_conversions_offer ON fact_conversions(offer_id, status);
CREATE INDEX IF NOT EXISTS idx_clicks_ip ON fact_clicks(user_ip);
