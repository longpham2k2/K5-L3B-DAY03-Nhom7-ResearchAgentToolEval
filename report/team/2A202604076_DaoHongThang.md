# Báo cáo cá nhân — Đào Hồng Thắng - 2A202604076

## 1. Thông tin thành viên

- Họ tên: Đào Hồng Thắng
- MSSV: 2A202604076
- Email: 

## 2. Phần việc phụ trách

Tôi phụ trách tối ưu `artifacts/system_prompt.md` qua hai phiên bản v1 và v2.

## 3. Đóng góp cụ thể

Các run đều chạy trên `data/eval_base.json` với model `gemini-3.5-flash-lite`, đủ 20/20 case và không có lỗi provider.

### v0 — Gán nhãn lỗi

Baseline đạt 0.65, sai 7/20 case:

| Case | Model làm gì | Loại lỗi |
|---|---|---|
| R03_web_news_routing | Gọi `lookup` nhưng viết query thành "AI artificial intelligence news today" | `wrong_arg_value` |
| R10_missing_handle | Không biết tài khoản nào nên tự chọn Sam Altman | `missing_info` |
| R11_missing_url | Không có link nên tự đi tìm tin tức thay vì hỏi | `missing_info` |
| R12_confirm_before_send | Tự soạn nội dung rồi gửi luôn lên Telegram | `wrong_boundary` |
| R13_parallel_web_and_tweets | Chỉ tìm trên web, bỏ qua phần tìm tweet | `wrong_tool` |
| M02_carryover_timeframe | Query thành "AI robotics news today" thay vì "robotics" | `wrong_arg_value` |
| M06_switch_tool | Query thành "OpenAI latest news", tự thêm `timeframe=week` | `wrong_arg_value` |

Phần lớn lỗi đến thẳng từ các chỉ dẫn cố ý sai trong prompt gốc: "đừng hỏi lại, cứ đoán", "muốn gửi thì gửi luôn", "chỉ chọn một tool".

### v1 — Bỏ chỉ dẫn xấu

Giữ nguyên bố cục prompt gốc, chỉ thay ba chỗ: thiếu thông tin thì hỏi lại thay vì đoán, muốn gửi thì phải hỏi xác nhận trước, và được dùng nhiều tool nếu yêu cầu cần. Prompt không nhắc tên tool hay tham số nào.

Kết quả tăng từ 0.65 lên **0.70**. R10 và R11 đã biết hỏi lại tài khoản và link; R12 không còn tự gửi; R13 đã gọi đủ cả hai tool. Tuy vậy R12, R13 vẫn bị chấm sai vì tham số chưa đúng, và có một case bị hỏng thêm: ở M01 người dùng đã nói "Elon Musk" nhưng model vẫn hỏi lại tài khoản nào — tức là sau khi bỏ "cứ đoán", model chuyển sang hỏi hơi quá tay.

### v2 — Thêm routing

Trên nền v1, tôi thêm một đoạn ngắn chỉ ra loại yêu cầu nào thì dùng tool nào (tweet của một người → `timeline`, tweet theo chủ đề → `social_search`, tìm web/tin tức → `lookup`, có link → `fetch`, thiếu thông tin hoặc cần xác nhận → `clarify`). `tools.yaml` giữ nguyên.

| Metric | v0 | v1 | v2 |
|---|---|---|---|
| case_accuracy | 0.65 | 0.70 | 0.70 |
| tool_routing_accuracy | 0.80 | 0.95 | **1.0** |


## 4. Bằng chứng

- File:`
  - `starter_v0/runs/v1_B_base_gemini_20261110T193341337170.json`
  - `starter_v0/runs/v2_B_base_gemini_20261110T194153325112.json`
  - `starter_v0/artifacts/system_prompt.md`
- AI/công cụ đã dùng và cách tự kiểm tra: dùng Claude Code để đọc run JSON và gợi ý chỗ sửa prompt. Tôi tự kiểm tra bằng cách xem `provider_error_cases` và `measured_cases` để chắc run hợp lệ, rồi đọc lại từng case sai trong JSON và so sánh giữa các version để phát hiện case bị hỏng thêm.

## 5. Tự đánh giá

...
