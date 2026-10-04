# DAX MEASURES – AP-TRIS

Danh sách này khớp với bảng `_Measures` trong `dashboard_main.SemanticModel` (22 measure).

Mô hình: star schema gồm `fact_clicks`, `fact_conversions`, `dim_publishers`, `dim_offers`, `dim_date`. Bảng `dim_date` được dựng trong Power Query (01/08–30/09/2026) và nối với cả 2 bảng fact qua cột ngày đã quy đổi sang giờ Việt Nam.

---

## 1. Volume & chuyển đổi

### Total Clicks

```dax
Total Clicks = COUNTROWS('fact_clicks')
```

### Total Conversions

```dax
Total Conversions = COUNTROWS('fact_conversions')
```

### Approved Conversions

```dax
Approved Conversions = CALCULATE(COUNTROWS('fact_conversions'), 'fact_conversions'[status] = "Approved")
```

### Rejected Conversions

```dax
Rejected Conversions = CALCULATE(COUNTROWS('fact_conversions'), 'fact_conversions'[status] IN {"Rejected", "Fraud"})
```

### CR %

```dax
CR % = DIVIDE([Total Conversions], [Total Clicks], 0)
```

### Approval Rate %

```dax
Approval Rate % = DIVIDE([Approved Conversions], [Total Conversions], 0)
```

---

## 2. Doanh thu & lợi nhuận

### Gross Revenue

```dax
Gross Revenue = SUM('fact_conversions'[advertiser_revenue_vnd])
```

### Publisher Payout

```dax
Publisher Payout = SUM('fact_conversions'[publisher_payout_vnd])
```

### Net Platform Margin

```dax
Net Platform Margin = [Gross Revenue] - [Publisher Payout]
```

### Gross Margin %

```dax
Gross Margin % = DIVIDE([Net Platform Margin], [Gross Revenue], 0)
```

### EPC (VND)

Hoa hồng trung bình publisher nhận trên mỗi click.

```dax
EPC (VND) = DIVIDE([Publisher Payout], [Total Clicks], 0)
```

### Platform RPC

Doanh thu sàn trên mỗi click.

```dax
Platform RPC = DIVIDE([Gross Revenue], [Total Clicks], 0)
```

---

## 3. Measure hiển thị (đổi đơn vị cho thẻ KPI & biểu đồ)

### Revenue (bn VND)

Chia 1 tỷ để thẻ KPI hiển thị gọn (5,89).

```dax
Revenue (bn VND) = DIVIDE([Gross Revenue], 1000000000)
```

### Margin (bn VND)

```dax
Margin (bn VND) = DIVIDE([Net Platform Margin], 1000000000)
```

### Revenue (M VND)

```dax
Revenue (M VND) = DIVIDE([Gross Revenue], 1000000)
```

### Margin (M VND)

```dax
Margin (M VND) = DIVIDE([Net Platform Margin], 1000000)
```

---

## 4. Chất lượng traffic & rủi ro

### Approval Rate % (excl. Flagged)

Tỷ lệ duyệt sau khi loại publisher bị gắn cờ. Dùng ở trang 2 để so sánh kênh trước/sau khi loại gian lận.

```dax
Approval Rate % (excl. Flagged) = CALCULATE([Approval Rate %], KEEPFILTERS('dim_publishers'[status] <> "Flagged"))
```

### Bot Lead Count

```dax
Bot Lead Count = CALCULATE(COUNTROWS('fact_conversions'), 'fact_conversions'[time_to_convert_seconds] < 5)
```

### Bot Traffic Ratio %

```dax
Bot Traffic Ratio % = DIVIDE([Bot Lead Count], [Total Conversions], 0)
```

### Leaked Payout (M VND)

Hoa hồng đã trả cho các đơn điền form < 5 giây (đơn bot lọt duyệt). Kết quả toàn kỳ: 41,8 triệu VNĐ.

```dax
Leaked Payout (M VND) = DIVIDE(CALCULATE([Publisher Payout], 'fact_conversions'[time_to_convert_seconds] < 5), 1000000)
```

### Flagged Publishers

Số publisher có từ 5 lead nghi bot trở lên trong bộ lọc hiện tại. Kết quả toàn kỳ: 5.

```dax
Flagged Publishers = COUNTROWS(FILTER(VALUES('dim_publishers'[publisher_id]), [Bot Lead Count] >= 5))
```

### Publisher Risk Status

Ưu tiên: bot (≥ 5 lead < 5 giây) → tỷ lệ duyệt thấp (≥ 20 đơn, < 15%) → watchlist (≥ 10 đơn, < 25%).

```dax
Publisher Risk Status = SWITCH(TRUE(), [Bot Lead Count] >= 5, "🔴 BOT - Hold payout", [Total Conversions] >= 20 && [Approval Rate %] < 0.15, "🔴 LOW APPROVAL - Audit", [Total Conversions] >= 10 && [Approval Rate %] < 0.25, "🟡 WATCHLIST", "🟢 NORMAL")
```

---

## 5. Chưa triển khai: so sánh theo thời gian

Có thể bổ sung khi dữ liệu dài hơn 2 tháng:

```dax
Revenue LM = CALCULATE([Gross Revenue], DATEADD('dim_date'[Date], -1, MONTH))
MoM Revenue Growth % = DIVIDE([Gross Revenue] - [Revenue LM], [Revenue LM])
```
