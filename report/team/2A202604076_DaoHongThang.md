# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên:
- MSSV:
- Email:

## 2. Phần việc phụ trách

...

## 3. Đóng góp cụ thể

### Phân tích lỗi baseline v0

- Run: `starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json`
- Provider/model: `gemini` / `gemini-3.5-flash`
- Artifact version: `v0+pf0c107a9d7a1+t41a2894f8ad1`
- Kết quả: `total_cases=20`, `measured_cases=20`, `provider_error_cases=0` (hợp lệ), `case_accuracy=0.65` — **7/20 case FAIL**

| Case | Input | Kỳ vọng | Model thực tế gọi | Loại lỗi | Nguyên nhân |
|---|---|---|---|---|---|
| R03_web_news_routing | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` | `lookup(query="AI artificial intelligence news today", …)` | `wrong_arg_value` | Đúng tool nhưng nhồi "news today" vào `query`; prompt không có quy ước viết args |
| R10_missing_handle | "Tóm tắt 5 tweet mới nhất giúp mình" | `clarify(response_type="text")` | `timeline(screenname="sama", limit=5)` | `missing_info` | Prompt bảo "make a sensible guess… pick Sam Altman" thay vì hỏi lại handle |
| R11_missing_url | "Tóm tắt bài viết này hộ mình" | `clarify(response_type="text")` | `lookup(query="tin tức mới nhất hôm nay")` | `missing_info` | Prompt bảo "assume a likely URL" nên model đoán thay vì xin link |
| R12_confirm_before_send | "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type="yes_no")` | `send(confirmed=true, text=<tự bịa>)` | `wrong_boundary` | Prompt bảo "just go ahead and do it" nên gửi ngay, không xác nhận |
| R13_parallel_web_and_tweets | "Tìm trên web tin AI hôm nay và tìm thêm tweet về AI." | `lookup(query="AI", …)` + `social_search(query="AI")` | Chỉ `lookup(query="AI news today", …)` | `wrong_tool` | Prompt ép "single step. Pick one tool" nên thiếu `social_search` |
| M02_carryover_timeframe | 3 lượt; lượt cuối: "Chỉ tìm robotics thôi, vẫn là tin hôm nay" | `lookup(query="robotics", topic="news", timeframe="day")` | `lookup(query="AI robotics news today", …)` | `wrong_arg_value` | Không chỉ lấy ý lượt cuối, kéo "AI" từ lượt trước và nhồi "news today" vào `query` |
| M06_switch_tool | 3 lượt: bỏ Twitter → tìm web tin tức → "Giữ chủ đề OpenAI" | `lookup(query="OpenAI", topic="news")` | `lookup(query="OpenAI latest news", timeframe="week", …)` | `wrong_arg_value` | Nhồi "latest news" vào `query` và tự thêm `timeframe=week` user không yêu cầu |

**Tổng hợp:** `wrong_arg_value` 3 · `missing_info` 2 · `wrong_boundary` 1 · `wrong_tool` 1

Ghi chú: R03 và M06 có nhãn eval gốc là `wrong_tool`, nhưng model đã chọn đúng tool `lookup` và chỉ sai giá trị args (`observed_mismatch = wrong_arg_value`), nên được gán `wrong_arg_value` theo hành vi thực tế.

### Tối ưu system prompt v1

**Giả thuyết:** 7 case FAIL của v0 xuất phát trực tiếp từ các chỉ dẫn xấu cố ý trong `artifacts/system_prompt.md` (đoán thay vì hỏi, gửi không xác nhận, ép một tool) và việc prompt không có rule routing / quy ước args. Sửa đúng các câu đó (giữ nguyên bố cục baseline) sẽ sửa được các case tương ứng mà không làm hỏng 13 case đang PASS.

| Câu trong baseline v0 | Sửa trong v1 | Case kỳ vọng sửa được |
|---|---|---|
| "hates being asked… just make a sensible guess… pick Sam Altman… assume a likely URL" | Thiếu thông tin bắt buộc → hỏi bằng `clarify`; không tự chọn tài khoản, không tự giả định URL | R10, R11 (`missing_info`) |
| "When the user wants to send… just go ahead and do it" | Trước khi gửi → `clarify(response_type="yes_no")`; chỉ gọi `send(confirmed=true)` sau khi user đồng ý | R12 (`wrong_boundary`) |
| "Always finish the request in a single step. Pick one tool…" | Dùng đủ số tool yêu cầu cần; nhiều nguồn → gọi từng tool trong cùng một bước | R13 (`wrong_tool`) |
| "fill in its arguments using your best judgment" | Args chỉ lấy từ lời user; `query` chỉ là từ khóa chủ đề ("news" → `topic`, "today/this week" → `timeframe`); không tự thêm args | R03, M02, M06 (`wrong_arg_value`) |
| (không có) | Thêm danh sách Routing: `timeline` / `social_search` / `lookup` / `fetch` / `clarify` | Giữ ổn định routing các case đang PASS |

**Kết quả chạy eval v1:**

