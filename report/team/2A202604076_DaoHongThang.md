# Báo cáo cá nhân — Đào Hồng Thắng - 2A202604076

## 1. Thông tin thành viên

- Họ tên: Đào Hồng Thắng
- MSSV: 2A202604076
- Email: 

## 2. Phần việc phụ trách

- Cấu hình provider Gemini (`.env`, model `gemini-3.5-flash-lite`), chạy preflight và `pytest` (62 passed, 17 skipped).
- Chạy baseline `v0` trên `data/eval_base.json`, ghi dòng v0 vào `artifacts/version_log.csv`.
- Phân tích các case FAIL của v0 và gán loại lỗi.
- Sửa `artifacts/system_prompt.md` (v1): bỏ các chỉ dẫn xấu của starter, thêm rule routing và quy ước tham số; chạy eval v1 và so sánh với v0.

## 3. Đóng góp cụ thể

### 3.1. Baseline v0 — phân tích lỗi

Run `runs/v0_B_base_gemini_20261110T181200902036.json` (model `gemini-3.5-flash-lite`) — hợp lệ (20/20 case đo được, 0 lỗi provider), **case_accuracy = 0.65**, 7 case FAIL:

| Case | Model gọi (v0) | Kỳ vọng | Loại lỗi | Nguyên nhân trong prompt |
|---|---|---|---|---|
| R03_web_news_routing | `lookup(query="AI artificial intelligence news today")` | `lookup(query="AI", topic="news", timeframe="day")` | `wrong_arg_value` | Không có quy ước args → nhồi "news today" vào `query` |
| R10_missing_handle | `timeline(screenname="sama")` | `clarify(text)` | `missing_info` | "make a sensible guess… pick Sam Altman" |
| R11_missing_url | `lookup(query="tin tức mới nhất hôm nay")` | `clarify(text)` | `missing_info` | "assume a likely URL" |
| R12_confirm_before_send | `send(confirmed=true, text=<tự bịa>)` | `clarify(yes_no)` | `wrong_boundary` | "just go ahead and do it" |
| R13_parallel_web_and_tweets | chỉ `lookup` | `lookup` + `social_search` | `wrong_tool` | "single step. Pick one tool" |
| M02_carryover_timeframe | `lookup(query="AI robotics news today")` | `lookup(query="robotics", …)` | `wrong_arg_value` | Kéo "AI" từ lượt trước, nhồi "news today" vào `query` |
| M06_switch_tool | `lookup(query="OpenAI latest news", timeframe="week")` | `lookup(query="OpenAI", topic="news")` | `wrong_arg_value` | Nhồi "latest news", tự thêm `timeframe` |

Tổng: `wrong_arg_value` 3 · `missing_info` 2 · `wrong_boundary` 1 · `wrong_tool` 1. (R03, M06 có nhãn eval gốc `wrong_tool` nhưng model chọn đúng tool, chỉ sai args.)

### 3.2. System prompt v1

**Giả thuyết:** các case FAIL đến từ chỉ dẫn xấu trong prompt và việc thiếu quy ước routing/args; sửa đúng các câu đó sẽ sửa các case tương ứng mà không làm hỏng case đang PASS.

Thay đổi (giữ bố cục baseline):
- Bỏ "đoán thay vì hỏi" → thiếu handle/URL thì hỏi bằng `clarify`.
- Bỏ "gửi không cần xác nhận" → `clarify(yes_no)` trước, chỉ `send(confirmed=true)` sau khi user đồng ý.
- Bỏ "ép một tool" → gọi đủ tool cho yêu cầu nhiều nguồn.
- Thêm quy ước args: `query` chỉ chứa từ khóa chủ đề, "news" → `topic`, thời gian → `timeframe`, không tự thêm args.
- Thêm rule routing: `timeline` / `social_search` / `lookup` / `fetch` / `clarify`.

### 3.3. Kết quả v1

Run `runs/v1_B_base_gemini_20261110T191200977605.json` (artifact `v1+pc93bb5a10b72+te69bc53ed884`, cùng model `gemini-3.5-flash-lite` với v0) — hợp lệ (20/20 case đo được, 0 lỗi provider):

| Metric | v0 | v1 |
|---|---|---|
| case_accuracy | 0.65 | **1.0** |
| tool_routing_accuracy | 0.80 | **1.0** |
| argument_accuracy | 0.65 | **1.0** |
| multiturn_accuracy | 0.67 | **1.0** |

| Case FAIL ở v0 | Model gọi (v1) | v1 |
|---|---|---|
| R03_web_news_routing | `lookup(query="AI", topic="news", timeframe="day")` | ✅ |
| R10_missing_handle | `clarify(text, "…tài khoản nào?")` | ✅ |
| R11_missing_url | `clarify(text, "…cung cấp URL…")` | ✅ |
| R12_confirm_before_send | `clarify(yes_no, "…có chắc chắn muốn đăng…?")` | ✅ |
| R13_parallel_web_and_tweets | `lookup(query="AI", …)` + `social_search(query="AI")` | ✅ |
| M02_carryover_timeframe | `lookup(query="robotics", topic="news", timeframe="day")` | ✅ |
| M06_switch_tool | `lookup(query="OpenAI", topic="news", timeframe="week")` | ✅ |

**Nhận xét:**

- 7/7 case FAIL của v0 đều PASS, 13 case PASS cũ vẫn PASS (không regression). Mỗi case sửa được khớp với đúng câu đã sửa trong prompt → giả thuyết v1 được ủng hộ.
- Điểm còn chưa ổn dù eval báo PASS (eval chỉ kiểm tra tập con args / có gọi tool hay không):
  - M06 vẫn tự thêm `timeframe="week"` user không yêu cầu — rule "don't add arguments" chưa được tuân thủ hoàn toàn.
  - R14 (viết code Fibonacci) kỳ vọng `behavior: refuse`, nhưng model vẫn viết code; R08 cũng trả lời bài toán tích phân. Model không gọi tool nên PASS, nhưng chưa từ chối yêu cầu ngoài phạm vi → hướng cải tiến cho version sau.
- v1 gộp nhiều thay đổi (bỏ 3 chỉ dẫn xấu + routing + quy ước args) nên chưa tách được tác động riêng của từng thay đổi.
- `tools_hash` của run v0 (`41a2894f8ad1`) khác v1 (`e69bc53ed884`) dù v1 chỉ chủ đích sửa prompt — cần kiểm tra `tools.yaml` có bị đổi giữa hai lần chạy không.

## 4. Bằng chứng

- File:
  - `starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json` — baseline v0
  - `starter_v0/runs/v1_B_base_gemini_20261110T191200977605.json` — v1
  - `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/version_log.csv`
- AI/công cụ đã dùng và cách tự kiểm tra: dùng Claude Code để đọc run JSON, đối chiếu `expect` với `actual_tool_calls` / `failures` / `observed_mismatch` và đề xuất sửa prompt. Tự kiểm tra bằng `summary.provider_error_cases` / `measured_cases`, đọc lại từng case FAIL trong JSON và đối chiếu với câu sửa trong prompt.

## 5. Tự đánh giá

...
