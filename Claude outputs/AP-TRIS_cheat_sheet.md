# AP-TRIS — Cheat sheet phỏng vấn (DA mạng affiliate)

> Đọc phần 1 và 2 trước. Phần 3 và 4 đọc nếu còn thời gian.
> Mọi con số dưới đây mình đã tính lại trực tiếp từ data trong repo.

---

## 1. Câu mở đầu (bắt buộc nói)

"Dự án này em tự xây dựng để luyện tư duy phân tích cho mảng affiliate. **Dữ liệu là giả lập**: em viết script Python sinh 1 triệu click theo đúng nghiệp vụ của một mạng affiliate, có cài sẵn một nhóm publisher gian lận. Sau đó em đóng vai DA để tìm ra chúng bằng SQL và dựng dashboard Power BI."

Vì sao nên nói vậy: interviewer ở mạng affiliate sẽ nhận ra ngay data không thật. Bạn chủ động nói trước thì đó là điểm cộng; để họ tự phát hiện thì thành điểm trừ.

---

## 2. Mười con số cần thuộc

| # | Chỉ số | Giá trị |
|---|---|---|
| 1 | Quy mô | **1.000.000 click · 49.006 chuyển đổi** · 250 publisher · 25 offer · 6 kênh · **2 tháng** (8–9/2026) |
| 2 | CR (click → đơn) | **4,9%** |
| 3 | Approval Rate (tỷ lệ duyệt) | **61,8%** toàn sàn · **69,7%** nếu loại publisher gian lận |
| 4 | Doanh thu / Hoa hồng / Lãi gộp | **5,89 tỷ / 4,22 tỷ / 1,67 tỷ VNĐ** |
| 5 | Margin % | **28,4%** (mỗi offer dao động 26–33%) |
| 6 | EPC | **~4.200 VNĐ/click** |
| 7 | Ngân hàng – Tài chính (BFSI) | 40% click → **44% doanh thu, 42,5% lãi gộp** (mảng lớn nhất) |
| 8 | Publisher gian lận | **5 publisher**, chiếm 12% click và 12% đơn (5.935 đơn) |
| 9 | Dấu hiệu bot | Điền form trong **1–3 giây** (người thật: trung vị ~22 phút) · dồn về **6 IP** cùng dải 113.161.44.x · tỷ lệ duyệt chỉ **~4–6%** |
| 10 | Tiền bị thất thoát | **269 đơn bot vẫn lọt duyệt → 41,8 triệu VNĐ** hoa hồng trả sai. File kế toán đã chuyển 5 publisher này sang trạng thái **HOLD** |

---

## 3. Pitch 3 phút (kể theo STAR)

**Situation (bối cảnh).** Mạng affiliate đứng giữa hai bên. Publisher muốn nhiều click và hoa hồng cao. Ngân hàng chỉ trả tiền cho hồ sơ được duyệt. Nếu traffic bẩn lọt qua, sàn mất tiền hoa hồng và mất uy tín với advertiser.

**Task (nhiệm vụ).** Xây hệ thống đo hiệu quả (CR, Approval Rate, EPC, margin) và phát hiện publisher gian lận sớm.

**Action (việc đã làm).**
1. Thiết kế **star schema**: 2 bảng fact (clicks, conversions) và 2 bảng dim (publishers, offers).
2. Viết SQL với **CTE và window function** (`DENSE_RANK`, `SUM() OVER()`) để xếp hạng publisher theo lợi nhuận và tỷ trọng đóng góp.
3. Viết **3 rule bắt gian lận** bằng SQL:
   - Time-to-convert dưới 5 giây.
   - Một IP sinh từ 3 đơn trở lên trong ngày.
   - Tỷ lệ duyệt dưới 15% khi có từ 20 đơn trở lên.
4. Viết **script Python ETL** kiểm tra chất lượng dữ liệu (khóa chính, margin âm, thời gian âm) và in cảnh báo.
5. Dựng **dashboard Power BI 3 trang**: Tổng quan, Chiến dịch, Rủi ro.