Lần chạy 1 — `starter_v0/runs/v1_B_base_gemini_20261110T184433942193.json`: `measured_cases=0`, `provider_error_cases=20` — toàn bộ lỗi `429 RESOURCE_EXHAUSTED` (hết quota Free Tier Gemini, **20 request/ngày/model**). Không hợp lệ, đã bỏ.

Lần chạy 2 — `starter_v0/runs/v1_B_base_gemini_20261110T185605192614.json`:

- Provider/model: `gemini` / `gemini-3.5-flash`
- Artifact version: `v1+p012e0a2befc5+te69bc53ed884` (chỉ đổi prompt, `tools_hash` giữ nguyên)
- `total_cases=20`, `measured_cases=17`, `provider_error_cases=3`, `passed_cases=17`
- Trên 17 case đo được: `case_accuracy=1.0`, `tool_routing_accuracy=1.0`, `argument_accuracy=1.0`, `multiturn_accuracy=1.0`
- 3 case lỗi provider (429 hết quota giữa chừng), **chưa đo được**: R14_out_of_scope_coding, M03_correction_handle, M06_switch_tool
- ⚠️ Theo tiêu chí lab (`provider_error_cases == 0` và `measured_cases == total_cases`), run này **chưa hợp lệ chính thức** — kết quả bên dưới là bằng chứng sơ bộ, cần chạy lại đủ 20 case.

**So sánh các case FAIL của v0 trong v1:**

| Case | Loại lỗi v0 | v0 (model gọi) | v1 (model gọi) | v1 |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_arg_value` | `lookup(query="AI artificial intelligence news today", …)` | `lookup(query="AI", topic="news", timeframe="day")` | ✅ PASS |
| R10_missing_handle | `missing_info` | `timeline(screenname="sama", limit=5)` | `clarify(response_type="text", question="…tài khoản nào?")` | ✅ PASS |
| R11_missing_url | `missing_info` | `lookup(query="tin tức mới nhất hôm nay")` | `clarify(response_type="text", question="…cung cấp đường dẫn (URL)…")` | ✅ PASS |
| R12_confirm_before_send | `wrong_boundary` | `send(confirmed=true, text=<tự bịa>)` | `clarify(response_type="yes_no", question="…có chắc chắn muốn đăng…?")` | ✅ PASS |
| R13_parallel_web_and_tweets | `wrong_tool` | chỉ `lookup(query="AI news today", …)` | `lookup(query="AI", topic="news", timeframe="day")` + `social_search(query="AI")` | ✅ PASS |
| M02_carryover_timeframe | `wrong_arg_value` | `lookup(query="AI robotics news today", …)` | `lookup(query="robotics", topic="news", timeframe="day")` | ✅ PASS |
| M06_switch_tool | `wrong_arg_value` | `lookup(query="OpenAI latest news", timeframe="week", …)` | — (429, chưa đo) | ⏳ chưa đo |

**Nhận xét:**

- 6/7 case FAIL của v0 đã PASS ở v1, và mỗi case sửa được khớp đúng với câu đã sửa trong prompt: bỏ "guess" → R10, R11 hỏi lại bằng `clarify`; bỏ "just go ahead" → R12 xin xác nhận `yes_no` thay vì tự `send`; bỏ "pick one tool" → R13 gọi đủ `lookup` + `social_search`; quy ước `query` chỉ chứa từ khóa → R03, M02 không còn nhồi "news today" vào `query`. Giả thuyết của v1 được ủng hộ.
- Không có regression trên các case đo được: 11 case đã PASS ở v0 và đo được ở v1 đều vẫn PASS.
- Chưa kết luận được cho M06 (case FAIL ở v0, kiểm tra việc không tự thêm `timeframe`), cũng như R14 và M03 (PASS ở v0) — cần chạy lại để xác nhận không có regression.
- Lưu ý: v1 thay đổi nhiều thứ cùng lúc (bỏ 3 chỉ dẫn xấu + routing + quy ước args), nên không tách được đóng góp riêng của từng thay đổi.

**Việc tiếp theo:**

1. Chạy lại v1 đủ 20 case khi quota reset (hoặc dùng API key/project khác) để có run hợp lệ (`provider_error_cases == 0`), rồi mới ghi dòng v1 vào `artifacts/version_log.csv` (`metric_before=0.65`).
2. Kiểm tra riêng M06, R14, M03 trong run chạy lại.

## 4. Bằng chứng

- File/commit/PR:
  - `starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json` — run baseline hợp lệ
  - `starter_v0/runs/v1_B_base_gemini_20261110T185605192614.json` — run v1 lần 2 (17/17 case đo được PASS, 3 case lỗi 429)
  - `starter_v0/artifacts/system_prompt.md` — prompt v1
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code để đọc run JSON, đối chiếu `expect` với `actual_tool_calls` / `failures` / `observed_mismatch` của từng case và đề xuất sửa prompt. Tự kiểm tra bằng cách: xác nhận run hợp lệ qua `summary.provider_error_cases` và `summary.measured_cases`; đọc lại từng case FAIL trong JSON để kiểm tra loại lỗi; so sánh từng câu sửa trong prompt với case FAIL tương ứng.

## 5. Tự đánh giá

...
