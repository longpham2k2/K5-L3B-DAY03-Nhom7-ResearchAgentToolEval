# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Nhóm 7
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `gemini` / `gemini-3.5-flash-lite` (xem mục 5 về lý do chọn model)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa (`prompt_hash` `f0c107a9d7a1`, `tools_hash` `41a2894f8ad1`) | — | 0.65 | [v0_B_base_gemini_20261110T181200902036.json](../../starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json) |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: [v0_B_base_gemini_20261110T181200902036.json](../../starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json) — 20/20 case đo được, `provider_error_cases = 0`. Kết quả: `case_accuracy` 0.65 (13/20), `tool_routing_accuracy` 0.80, `argument_accuracy` 0.65, `multiturn_accuracy` 0.6667.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value (case gắn nhãn `wrong_tool`) | `lookup(query="AI artificial intelligence news today", topic="news", timeframe="day", max_results=5)` | Chọn đúng tool nhưng `query` bị thêm từ thừa; expected `query="AI"` | `tools.yaml`: mô tả `query` chỉ chứa chủ đề cốt lõi, không thêm "news/today" vì đã có `topic`/`timeframe` |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query="AI news today", topic="news", timeframe="day")` | Thiếu lời gọi `social_search(query="AI")`; `query` cũng bị thêm từ thừa | `system_prompt.md`: bỏ câu "Always finish the request in a single step. Pick one tool"; cho phép gọi nhiều tool khi user yêu cầu nhiều nguồn |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="AI robotics news today", topic="news", timeframe="day")` | Giữ đúng `timeframe` từ turn trước nhưng kéo cả chủ đề cũ "AI" vào `query`; expected `query="robotics"` | Như R03, thêm rule: khi user đổi chủ đề thì thay `query`, chỉ giữ lại các ràng buộc (timeframe, topic) |
| M06_switch_tool | wrong_arg_value (case gắn nhãn `wrong_tool`) | `lookup(query="OpenAI latest news", topic="news", timeframe="week")` | Đã chuyển đúng sang `lookup`, chỉ sai `query`; expected `query="OpenAI"` | Như R03 |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Không biết tweet của ai nhưng tự đoán `sama` thay vì hỏi lại | `system_prompt.md`: bỏ chỉ dẫn "pick a well-known account like Sam Altman"; thêm rule thiếu handle → `clarify` |
| R11_missing_url | missing_info | `lookup(query="tin tức mới nhất hôm nay")` | "Bài viết này" không có URL nhưng agent tự tìm web thay vì hỏi URL | `system_prompt.md`: bỏ chỉ dẫn "assume a likely URL"; thêm rule thiếu URL → `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(confirmed=true, text="Bản tin cập nhật hôm nay: ...")` | Tự đặt `confirmed=true` và gửi nội dung tự bịa, không hỏi xác nhận | `system_prompt.md`: bỏ "just go ahead and do it"; `tools.yaml`: `send` chỉ dùng `confirmed=true` sau khi user xác nhận qua `clarify(response_type="yes_no")` |

Nguyên nhân gốc: 3 lỗi `missing_info`/`wrong_boundary` (R10, R11, R12) đến trực tiếp từ các chỉ dẫn xấu cố ý trong `system_prompt.md` của starter (đoán thay vì hỏi, gửi không cần xác nhận). 4 lỗi còn lại (R03, R13, M02, M06) đều có `query` bị thêm từ thừa → thiếu convention args trong `tools.yaml`; R13 còn do chỉ dẫn "single step / one tool".

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- **Provider Gemini lỗi khi chạy preflight/eval (CP1).** Model mặc định `gemini-3.8-flash` trả `503 UNAVAILABLE` ("model is currently experiencing high demand"); thử `gemini-2.5-flash` thì bị `404 NOT_FOUND` ("no longer available to new users"). Cách xử lý: thêm retry có backoff cho lỗi 503/429 trong `starter_v0/providers/gemini_provider.py`, cho phép đổi model qua biến `GEMINI_MODEL`, và chốt model `gemini-3.5-flash-lite` cho toàn bộ v0–v3 để so sánh công bằng. Run v0 hợp lệ: `provider_error_cases = 0`, `measured_cases = total_cases = 20`.
- **Twitter API (RapidAPI `twitter-api45`) trả `403 Forbidden` / `429 Too Many Requests`** trong lần chạy v0 đầu tiên (model `gemini-3.5-flash`, run đó đã bỏ khi đổi model). Lỗi này không ảnh hưởng điểm eval (eval chấm tool call + args). Trong run v0 chính thức không còn lỗi Twitter; lỗi tool duy nhất là `send` thiếu `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` (case R12), vì nhóm chưa cấu hình Telegram.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
