# Ảnh chụp dashboard cho README

README chính đã chèn sẵn 6 ảnh Power BI dưới đây. Các biểu đồ không thuộc Power BI (đối soát, A/B test, cohort) do script Python tự sinh và đã có sẵn trong repo. Chỉ cần lưu ảnh vào **thư mục này**, **đúng tên file**, rồi push lên là ảnh tự hiện.

| # | Tên file | Chụp gì | Hiện ở đâu trong README |
|---|---|---|---|
| 1 | `page1_overview.png` | **Toàn bộ trang 1 – Tổng quan** | Đầu README (ảnh bìa) |
| 2 | `page2_campaign_channel.png` | **Toàn bộ trang 2 – Chiến dịch & Kênh** | Mục 2.4 |
| 3 | `page3_risk.png` | **Toàn bộ trang 3 – Rủi ro gian lận** | Mục 2.4 |
| 4 | `zoom_channel_approval.png` | Riêng biểu đồ *"Tỷ lệ duyệt theo kênh: trước & sau khi loại traffic gian lận"* (trang 2) | Mục 3, bước 1 |
| 5 | `zoom_ttc_distribution.png` | Riêng biểu đồ *"Phân phối thời gian từ click đến điền form"* (trang 3) | Mục 3, bước 3 (bên trái) |
| 6 | `zoom_publisher_risk_table.png` | Riêng bảng *"Bảng chấm điểm rủi ro publisher"*, thấy rõ 5 dòng đầu (trang 3) | Mục 3, bước 3 (bên phải) |

## Cách chụp cho đẹp

1. **Xóa hết bộ lọc** trước khi chụp, để số trên ảnh khớp với số trong README:
   - 5,89 tỷ doanh thu.
   - 61,8% tỷ lệ duyệt.
   - 41,8 triệu trả sai.
2. **Ảnh toàn trang (#1–#3):**
   - Bấm **View → Fit to page**.
   - Dùng `Win + Shift + S` chụp đúng vùng trang.
   - Hoặc dùng **File → Export → PDF** rồi cắt từng trang.
3. **Ảnh zoom (#4–#6):**
   - Di chuột vào biểu đồ, bấm biểu tượng **Focus mode** (ô vuông có mũi tên) để phóng to, rồi chụp.
4. **Kích thước:**
   - Nên rộng ≥ 1.600 px.
   - Lưu dạng `.png`.
   - Mỗi file dưới ~1 MB để GitHub tải nhanh.
5. **Kiểm tra trước khi push:** mở README bằng preview của VS Code (`Ctrl + Shift + V`). Ảnh nào chưa có sẽ hiện biểu tượng ảnh lỗi.

> Nếu chưa kịp chụp ảnh nào, xóa dòng `![...](...)` hoặc thẻ `<img>` tương ứng trong README, để GitHub không hiện ảnh lỗi.
