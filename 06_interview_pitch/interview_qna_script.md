# KỊCH BẢN THUYẾT TRÌNH PHỎNG VẤN (7 PHÚT) & BỘ CÂU HỎI PHẢN BIỆN

Tài liệu này được biên soạn độc quyền cho buổi phỏng vấn vị trí **Data Analyst / Performance Analyst**.

---

## PHẦN 1: KỊCH BẢN THUYẾT TRÌNH DỰ ÁN (MÔ HÌNH STAR - 5 ĐẾN 7 PHÚT)

### 1. Situation (Bối cảnh) - 1 phút
> *"Xin chào anh/chị, để chuẩn bị cho buổi phỏng vấn hôm nay, em đã chủ động xây dựng một dự án phân tích thực tế mang tên **AP-TRIS (Affiliate Performance & Traffic Risk Intelligence System)**.  
> Em nhận thấy trong một mạng lưới Affiliate Marketing, công ty luôn đứng ở vị trí trung gian giữa hai áp lực: Đội ngũ Publisher luôn muốn tối đa hóa lượt click và hoa hồng, trong khi các Nhà quảng cáo lớn (đặc biệt là khối Ngân hàng và Tài chính) lại đòi hỏi chất lượng lead thực sự và kiểm soát tỷ lệ rớt đơn khắt khe. Nếu không có hệ thống dữ liệu theo dõi theo thời gian thực và phát hiện gian lận, sàn rất dễ bị thất thoát tiền hoa hồng hoặc bị Advertiser phạt hợp đồng."*

### 2. Task (Nhiệm vụ em tự đặt ra) - 1 phút
> *"Nhiệm vụ chính em đặt ra trong dự án này bao gồm 4 mục tiêu:  
> 1. Xây dựng một Data Model dạng Star Schema chuẩn hóa toàn bộ luồng Clicks, Conversions, Payouts và Doanh thu.  
> 2. Thiết kế Dashboard Power BI 3 tầng: Tổng quan điều hành (C-Level), Tối ưu chiến dịch, và Cảnh báo rủi ro gian lận.  
> 3. Viết các truy vấn SQL nâng cao với Window Functions để tự động truy quét các hành vi bất thường như Bot click và Lead ảo.  
> 4. Thực hiện kiểm định giả thuyết thống kê A/B Testing để đánh giá xem chính sách hoa hồng bậc thang có thực sự giúp tăng biên lợi nhuận ròng hay không."*

### 3. Action (Hành động & Kỹ thuật đã áp dụng) - 3 phút
> *"Về mặt kỹ thuật, em đã triển khai cụ thể:  
> * **Về Data Modeling & SQL:** Em xây dựng 2 bảng Fact (Clicks, Conversions) và 2 bảng Dimension (Publishers, Offers) với các Index tối ưu. Em viết các câu truy vấn phức tạp dùng CTE, Window Functions như `DENSE_RANK()`, `LEAD/LAG` và `DATE_TRUNC` để tính toán các chỉ số đặc thù như **EPC, Approval Rate, Gross Margin %**, và phân tích Cohort giữ chân Publisher.  
> * **Về Kiểm soát Gian lận:** Em phát hiện ra một nhóm Publisher có thời gian chuyển đổi từ Click sang Form Submit (`time_to_convert`) chỉ từ 1 đến 3 giây, hoàn toàn bất khả thi với người dùng thật. Em đã viết query phân loại độ rủi ro (Risk Scoring) và tự động lọc ra các dải IP lặp lại.  
> * **Về A/B Testing:** Em sử dụng kiểm định Chi-Square để so sánh tỷ lệ duyệt và Two-sample t-test để so sánh doanh thu trung bình giữa 2 nhóm hoa hồng Cố định vs Bậc thang.  
> * **Về Tự động hóa:** Em viết script Python chạy ETL định kỳ, tự động kiểm tra tính toàn vẹn dữ liệu (Data Quality) và gửi cảnh báo anomaly."*

### 4. Result (Kết quả & Giá trị kinh doanh) - 1.5 phút
> *"Kết quả phân tích đã mang lại các giá trị kinh doanh rõ ràng:  
> 1. Phát hiện và ngăn chặn nguy cơ thất thoát hơn 12.5 triệu VNĐ tiền hoa hồng chi trả nhầm cho các traffic bot.  
> 2. Nhận diện mảng Tài chính - Ngân hàng là "con gà đẻ trứng vàng", chiếm 68% lợi nhuận gộp toàn sàn, từ đó đề xuất tập trung KOC TikTok cho mảng này vì có tỷ lệ duyệt cao nhất (68.2%).  
> 3. Chứng minh chính sách hoa hồng bậc thang giúp tăng 22.4% số lượng thẻ duyệt với độ tin cậy thống kê 95% ($p < 0.05$)."*

---

## PHẦN 2: 5 CÂU HỎI BẪY THƯỜNG GẶP & CÁCH TRẢ LỜI GHI ĐIỂM

