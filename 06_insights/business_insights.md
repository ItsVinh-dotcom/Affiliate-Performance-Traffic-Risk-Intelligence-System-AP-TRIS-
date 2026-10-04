# INSIGHT KINH DOANH & ĐỀ XUẤT HÀNH ĐỘNG

> Số liệu tính từ dataset mô phỏng: 1.000.000 click, 49.006 chuyển đổi, tháng 08–09/2026. Lịch sử publisher 12 tháng dùng cho cohort cũng là dữ liệu mô phỏng. Hiệu ứng trong A/B test là giả định.
>
> Các insight được sắp theo thứ tự câu hỏi mà team traffic và team tối ưu chiến dịch đặt ra cho DA.

---

## 1. "Kênh TikTok có tỷ lệ duyệt thấp, có nên cắt không?" (team traffic)

**Phát hiện**

| Kênh | Tỷ lệ duyệt (toàn bộ) | Tỷ lệ duyệt (đã loại gian lận) |
|---|---|---|
| TikTok Creator | 60,0% | 70,7% |
| SEO Content Hub | 53,3% | 69,0% |
| Google Ads Specialist | 60,8% | 69,5% |
| Facebook Media Buyer | 70,2% | 70,2% |
| Telegram/Zalo Community | 70,2% | 70,2% |
| YouTube Reviewer | 69,4% | 69,4% |

- Tỷ lệ duyệt thấp của TikTok đến từ **một publisher gian lận** (`PUB_042`). SEO thấp vì có 3 publisher gian lận.
- Sau khi loại nhóm gian lận, các kênh đều đạt khoảng 69–71%.

**Đề xuất**

- **Không cắt kênh TikTok.**
- Mọi báo cáo so sánh kênh hoặc publisher cần có thêm phiên bản đã loại traffic bị gắn cờ.

---

## 2. "Ngân hàng phàn nàn lead rác, nguồn từ đâu?" (team tối ưu chiến dịch)

**Phát hiện**

- Có 5 publisher (`PUB_042`, `PUB_077`, `PUB_091`, `PUB_142`, `PUB_188`), chiếm ~12% click và 12% đơn (5.935 đơn).
- **Time-to-convert** chỉ 1–3 giây, trong khi người dùng thật có trung vị khoảng 22 phút.
- **IP:** toàn bộ dồn về 6 địa chỉ thuộc dải `113.161.44.x`.
- **Tỷ lệ duyệt** chỉ ~4–6%, so với 61,8% trung bình sàn.
- **Tiền mất:** vẫn có **269 đơn lọt duyệt**, tương đương **41,8 triệu VNĐ** hoa hồng trả sai.

**Đề xuất**

- Tự động **tạm giữ thanh toán (hold payout)** cho đơn có `time_to_convert < 5 giây`.
- Audit publisher có ≥ 20 đơn và tỷ lệ duyệt < 15%. Nếu lặp lại 2 kỳ liên tiếp thì hạ hạng hoặc khóa tài khoản.

---

## 3. "Mảng nào đang mang lại lợi nhuận?" (cả hai team)

| Ngành hàng | % Click | % Doanh thu | % Lợi nhuận gộp |
|---|---|---|---|
| Finance & Banking | 40,0% | 44,2% | 42,5% |
| Health & Wellness | 15,9% | 23,9% | 24,2% |
| Beauty & Cosmetics | 12,0% | 18,1% | 18,4% |
| E-commerce | 16,0% | 8,1% | 8,7% |
| Mobile Apps | 12,0% | 4,4% | 4,7% |
| Education | 4,0% | 1,3% | 1,5% |

**Đề xuất:** ưu tiên nguồn lực account management cho các đối tác ngân hàng. Offer mang lãi nhiều nhất là VIB Financial Super Card (122,7 triệu VNĐ).

---

## 4. "Số đơn duyệt có khớp với số ngân hàng xác nhận không?" (đối soát cuối tháng)

- Tháng 09/2026: sau khi tách riêng các đơn pending đã được ngân hàng chốt, chênh lệch không giải thích được là **−2,1%** (−60 triệu VNĐ).
- **Nguyên nhân lớn nhất:** đơn thiếu ở phía advertiser (mất postback) và đơn lệch trạng thái.

**Đề xuất:**

- Gửi danh sách `click_id` lệch cho từng advertiser.
- Escalate các advertiser lệch > 3%.
- Chỉ trả hoa hồng cho publisher trên các đơn đã được advertiser xác nhận.

---

## 5. "Có nên đổi sang hoa hồng bậc thang để kéo volume?" (team traffic) → A/B test

- **Thiết kế:** chia nhóm theo publisher, ghép cặp publisher có quy mô tương đương. A/A test trên dữ liệu thật cho thấy hai nhóm cân bằng (p = 0,72).
- **Kết quả** (hiệu ứng là giả định): volume **+14%** và có ý nghĩa thống kê (p < 0,001). Lãi của sàn cũng +14% nhưng **không có ý nghĩa thống kê** (p = 0,13).

**Đề xuất:** chưa triển khai. Chạy test lâu hơn hoặc dùng CUPED, và quyết định dựa trên lãi chứ không dựa trên volume.

---

## 6. "Nên tuyển publisher từ kênh nào?" (team phát triển publisher) → Cohort

**Phát hiện**

- **Facebook Media Buyer** kích hoạt nhanh nhất (83%) nhưng LTV-3 thấp nhất: 1,85 triệu VNĐ / publisher đăng ký.
- **SEO** có LTV-3 cao nhất: 4,26 triệu VNĐ, gấp khoảng 2,3 lần Facebook.
- Khoảng **24%** publisher đăng ký nhưng không bao giờ kích hoạt. Trong số đã kích hoạt, chỉ khoảng 65% còn hoạt động ở M+3.
- **Cohort 12/2025** có retention cao bất thường. Lý do là cohort này có 40% publisher managed, so với khoảng 20% ở các cohort khác. Khác biệt đến từ cơ cấu cohort, không phải từ tháng đăng ký.

**Đề xuất**

- Đánh giá kênh tuyển publisher bằng LTV, không bằng số đăng ký.
- Đầu tư vào onboarding 30 ngày đầu.
