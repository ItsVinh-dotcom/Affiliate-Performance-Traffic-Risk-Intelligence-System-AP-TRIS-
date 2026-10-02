# HƯỚNG DẪN BỐ CỤC DASHBOARD POWER BI (DASHBOARD WIREFRAME & SPECS)

Dự án thiết kế Dashboard gồm **3 trang trực quan** chuẩn mực, phục vụ 3 nhóm đối tượng: Ban Giám Đốc (C-Level), Đội Vận hành Chiến dịch (Campaign Ops), và Đội Kiểm soát Gian lận (Fraud/Risk Unit).

---

## TRANG 1: EXECUTIVE KPI OVERVIEW (Tổng quan Hiệu suất Sàn)

* **Mục tiêu:** Cung cấp cái nhìn tức thời 360 độ về sức khỏe tài chính và lưu lượng chuyển đổi toàn mạng lưới.
* **Bộ lọc (Slicers) trên cùng:**
  * Chọn khoảng thời gian: Date Range Slider (Tháng 8 - Tháng 9/2026)
  * Vertical: Finance & Banking | Beauty CPO | Health CPO | E-commerce
  * Payout Model: CPA | CPL | CPO | CPS
* **Hàng thẻ số KPI (Top KPI Cards):**
  1. **Gross Revenue:** 285.4M VNĐ (Doanh thu gộp từ Advertiser)
  2. **Net Platform Margin:** 82.1M VNĐ (Lợi nhuận gộp của Sàn)
  3. **Average Margin %:** 28.7% (Biên lợi nhuận gộp mục tiêu > 25%)
  4. **Total Approved Leads:** 642 Leads (Tổng đơn duyệt thành công)
  5. **Average Approval Rate:** 57.1% (Tỷ lệ duyệt trung bình)
  6. **Network EPC:** 10,250 VNĐ (Thu nhập trung bình trên mỗi click)
* **Biểu đồ chính:**
  * **Line Chart:** Doanh thu & Lợi nhuận gộp theo từng ngày (Gross Revenue vs Net Margin over Time).
  * **Donut Chart:** Tỷ trọng doanh thu theo ngành hàng (Finance & Banking 62%, CPO 28%, E-commerce 10%).
  * **Bar Chart (Horizontal):** Top 5 Chiến dịch có Lợi nhuận gộp cao nhất (Dẫn đầu: VPBank StepUp, Techcombank eKYC, VIB Super Card).

---

## TRANG 2: CAMPAIGN & TRAFFIC DEEP-DIVE (Phân tích Chiến dịch & Kênh phân phối)

* **Mục tiêu:** Giúp đội Tối ưu Chiến dịch (Campaign Optimizer) biết nên đẩy mạnh ngân sách vào đâu và kênh nào mang lại ROI cao nhất.
* **Biểu đồ:**
  * **Scatter Plot (Biểu đồ phân tán):** Trục X là `Total Clicks`, Trục Y là `Approval Rate %`, Kích thước bong bóng là `Gross Margin`. Giúp nhận diện ngay các chiến dịch "Volume lớn - Duyệt cao" (Ngôi sao) vs "Volume lớn - Duyệt thấp" (Cần điều chỉnh).
  * **Stacked Column Chart:** Hiệu suất theo Kênh Traffic (TikTok vs FB Ads vs Google Ads vs SEO): So sánh Clicks vs Approved Conversions.
  * **Detailed Matrix Table:** Bảng chi tiết từng Offer:
    * Tên Offer | Payout Model | Clicks | Leads | CR % | Approved | Approval Rate % | Payout | Net Margin | EPC

---

## TRANG 3: TRAFFIC QUALITY & RISK INTELLIGENCE (Kiểm soát Rủi ro & Gian lận)

* **Mục tiêu:** Giúp Data Analyst và Risk Team phát hiện hành vi gian lận của Publisher, bảo vệ uy tín với Ngân hàng/Advertiser.
* **Hàng thẻ cảnh báo (Risk Alert Cards):**
  * **Flagged Bot Conversions:** Số lượng đơn nghi vấn bot (< 5s)
  * **High-Risk Publishers:** Số lượng Publisher bị đưa vào danh sách đen/cần audit
  * **Saved Budget (Ngân sách giữ lại nhờ phát hiện gian lận):** Ước tính số tiền hoa hồng ngăn chặn chi trả nhầm
* **Biểu đồ:**
  * **Histogram / Distribution Chart:** Phân phối thời gian Time-to-Convert (Thời gian từ Click đến Form submit). Đỉnh nhọn bất thường ở giây thứ 1-3 phản ánh bot traffic.
  * **Risk Heatmap / Matrix Table:**
    * Publisher ID | Tên | Kênh Traffic | Tổng đơn | Đơn duyệt | Tỷ lệ duyệt % | Đơn < 5s | Đánh giá rủi ro (CRITICAL / NORMAL)
    * Sử dụng Conditional Formatting: Đỏ rực nếu Approval Rate < 15% hoặc Time-to-convert trung bình < 5s.
