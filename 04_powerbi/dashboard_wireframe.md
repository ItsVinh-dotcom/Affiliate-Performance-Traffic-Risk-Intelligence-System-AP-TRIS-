# BỐ CỤC DASHBOARD POWER BI

File: `04_powerbi/dashboard_main.pbip`. Khổ trang 1280 × 720. Có 3 trang, đi theo mạch câu chuyện của dự án:

1. Tổng quan.
2. Tìm dấu hiệu bất thường theo kênh.
3. Điều tra rủi ro.

Mọi trang đều có thanh tiêu đề và bộ lọc thời gian. Bộ lọc dùng bảng `dim_date`, theo giờ Việt Nam.

> Số liệu trong ngoặc là kết quả khi chưa lọc gì, đã đối chiếu với SQL/Python.

---

## Trang 1 – Tổng quan (Executive Overview)

**Người xem:** quản lý, cả team traffic và team chiến dịch.

**Bộ lọc:** thời gian · ngành hàng · kênh traffic.

**Hàng thẻ KPI:**

| Thẻ | Measure | Giá trị |
|---|---|---|
| Doanh thu (tỷ VNĐ) | `Revenue (bn VND)` | 5,89 |
| Lãi gộp (tỷ VNĐ) | `Margin (bn VND)` | 1,67 |
| Margin % | `Gross Margin %` | 28,4% |
| Đơn được duyệt | `Approved Conversions` | 30.292 |
| Tỷ lệ duyệt | `Approval Rate %` | 61,8% |
| EPC (VNĐ/click) | `EPC (VND)` | ~4.219 |

**Biểu đồ:**

- **Đường:** doanh thu và lãi gộp theo ngày, đơn vị triệu VNĐ.
- **Thanh ngang:** doanh thu và lãi gộp theo ngành hàng, đơn vị tỷ VNĐ. Ngân hàng – Tài chính dẫn đầu.
- **Thanh ngang:** xếp hạng 25 offer theo lãi gộp. Dẫn đầu là VIB Financial Super Card.

---

## Trang 2 – Chiến dịch & Kênh (Campaign & Traffic)

**Người xem:** team traffic và team tối ưu chiến dịch.

**Bộ lọc:** thời gian · ngành hàng · hạng publisher.

**Biểu đồ:**

- **Thanh ngang "Tỷ lệ duyệt theo kênh: trước & sau khi loại traffic gian lận"** (dùng `Approval Rate %` và `Approval Rate % (excl. Flagged)`). Đây là biểu đồ mở đầu phần điều tra: TikTok 60,0% → 70,7%, SEO 53,3% → 69,0% sau khi loại gian lận.
- **Phân tán theo offer:** trục X là tỷ lệ duyệt, trục Y là lãi gộp, kích thước bong bóng là số đơn duyệt, màu theo ngành hàng.
- **Bảng chi tiết offer:** click, đơn, CR, đơn duyệt, tỷ lệ duyệt, doanh thu, lãi gộp, margin %, EPC. Sắp xếp theo lãi gộp giảm dần.

---

## Trang 3 – Rủi ro gian lận (Traffic Quality & Risk)

**Người xem:** team chiến dịch, kế toán, người phụ trách kiểm soát rủi ro.

**Bộ lọc:** thời gian · kênh traffic.

**Thẻ cảnh báo:**

| Thẻ | Measure | Giá trị |
|---|---|---|
| Lead nghi bot (< 5 giây) | `Bot Lead Count` | 5.935 |
| Tỷ lệ lead nghi bot | `Bot Traffic Ratio %` | 12,1% |
| Publisher bị gắn cờ | `Flagged Publishers` | 5 |
| Hoa hồng trả sai (tr VNĐ) | `Leaked Payout (M VND)` | 41,8 |

**Biểu đồ:**

- **Cột "Phân phối thời gian từ click đến điền form":** chia 6 nhóm, từ < 5 giây đến > 30 phút. Nhóm < 5 giây nhô cao bất thường.
- **Thanh ngang "Lý do bị từ chối / gắn cờ":** số đơn bị từ chối theo từng lý do.
- **Bảng chấm điểm rủi ro publisher:** publisher, kênh, hạng, số đơn, tỷ lệ duyệt, số lead < 5 giây, tiền trả sai, đánh giá rủi ro (`Publisher Risk Status`). Sắp xếp theo số lead nghi bot giảm dần, nên 5 publisher gian lận nằm ở đầu bảng.
