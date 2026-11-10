# Báo cáo cá nhân — Đào Hồng Thắng - 2A202604076

## 1. Thông tin thành viên

- Họ tên: Đào Hồng Thắng
- MSSV: 2A202604076
- Email: 

## 2. Phần việc phụ trách

- Cấu hình provider Gemini (`.env`, model `gemini-3.5-flash-lite`), chạy preflight và `pytest` (62 passed, 17 skipped).
- Chạy baseline `v0` trên `data/eval_base.json`, ghi dòng v0 vào `artifacts/version_log.csv`.
- Phân tích các case FAIL của v0 và gán loại lỗi.
- Tối ưu `artifacts/system_prompt.md` theo nguyên tắc mỗi version một giả thuyết:
  - v1: bỏ các chỉ dẫn xấu cố ý của starter.
  - v2: thêm rule routing (chưa sửa `tools.yaml`).
- Chạy eval từng version, so sánh metric và phân tích case FAIL.

## 3. Đóng góp cụ thể

Tất cả run dùng cùng provider/model `gemini` / `gemini-3.5-flash-lite`, cùng `data/eval_base.json`, hợp lệ (20/20 case đo được, 0 lỗi provider).

### 3.1. Baseline v0 — phân tích lỗi

Run `runs/v0_B_base_gemini_20261110T181200902036.json` — **case_accuracy = 0.65**, 7 case FAIL:

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

### 3.2. v1 — bỏ chỉ dẫn xấu

**Giả thuyết:** các lỗi `missing_info`, `wrong_boundary`, `wrong_tool` đến từ 3 chỉ dẫn xấu cố ý; bỏ chúng (không nhắc tên tool/tham số) sẽ khiến model hỏi lại khi thiếu thông tin, xác nhận trước khi gửi và dùng đủ tool.

| Baseline v0 | v1 |
|---|---|
| "fast, proactive" | "fast, careful" |
| "hates being asked… make a sensible guess… pick Sam Altman… assume a likely URL" | Thiếu thông tin → hỏi lại thay vì đoán; hỏi tài khoản nào, hỏi link |
| "just go ahead and do it" | Xác nhận với user trước, chỉ làm khi user đồng ý |
| "single step. Pick one tool… best judgment" | Dùng đủ bước/tool cần thiết; args chỉ lấy từ lời user |

Run `runs/v1_B_base_gemini_20261110T193341337170.json` — **case_accuracy = 0.70** (0.65 → 0.70):

| Case | v0 | v1 |
|---|---|---|
| R10, R11 | ❌ đoán handle / URL | ✅ `clarify(text)` hỏi tài khoản / link |
| R12 | ❌ tự `send(confirmed=true)` | ❌ đã hỏi lại thay vì tự gửi, nhưng `response_type="text"` thay vì `yes_no` |
| R13 | ❌ chỉ `lookup` | ❌ đã gọi đủ `lookup` + `social_search`, nhưng `query="AI news today"` |
| M01 | ✅ | ❌ **regression**: user đã nói "Elon Musk" nhưng model vẫn `clarify` hỏi tài khoản |
| R03, M02, M06 | ❌ | ❌ vẫn nhồi "news today/news" vào `query` |

**Nhận xét:** giả thuyết được ủng hộ — hết hành vi đoán bừa và tự gửi, R13 đã gọi đủ 2 tool. R12, R13 vẫn FAIL nhưng giờ chỉ do sai args. Regression M01 cho thấy bỏ "đoán" khiến model hỏi lại quá mức.

### 3.3. v2 — thêm routing

**Giả thuyết:** thêm quy tắc "loại yêu cầu → tool" vào prompt (không mô tả tool làm gì, không sửa `tools.yaml`) sẽ giúp model chọn đúng tool và đúng kiểu `clarify`.

Thêm vào prompt v1:

```
Routing:
- Posts from a specific person or account → `timeline`
- Tweets or posts about a topic → `social_search`
- Web search or news → `lookup`
- A link the user gave → `fetch`
- Missing information → `clarify` (text)
- Request to send, post, or publish → `clarify` (yes_no) first
```

Run `runs/v2_B_base_gemini_20261110T194153325112.json`:

| Metric | v0 | v1 | v2 |
|---|---|---|---|
| case_accuracy | 0.65 | 0.70 | 0.70 |
| tool_routing_accuracy | 0.80 | 0.95 | **1.0** |
| argument_accuracy | 0.65 | 0.70 | 0.70 |
| multiturn_accuracy | 0.67 | 0.50 | **0.67** |

| Case | v1 | v2 |
|---|---|---|
| M01 | ❌ hỏi lại tài khoản | ✅ `timeline(screenname="ElonMusk", limit=5)` |
| R11 | ✅ `clarify(response_type="text")` | ❌ **regression**: `clarify` bỏ trống `response_type` |
| R12 | ❌ `response_type="text"` | ❌ `clarify` bỏ trống `response_type` |
| R03, R13, M02, M06 | ❌ nhồi từ vào `query` | ❌ như cũ |

**Nhận xét:**

- Giả thuyết đúng trong phạm vi routing: `tool_routing_accuracy` đạt 1.0 (chọn đúng tool ở 20/20 case), sửa được M01.
- `case_accuracy` không tăng vì M01 sửa được nhưng R11 regression. Model hiểu cách ghi `clarify (text)` / `clarify (yes_no)` là chú thích chứ không phải giá trị tham số, nên bỏ trống `response_type`.
- Toàn bộ 6 case FAIL còn lại đều là `wrong_arg_value` (`query` bị nhồi từ, `response_type` thiếu/sai) → nút thắt hiện tại là mô tả tham số. Đây là giả thuyết cho v3: viết lại description tham số trong `tools.yaml` (`query` chỉ chứa từ khóa chủ đề; `topic`/`timeframe` cho tin tức và thời gian; `response_type` = `yes_no` khi xác nhận gửi, `text` khi hỏi thông tin).

## 4. Bằng chứng

- File:
  - `starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json` — baseline v0
  - `starter_v0/runs/v1_B_base_gemini_20261110T193341337170.json` — v1
  - `starter_v0/runs/v2_B_base_gemini_20261110T194153325112.json` — v2
  - `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/version_log.csv`
- AI/công cụ đã dùng và cách tự kiểm tra: dùng Claude Code để đọc run JSON, đối chiếu `expect` với `actual_tool_calls` / `failures` / `observed_mismatch` và đề xuất sửa prompt. Tự kiểm tra bằng `summary.provider_error_cases` / `measured_cases`, đọc lại từng case FAIL trong JSON, so sánh từng case giữa các version để phát hiện regression.

## 5. Tự đánh giá

...
