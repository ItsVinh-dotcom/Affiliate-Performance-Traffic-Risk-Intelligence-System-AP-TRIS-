# TỔNG HỢP INSIGHT KINH DOANH & ĐỀ XUẤT HÀNH ĐỘNG

> Mọi số liệu dưới đây được tính từ dataset mô phỏng (1.000.000 click, 49.006 chuyển đổi, tháng 08–09/2026). Riêng mục 4 (A/B test) là một case mô phỏng riêng, có số liệu giả định.

---

## 1. Ngân hàng – Tài chính (BFSI) là mảng đóng góp lợi nhuận lớn nhất

**Phát hiện**

| Ngành hàng | % Click | % Doanh thu | % Lợi nhuận gộp |
|---|---|---|---|
| Finance & Banking | 40,0% | 44,2% | 42,5% |
| Health & Wellness | 15,9% | 23,9% | 24,2% |
| Beauty & Cosmetics | 12,0% | 18,1% | 18,4% |
| E-commerce | 16,0% | 8,1% | 8,7% |
| Mobile Apps | 12,0% | 4,4% | 4,7% |
| Education | 4,0% | 1,3% | 1,5% |

- Offer mang lãi nhiều nhất là **VIB Financial Super Card** (122,7 triệu VNĐ lãi gộp), tiếp theo là Cordyceps Natural Tonic và **VPBank StepUp** (lãi 110.000 VNĐ mỗi thẻ được duyệt).
- E-commerce chiếm 16% click nhưng chỉ đóng góp 8,7% lợi nhuận, do hoa hồng mỗi đơn thấp (45.000–90.000 VNĐ).

**Đề xuất**

- Ưu tiên nguồn lực account management cho các đối tác ngân hàng.
- Có cơ chế thưởng để publisher top đầu chuyển thêm traffic sang offer tài chính.

---

## 2. Kiểm soát gian lận: 41,8 triệu VNĐ hoa hồng trả sai

**Phát hiện**

- Có 5 publisher bất thường: `PUB_042`, `PUB_077`, `PUB_091`, `PUB_142`, `PUB_188`. Nhóm này chiếm ~12% click và 12% đơn (5.935 đơn).
- **Time-to-convert:** nhóm này điền form trong 1–3 giây, trong khi người dùng thật có trung vị khoảng 22 phút.
- **Cụm IP:** toàn bộ traffic của nhóm đến từ 6 IP thuộc dải `113.161.44.x`.
- **Tỷ lệ duyệt** chỉ khoảng 4–6%, so với 61,8% trung bình sàn. Phần lớn đơn bị từ chối vì trùng số điện thoại, lỗi eKYC/OCR hoặc bị đánh dấu bot.
- Dù vậy, vẫn có **269 đơn lọt duyệt**, khiến sàn trả sai **41,8 triệu VNĐ** hoa hồng.

**Đề xuất**

- Tự động **tạm giữ thanh toán (hold payout)** cho mọi đơn có `time_to_convert < 5 giây`. File kế toán hiện đã chuyển 5 publisher này sang trạng thái `HOLD`.
- Đưa vào audit các publisher có ≥ 20 đơn và tỷ lệ duyệt < 15%. Nếu tình trạng lặp lại 2 kỳ liên tiếp thì hạ hạng hoặc khóa tài khoản.

---

## 3. So sánh kênh traffic: phải loại nhiễu gian lận trước

**Phát hiện**

| Kênh | Tỷ lệ duyệt (toàn bộ) | Tỷ lệ duyệt (đã loại gian lận) |
|---|---|---|
| TikTok Creator | 60,0% | 70,7% |
| SEO Content Hub | 53,3% | 69,0% |
| Google Ads Specialist | 60,8% | 69,5% |
| Facebook Media Buyer | 70,2% | 70,2% |
| Telegram/Zalo Community | 70,2% | 70,2% |
| YouTube Reviewer | 69,4% | 69,4% |

- Nhìn số thô, TikTok và SEO trông như kênh kém. Nguyên nhân thực sự là các kênh này có publisher gian lận: TikTok có 1, SEO có 3, Google Ads có 1.
- Sau khi loại nhóm gian lận, các kênh không khác biệt đáng kể (69–71%).

**Bài học / Đề xuất**

- Mọi báo cáo so sánh kênh hoặc publisher nên có thêm một phiên bản đã loại traffic bị gắn cờ, để tránh ra quyết định sai về phân bổ ngân sách.

---

## 4. A/B test chính sách hoa hồng bậc thang (case mô phỏng)

**Kết quả**

- Tỷ lệ thẻ được duyệt trên mỗi click: nhóm A 3,04%, nhóm B 3,96%. Mức tăng tương đối **+30,4%**, Z = 2,57, **p ≈ 0,010**.
- Lợi nhuận gộp của sàn tăng **+11,9%** sau khi trừ tiền thưởng.

**Hạn chế & đề xuất**

- Thử nghiệm đang chia nhóm theo click. Khi làm thật cần chia nhóm theo publisher, vì chính sách hoa hồng áp dụng cho từng publisher.
- Nên chạy thử (pilot) với nhóm publisher hạng Gold và Platinum trước khi triển khai rộng.
