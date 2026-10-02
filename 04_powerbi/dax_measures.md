# BỘ CÔNG THỨC DAX CHUẨN CHO POWER BI (AFFILIATE PERFORMANCE & RISK)

Tài liệu này tổng hợp toàn bộ các DAX Measures được tối ưu hóa cho mô hình Star Schema trong dự án **Affiliate Performance & Traffic Risk Intelligence System (AP-TRIS)**.

---

## 1. Volume & Conversion Measures (Đo lường quy mô & Chuyển đổi)

### Total Clicks
```dax
Total Clicks = COUNTROWS('fact_clicks')
```

### Total Conversions (Form nộp / Đơn đặt hàng)
```dax
Total Conversions = COUNTROWS('fact_conversions')
```

### Approved Conversions (Đơn được phê duyệt thành công)
```dax
Approved Conversions = 
CALCULATE(
    COUNTROWS('fact_conversions'),
    'fact_conversions'[status] = "Approved"
)
```

### Rejected Conversions (Đơn bị từ chối / Thẩm định rớt)
```dax
Rejected Conversions = 
CALCULATE(
    COUNTROWS('fact_conversions'),
    'fact_conversions'[status] IN {"Rejected", "Fraud"}
)
```

### Conversion Rate (CR %) - Tỷ lệ chuyển đổi Click sang Đơn
```dax
CR % = 
DIVIDE(
    [Total Conversions],
    [Total Clicks],
    0
)
```

### Approval Rate (%) - Tỷ lệ duyệt hồ sơ thành công
```dax
Approval Rate % = 
DIVIDE(
    [Approved Conversions],
    [Total Conversions],
    0
)
```

---

## 2. Financial & Profitability Measures (Doanh thu & Biên lợi nhuận)

### Gross Revenue (VND) - Tổng doanh thu sàn thu từ Advertiser
```dax
Gross Revenue = 
SUM('fact_conversions'[advertiser_revenue_vnd])
```

### Publisher Payout (VND) - Chi phí hoa hồng trả cho đối tác
```dax
Publisher Payout = 
SUM('fact_conversions'[publisher_payout_vnd])
```

### Net Platform Margin (VND) - Lợi nhuận gộp giữ lại của Sàn
```dax
Net Platform Margin = 
[Gross Revenue] - [Publisher Payout]
```

### Gross Margin % - Biên lợi nhuận gộp (%)
```dax
Gross Margin % = 
DIVIDE(
    [Net Platform Margin],
    [Gross Revenue],
    0
)
```

### EPC (Earnings Per Click - VND) - Thu nhập trên mỗi click cho Publisher
```dax
EPC (VND) = 
DIVIDE(
    [Publisher Payout],
    [Total Clicks],
    0
)
```

### Platform Revenue Per Click (RPC - VND)
```dax
Platform RPC = 
DIVIDE(
    [Gross Revenue],
    [Total Clicks],
    0
)
```

---

## 3. Time Intelligence (Tăng trưởng theo thời gian)

### Revenue Last Month (Doanh thu tháng trước)
```dax
Revenue LM = 
CALCULATE(
    [Gross Revenue],
    DATEADD('dim_date'[Date], -1, MONTH)
)
```

### MoM Revenue Growth % (Tăng trưởng doanh thu theo tháng)
```dax
MoM Revenue Growth % = 
VAR _Current = [Gross Revenue]
VAR _Previous = [Revenue LM]
RETURN
DIVIDE(_Current - _Previous, _Previous, 0)
```

---

## 4. Risk & Fraud Detection Measures (Kiểm soát gian lận)

### Bot Suspicion Conversions (Đơn hoàn tất < 5 giây)
```dax
Bot Lead Count = 
CALCULATE(
    COUNTROWS('fact_conversions'),
    'fact_conversions'[time_to_convert_seconds] < 5
)
```

### Bot Traffic Ratio % (Tỷ lệ lead nghi vấn bot)
```dax
Bot Traffic Ratio % = 
DIVIDE(
    [Bot Lead Count],
    [Total Conversions],
    0
)
```

### High Risk Publisher Alert (Cảnh báo Publisher có tỷ lệ duyệt < 15%)
```dax
Publisher Risk Status = 
SWITCH(
    TRUE(),
    [Total Conversions] >= 20 && [Approval Rate %] < 0.15, "🔴 CRITICAL (Block Recommended)",
    [Total Conversions] >= 10 && [Approval Rate %] < 0.25, "🟡 WATCHLIST (Review Traffic)",
    "🟢 NORMAL"
)
```
