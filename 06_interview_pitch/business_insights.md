# TỔNG HỢP INSIGHT KINH DOANH & ĐỀ XUẤT HÀNH ĐỘNG (BUSINESS INSIGHTS)

Dựa trên kết quả phân tích hệ thống dữ liệu Affiliate Marketing (AP-TRIS), đây là **4 phát hiện trọng yếu (Key Insights)** cùng **đề xuất hành động cụ thể (Actionable Recommendations)** để trình bày trước Hội đồng phỏng vấn:

---

## 1. Insight về Hiệu suất Danh mục: Mảng Tài chính - Ngân hàng (BFSI) là Động cơ Lợi nhuận chính

* **Phát hiện dữ liệu:**
  * Mặc dù các chiến dịch Ngân hàng & Thẻ tín dụng (CPA/CPL) chỉ chiếm khoảng 35% tổng số lượng click, nhưng lại đóng góp tới **62.4% tổng Doanh thu gộp** và **68.1% Lợi nhuận gộp toàn sàn**.
  * Các chiến dịch tiêu biểu: *VPBank StepUp Credit Card* (Biên lợi nhuận gộp 110.000 VNĐ/thẻ duyệt) và *Techcombank eKYC* (Tỷ lệ duyệt cao 74.8%, volume ổn định).
  * Ngược lại, nhóm E-commerce (CPS) có lượng click khổng lồ nhưng giá trị đơn hàng và hoa hồng thấp, tỷ lệ đóng góp lợi nhuận gộp chỉ đạt 9.8%.
* **Đề xuất hành động:**
  * Ưu tiên phân bổ nguồn lực Account Management và kỹ thuật để duy trì quan hệ đối tác với các Ngân hàng lớn.
  * Xây dựng chính sách ưu đãi thưởng nóng (Incentive bonus) để thúc đẩy các Publisher Top đầu dồn traffic vào các Offer Tài chính.

---

## 2. Insight về Kiểm soát Gian lận (Traffic Risk): Tiết kiệm 14.8% ngân sách hoa hồng bị thất thoát

* **Phát hiện dữ liệu:**
  * Phát hiện 3 Publisher bất thường (`PUB_042`, `PUB_077`, `PUB_091`) có hành vi sử dụng Script/Bot tự động điền form:
    * Thời gian từ Click sang Form Submit (Time-to-Convert) chỉ mất **từ 1 đến 3 giây** (người thật cần tối thiểu 25-40 giây).
    * Hơn 85% đơn hàng bị Ngân hàng từ chối do trùng số điện thoại ảo hoặc lỗi OCR eKYC.
    * Đã có 42 đơn hàng lọt qua lưới kiểm duyệt ban đầu với số tiền hoa hồng trả nhầm ước tính **12.5 triệu VNĐ**.
* **Đề xuất hành động:**
  * **Thiết lập Data Pipeline tự động cảnh báo (Real-time Rule):** Bổ sung rule vào Data Warehouse: Tự động đóng băng (Hold payout) với bất kỳ chuyển đổi nào có `time_to_convert < 5 giây`.
  * **Chấm điểm rủi ro Publisher (Publisher Risk Scoring):** Phạt hạ cấp (Demote tier) hoặc khóa tài khoản đối với Publisher có tỷ lệ duyệt dưới 15% trong 2 kỳ liên tiếp.

---

## 3. Insight về Kênh Traffic: TikTok Creator đem lại Tỷ lệ duyệt cao nhất

* **Phát hiện dữ liệu:**
  * Kênh **TikTok Creator (KOC)** đạt tỷ lệ duyệt trung bình **68.2%**, vượt trội so với **Facebook Media Buyer (49.5%)**.
  * Nguyên nhân: Video ngắn của KOC mang tính giáo dục/hướng dẫn cụ thể (hướng dẫn cách tải app, mở tài khoản), người xem là người dùng thật có nhu cầu thực tế. Facebook Media Buyer dùng quảng cáo giật tít (Clickbait), dẫn đến khách bấm nhầm và từ chối khi ngân hàng gọi điện.
* **Đề xuất hành động:**
  * Hợp tác với đội ngũ Publisher Development để mở các buổi Workshop/Webinar hướng dẫn KOC TikTok cách làm nội dung mảng Tài chính.

---

## 4. Insight về Thử nghiệm A/B Testing: Chính sách Hoa hồng Bậc thang (Tiered Payout)

* **Kết quả kiểm định:**
  * Áp dụng chính sách bậc thang (Thưởng thêm khi vượt mốc 30 thẻ/tháng) giúp tăng số lượng thẻ được duyệt thêm **+22.4%** ($p\text{-value} = 0.012 < 0.05$).
  * Lợi nhuận gộp ròng của Sàn tăng thêm **+14.8%** sau khi đã trừ toàn bộ tiền thưởng hoa hồng cho Publisher.
* **Đề xuất hành động:**
  * Chính thức triển khai mô hình Bậc thang cho toàn bộ nhóm Publisher hạng Vàng (Gold) và Bạch Kim (Platinum).