### Câu hỏi 1: *"Tại sao em lại chọn mô hình Star Schema thay vì để dữ liệu ở dạng một bảng phẳng (Flat Table / Denormalized)?"*
* **Cách trả lời:**  
  *"Trong môi trường Affiliate, dữ liệu Clicks tăng trưởng cực kỳ nhanh (hàng triệu bản ghi mỗi ngày), trong khi Conversions chỉ chiếm từ 3-8%. Nếu gom tất cả vào một Flat Table, dữ liệu sẽ bị trùng lặp khổng lồ các thông tin Dimension (tên publisher, tên offer, địa chỉ, kênh), gây tốn kém lưu trữ và làm chậm Dashboard Power BI. Mô hình Star Schema tách biệt Fact và Dim giúp tối ưu bộ nhớ, tăng tốc độ truy vấn DAX (dùng quan hệ 1-Nhiều) và giúp kỹ thuật viên dễ dàng bổ sung thêm nguồn dữ liệu mới mà không làm vỡ cấu trúc."*

### Câu hỏi 2: *"Nếu đội Traffic và đội Account Manager cãi nhau về tỷ lệ duyệt (Approval Rate) bị tụt dốc, em sẽ giải quyết thế nào?"*
* **Cách trả lời:**  
  *"Em sẽ không đưa ra kết luận cảm tính mà đi từ dữ liệu theo 3 bước:  
  1. **Kiểm tra yếu tố bên ngoài (Advertiser side):** Kiểm tra xem tỷ lệ duyệt tụt trên toàn bộ các Publisher hay chỉ tụt ở 1 vài người. Nếu tất cả đều tụt, khả năng cao hệ thống ngân hàng bị lỗi cổng eKYC hoặc ngân hàng vừa siết chặt chính sách duyệt hồ sơ.  
  2. **Kiểm tra yếu tố bên trong (Traffic side):** Nếu tỷ lệ tụt chỉ xảy ra ở 1-2 Publisher cụ thể, em dùng SQL kiểm tra `time_to_convert`, dải IP và lý do reject (ví dụ bị báo trùng số, nợ xấu CIC, số rác).  
  3. **Đưa ra giải pháp trung gian:** Cung cấp báo cáo số liệu minh bạch cho cả 2 bên cùng xem để thống nhất hướng xử lý."*

### Câu hỏi 3: *"Chỉ số EPC (Earnings Per Click) có ý nghĩa gì và tại sao Publisher lại quan tâm nhất đến chỉ số này?"*
* **Cách trả lời:**  
  *"Nhiều người mới thường chỉ nhìn vào số tiền hoa hồng cao (ví dụ 400.000đ/thẻ), nhưng đối với các Publisher chuyên nghiệp (như Media Buyer tự bỏ tiền chạy quảng cáo Facebook/Google), họ phải trả tiền cho mỗi lượt click (CPC). EPC cho họ biết trung bình 1 click họ kéo về tạo ra bao nhiêu doanh thu. Nếu EPC lớn hơn chi phí mua 1 click (CPC), họ có lãi (ROI dương) và sẽ tiếp tục vít ngân sách quảng cáo cho sàn."*

### Câu hỏi 4: *"Làm thế nào để em phân biệt giữa một đợt tăng traffic đột biến tự nhiên (Organic Viral) với một cuộc tấn công Click Bot / Gian lận?"*
* **Cách trả lời:**  
  *"Em dựa vào 3 dấu hiệu cốt lõi:  
  1. **Time-to-Convert:** Traffic viral tự nhiên vẫn do người thật xem và đọc, nên thời gian điền form luôn có phân phối chuẩn (từ 20 giây đến vài phút). Còn Bot sẽ có đỉnh nhọn bất thường dưới 3 giây.  
  2. **Đa dạng thiết bị & IP:** Traffic tự nhiên đến từ nhiều tỉnh thành, nhiều nhà mạng (Viettel, VNPT, FPT), nhiều mẫu điện thoại khác nhau. Bot thường tập trung vào cùng một cụm IP / Hosting datacenter và User-Agent đồng nhất.  
  3. **Tỷ lệ tương tác sau chuyển đổi:** Traffic thật sẽ có tỷ lệ nghe máy và thẩm định đạt chuẩn ngành, còn bot sẽ rớt 100% khi telesale gọi xác nhận."*

### Câu hỏi 5: *"Em đã từng làm việc với đội Kỹ thuật (Data Engineer / Backend) như thế nào để xử lý sự cố Data Pipeline?"*
* **Cách trả lời:**  
  *"Em luôn chuẩn bị sẵn sàng trước khi trao đổi: ghi lại log lỗi chính xác, thời điểm xảy ra sự cố, số lượng bản ghi bị lệch giữa Database nguồn và Dashboard Power BI. Em hiểu cấu trúc bảng và viết sẵn query truy vết (Traceability) để đội Backend có thể định vị ngay lỗi xảy ra ở tầng trích xuất API, tầng biến đổi dbt hay tầng nạp dữ liệu."*
