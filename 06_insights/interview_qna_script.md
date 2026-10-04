# THUYẾT TRÌNH DỰ ÁN & CÂU HỎI THƯỜNG GẶP

Vị trí hướng tới: **Data Analyst / Performance Analyst** tại mạng affiliate.

---

## PHẦN 1: TRÌNH BÀY DỰ ÁN THEO STAR (3–5 PHÚT)

### 1. Situation (Bối cảnh)
> "Dự án này em tự xây dựng để mô phỏng bài toán của một mạng affiliate. Dữ liệu là **giả lập**: em viết script Python sinh 1 triệu click và khoảng 49 nghìn chuyển đổi trong 2 tháng, theo đúng logic nghiệp vụ, trong đó có cài sẵn một nhóm publisher gian lận để kiểm chứng phương pháp phát hiện.
> Mạng affiliate đứng giữa hai bên: publisher muốn nhiều click và hoa hồng, còn ngân hàng chỉ trả tiền cho hồ sơ được duyệt. Nếu traffic bẩn lọt qua, sàn mất tiền hoa hồng và mất uy tín với đối tác."

### 2. Task (Nhiệm vụ)
> "Em đặt ra 3 mục tiêu:
> 1. Chuẩn hóa dữ liệu click, chuyển đổi, doanh thu và hoa hồng theo mô hình star schema.
> 2. Đo các KPI cốt lõi (CR, Approval Rate, EPC, Margin) theo offer, publisher và kênh.
> 3. Xây dựng các rule phát hiện publisher gian lận và ước tính số tiền bị thất thoát."

### 3. Action (Việc đã làm)
> "- **Mô hình dữ liệu & SQL:** 2 bảng fact (clicks, conversions) và 2 bảng dim (publishers, offers). Dùng CTE và window function (`DENSE_RANK`, `SUM() OVER()`) để xếp hạng publisher theo lợi nhuận và tỷ trọng đóng góp.
> - **Phát hiện gian lận:** 3 rule
>   - Time-to-convert < 5 giây.
>   - Từ 3 đơn trở lên đến từ cùng 1 IP trong 1 ngày.
>   - Tỷ lệ duyệt < 15% khi có từ 20 đơn trở lên.
> - **Pipeline Python:** kiểm tra chất lượng dữ liệu (khóa chính, margin âm, thời gian âm), tổng hợp KPI theo ngày và in cảnh báo rủi ro.
> - **Power BI:** dashboard 3 trang (Tổng quan, Chiến dịch, Rủi ro)."

### 4. Result (Kết quả)
> "- Cả 3 rule cùng chỉ ra **5 publisher**. Họ điền form trong 1–3 giây, traffic dồn về 6 IP, tỷ lệ duyệt chỉ khoảng 5%. Vẫn có **269 đơn lọt duyệt, tương ứng 41,8 triệu VNĐ** hoa hồng trả sai. Em đề xuất tự động tạm giữ thanh toán (hold payout) với các đơn dưới 5 giây.
> - Ngân hàng – Tài chính là mảng đóng góp lợi nhuận lớn nhất (**42,5% lợi nhuận gộp**).
> - Khi so sánh kênh, em nhận ra phải loại traffic gian lận trước: số thô cho thấy TikTok có tỷ lệ duyệt thấp, nhưng nguyên nhân là một publisher gian lận trong kênh này."

---

## PHẦN 2: CÂU HỎI THƯỜNG GẶP

### 1. Tại sao dùng star schema thay vì một bảng phẳng?
> "Bảng clicks rất lớn còn bảng dimension rất nhỏ. Tách riêng thì không phải lặp lại tên publisher, tên offer trên 1 triệu dòng, Power BI lọc theo quan hệ 1-nhiều nhanh hơn, và dễ bổ sung nguồn dữ liệu mới mà không phá vỡ cấu trúc."

### 2. Approval Rate tụt, team Traffic và team Account Manager đổ lỗi cho nhau, em xử lý thế nào?
> "Em dùng dữ liệu để khoanh vùng nguyên nhân:
> 1. **Tụt đều ở mọi publisher:** khả năng cao là phía advertiser, ví dụ ngân hàng siết điều kiện duyệt hoặc cổng eKYC bị lỗi.
> 2. **Chỉ tụt ở vài publisher:** em kiểm tra time-to-convert, IP và lý do bị từ chối của các publisher đó.
> 3. Sau đó đưa cùng một báo cáo cho cả hai bên để thống nhất hướng xử lý."

### 3. EPC là gì, tại sao publisher quan tâm?
> "EPC là hoa hồng trung bình mỗi click. Media buyer phải trả tiền cho mỗi click (CPC). Nếu EPC cao hơn CPC thì họ có lãi và sẽ tiếp tục đổ traffic về sàn. Trong dữ liệu của em, EPC toàn sàn khoảng 4.200 VNĐ/click."

### 4. Làm sao phân biệt traffic viral tự nhiên với bot?
> "Em nhìn vào 3 dấu hiệu:
> 1. **Phân phối time-to-convert:** người thật có phân phối rộng, từ vài chục giây đến vài chục phút. Bot dồn thành một đỉnh nhọn ở 1–3 giây.
> 2. **IP và thiết bị:** traffic thật đa dạng về IP và thiết bị. Bot dồn về vài IP, thường là IP datacenter.
> 3. **Chất lượng sau chuyển đổi:** traffic thật có tỷ lệ duyệt gần mức trung bình ngành. Bot gần như bị từ chối toàn bộ."

### 5. Rule < 5 giây có bắt nhầm người thật không?
> "Có thể, ví dụ người dùng có tính năng autofill. Vì vậy rule này chỉ dùng để tạm giữ thanh toán, không khóa tài khoản ngay. Publisher phải bị cả 3 rule cùng bắt thì mới đưa vào audit."

### 6. A/B test hoa hồng bậc thang có đáng tin không?
> "Đây là case mô phỏng với số liệu giả định. Kết quả là tỷ lệ thẻ được duyệt trên mỗi click tăng 30%, p ≈ 0,01, lợi nhuận gộp tăng 11,9%. Hạn chế lớn nhất: chính sách áp dụng theo publisher nhưng thử nghiệm lại chia nhóm theo click. Khi làm thật cần chia nhóm theo publisher và chạy lâu hơn."

### 7. Nếu làm tiếp, em sẽ cải thiện gì?
> "Em sẽ làm 3 việc:
> - Gộp các rule thành một risk score có trọng số.
> - Cho pipeline chạy theo lịch, chỉ xử lý phần dữ liệu mới (incremental), và gửi cảnh báo qua email hoặc Slack.
> - Bổ sung dữ liệu user-agent và thiết bị để phát hiện các loại bot tinh vi hơn."