**Result (kết quả).**
- Cả 3 rule cùng chỉ ra đúng 5 publisher.
- Phát hiện **41,8 triệu VNĐ** đã trả sai cho 269 đơn bot lọt duyệt. Đề xuất: tạm giữ thanh toán (hold payout) tự động với mọi đơn có time-to-convert dưới 5 giây.
- BFSI là mảng mang lại nhiều lãi nhất (42,5%), nên ưu tiên nguồn lực account management cho các ngân hàng.

---

## 4. Câu hỏi bẫy hay gặp ở mạng affiliate

**"Kênh nào tốt nhất, TikTok hay Facebook?"**
→ "Ban đầu em thấy TikTok có tỷ lệ duyệt thấp hơn (60% so với 70%). Đào sâu thì nguyên nhân là một publisher gian lận thuộc nhóm TikTok kéo trung bình xuống. Loại nhóm gian lận ra thì các kênh đều khoảng 69–71%. Bài học của em là phải tách nhiễu gian lận trước rồi mới so sánh kênh." *(Câu trả lời này cho thấy tư duy phân tích, nên dùng.)*

**"A/B test hoa hồng bậc thang thì sao?"**
→ "Đây là case mô phỏng với số liệu em tự giả định, không lấy từ dataset. Nhóm B (bậc thang) có tỷ lệ thẻ được duyệt trên mỗi click là 3,96%, nhóm A là 3,04%. Z = 2,57, p ≈ 0,01. Lãi gộp của sàn tăng 11,9%. Hạn chế: em chia nhóm theo click, trong khi chính sách hoa hồng áp dụng theo publisher. Làm thật thì phải chia nhóm theo publisher, và vì số publisher ít hơn nhiều nên cần chạy test lâu hơn."

**"Rule dưới 5 giây có bắt nhầm người thật không?"**
→ "Có thể bắt nhầm, ví dụ người dùng có tính năng autofill. Vì vậy rule chỉ để tạm giữ thanh toán (hold), không khóa tài khoản ngay. Em kết hợp thêm IP cụm và tỷ lệ duyệt; một publisher bị cả 3 rule bắt thì mới đưa vào audit."

**"Sao lại dùng star schema?"**
→ "Bảng clicks rất lớn còn bảng dim rất nhỏ. Tách ra thì không phải lặp lại tên publisher, tên offer trên 1 triệu dòng, Power BI lọc theo quan hệ 1-nhiều nhanh hơn, và dễ thêm nguồn dữ liệu mới."

**"EPC là gì, tại sao publisher quan tâm?"**
→ "EPC là hoa hồng trung bình trên mỗi click. Media buyer phải trả tiền cho mỗi click (CPC). Nếu EPC cao hơn CPC thì họ có lãi và sẽ tiếp tục đổ traffic về sàn."

**"Cohort retention publisher?"**
→ "Em có viết query cohort, nhưng dữ liệu chỉ có 2 tháng nên kết quả chưa có ý nghĩa. Đây là hướng phát triển nếu có thêm dữ liệu."

**"Nếu được làm tiếp, em sẽ làm gì?"**
→ "Có 3 việc:
- Chuyển các rule thành điểm rủi ro (risk score) có trọng số.
- Chạy pipeline theo lịch, xử lý dữ liệu mới theo từng ngày (incremental) và gửi cảnh báo qua Slack hoặc email.
- Thu thập thêm dữ liệu user-agent và thiết bị để bắt được bot tinh vi hơn."

---

## 5. KHÔNG được nói (README cũ ghi sai)

- ~~"BFSI chiếm 68% lợi nhuận"~~ → số đúng là 42,5%
- ~~"TikTok duyệt 68,2% so với Facebook 49,5%"~~ → sai
- ~~"3 publisher bot, 12,5 triệu"~~ → số đúng là 5 publisher, 41,8 triệu
- ~~"Tăng 22,4% thẻ duyệt, lãi tăng 14,8%"~~ → số đúng là +30,4% và +11,9% (và đây là số mô phỏng)
- ~~"Lưu bằng Parquet, giảm 89%, nhanh gấp 10 lần"~~ → thực tế là CSV nén gzip (74,6MB giải nén xuống 16,6MB)
- ~~LEAD/LAG, Chi-Square, t-test, dbt~~ → code không dùng các thứ này
- ~~Số liệu thật của MOSAIC/AccessTrade~~ → dữ liệu giả lập
