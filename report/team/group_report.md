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

**Research agent cho tin AI/công nghệ:** tìm tin trên web, tweet theo tài khoản hoặc theo chủ đề, đọc nội dung từ URL; tra thêm Wikipedia, Hacker News, repo GitHub và model Hugging Face (4 tool nhóm tự viết); tổng hợp thành bản tin và chỉ gửi lên Telegram sau khi người dùng xác nhận. Khi thiếu thông tin (không rõ tài khoản, không có link) agent hỏi lại bằng `clarify` thay vì tự đoán.

**Cách chạy UI:**

UI Streamlit ở `starter_v0/app.py` (dependency `streamlit>=1.30.0` đã thêm vào `starter_v0/requirements.txt`):

```bash
cd starter_v0
pip install -r requirements.txt
cp .env.example .env          # điền GEMINI_API_KEY + TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY
streamlit run app.py
```

Trong sidebar chọn provider **Google Gemini**, model `gemini-3.5-flash-lite` (model nhóm dùng cho v0–v3), nhãn version `v3`. UI chat nhiều lượt, hiển thị tool call và kết quả tool, lưu transcript vào `starter_v0/transcripts/`; lệnh gửi Telegram luôn dừng lại để người dùng kiểm tra nội dung và xác nhận trước khi gửi.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://biblical-leeds-palace-conduct.trycloudflare.com _(link tạm của Cloudflare Tunnel, đã hết hiệu lực)_

Nhóm đã deploy cho Team showdown bằng **Streamlit + Cloudflare Tunnel**: Tuấn chạy `streamlit run app.py` trên máy cá nhân và mở tunnel bằng `cloudflared tunnel --url http://localhost:8501`, tạo link tạm `trycloudflare.com` cho team khác dùng thử. Link này chỉ sống theo phiên `cloudflared`, nên **không còn truy cập được** sau khi máy của Tuấn tắt. Để chạy lại: làm theo "Cách chạy UI" ở trên, rồi chạy lại lệnh `cloudflared` để nhận link mới (mỗi lần chạy là một link khác).

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (tài khoản, link…), hoặc xin xác nhận yes/no trước khi gửi | không |
| `timeline` | Lấy tweet mới nhất của một tài khoản cụ thể (RapidAPI Twitter) | không |
| `social_search` | Tìm tweet theo chủ đề, sắp xếp mới nhất (`Latest`) hoặc nổi bật (`Top`) | không |
| `lookup` | Tìm kiếm web và tin tức theo khoảng thời gian (Tavily) | không |
| `fetch` | Đọc nội dung một trang từ URL người dùng đưa (Firecrawl) | không |
| `format` | Trình bày các kết quả đã thu thập thành bản tin markdown (không tự lấy dữ liệu) | không |
| `send` | Gửi bản tin lên Telegram, chỉ sau khi người dùng đã xác nhận | không |
| `policy` | Tra tài liệu nội bộ của công ty (`company_policy/`): quy định trích nguồn, bảo mật dữ liệu, đăng bài ra ngoài… | không |
| `papers` | Tìm bài báo khoa học trên arXiv | không |
| `paper_text` | Lấy nội dung text của một bài arXiv theo ID hoặc link | không |
| `wiki` | Tra kiến thức nền trên Wikipedia (khái niệm, tiểu sử, lịch sử; tiếng Anh hoặc tiếng Việt) | **có** |
| `hackernews` | Tìm bài thảo luận trên Hacker News về một chủ đề, theo độ liên quan hoặc mới nhất | **có** |
| `github` | Tìm repo / thư viện open-source trên GitHub, theo số sao hoặc mới cập nhật | **có** |
| `huggingface` | Tìm model AI trên Hugging Face Hub, theo lượt tải, lượt thích hoặc mới cập nhật | **có** |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

Nhóm sửa theo thứ tự: **bỏ chỉ dẫn xấu → thêm routing → thêm quy ước args**, mỗi version một giả thuyết; prompt sửa hành vi chung, `tools.yaml` sửa quy ước riêng của từng tool. Kết quả base suite: `case_accuracy` 0.65 (v0) → 0.70 (v1) → 0.70 (v2) → 0.90 (v3), chi tiết ở B1.

**`system_prompt.md` (v1, v2 — commit `b6763ae`, `3a0640f`)**

- **v1 — bỏ 3 chỉ dẫn xấu của starter:**
  - "đoán thay vì hỏi" (tự chọn tài khoản như Sam Altman, tự đoán URL) → thiếu thông tin thì hỏi lại: không rõ tài khoản thì hỏi tài khoản, chỉ có "bài viết này" thì xin link.
  - "gửi ngay không cần chờ" → muốn gửi/đăng/publish thì xác nhận với người dùng trước, chỉ làm sau khi họ đồng ý.
  - "luôn xong trong một bước, chọn một tool" → dùng bao nhiêu bước/tool cũng được nếu yêu cầu cần, và chỉ điền args từ những gì người dùng thực sự nói.
- **v2 — thêm bảng routing:** bài của một tài khoản cụ thể → `timeline`; tweet theo chủ đề → `social_search`; tìm web/tin tức → `lookup`; link người dùng đưa → `fetch`; thiếu thông tin → `clarify` (`text`); yêu cầu gửi/đăng → `clarify` (`yes_no`) trước.

**`tools.yaml` (v3 — commit `b02cf90`; khai báo tool mới — commit `117b59a`)**

- **v3 — quy ước args trong description tham số** (prompt giữ nguyên):
  - `lookup.query`: chỉ từ khóa chủ đề cốt lõi, không thêm "news / tin tức / today / hôm nay" vì đã có `topic` và `timeframe` (ví dụ "tin tức chip bán dẫn tuần này" → `query="chip bán dẫn"`).
  - `lookup.topic` / `lookup.timeframe`: hỏi tin → `news`; "hôm nay" → `day`, "tuần này" → `week`…; ở lượt sau nếu người dùng không đổi thì giữ giá trị cũ.
  - `clarify.response_type`: luôn điền (đưa vào `required`); `text` để xin thông tin còn thiếu, `yes_no` để xin xác nhận trước khi gửi.
  - `send.confirmed`: chỉ đặt `true` khi người dùng đã đồng ý ở lượt trước cho đúng nội dung đó; chưa có xác nhận thì gọi `clarify(response_type="yes_no")`.
- **Khai báo 4 tool mới** ở cuối file, mỗi description ghi rõ **khi nào dùng / KHÔNG dùng** để tool mới không giành câu hỏi của tool cũ. Thay đổi này đổi `tools_hash` và **chưa được đo** bằng base suite (sẽ là version tiếp theo sau v3).

**Tool mới nhóm viết (`starter_v0/tools/<tên>/`, PR #1 `07ed325`)**

| Tool | Làm gì | Khi nào agent nên gọi | Khi nào KHÔNG gọi |
|---|---|---|---|
| `wiki` | Tìm bài Wikipedia (en/vi) | Hỏi khái niệm, định nghĩa, tiểu sử, lịch sử | Tin mới, sự kiện gần đây → `lookup` |
| `hackernews` | Tìm thảo luận Hacker News (theo độ liên quan / mới nhất) | Hỏi rõ về Hacker News, hoặc dân lập trình đang bàn gì về một chủ đề | Tin tức chung → `lookup`; tweet → `social_search` |
| `github` | Tìm repo GitHub (theo sao / mới cập nhật / khớp nhất) | Tìm repo, thư viện, project open-source về một chủ đề | Viết code hộ người dùng; tin tức → `lookup` |
| `huggingface` | Tìm model trên Hugging Face Hub (theo lượt tải / lượt thích / mới cập nhật) | Tìm model, checkpoint, model phổ biến cho một tác vụ | Tin AI → `lookup`; paper → `papers` |

Cả 4 tool gọi API công khai, không cần key, chỉ đọc (không side effect), trả item cùng format với tool có sẵn để `format` dùng tiếp, và trả error dict thay vì raise khi lỗi. Mỗi tool có 4–5 unit test (xem B5a).

**Sửa bug trong tool có sẵn (commit `3f31924`):** `timeline`, `social_search`, `lookup` trả danh sách rỗng khi model gửi `limit="0"` dạng chuỗi; sửa bằng hàm `_clamp` trong `starter_v0/tools/_shared.py` và giữ regression test (xem B5a).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa (`prompt_hash` `f0c107a9d7a1`, `tools_hash` `41a2894f8ad1`) | — | 0.65 | [v0_B_base_gemini_20261110T181200902036.json](../../starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json) |
| v1 | `system_prompt.md` (`b6763ae`) | Lỗi `missing_info` / `wrong_boundary` ở v0 (R10, R11, R12) là do 3 chỉ dẫn xấu trong prompt (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước/một tool); bỏ chúng thì agent sẽ hỏi lại thay vì đoán | 0.65 | 0.70 | [v1_B_base_gemini_20261110T193341337170.json](../../starter_v0/runs/v1_B_base_gemini_20261110T193341337170.json) |
| v2 | `system_prompt.md` (`3a0640f`) | Agent chọn sai hoặc bỏ sót tool vì không biết khi nào dùng tool nào; thêm bảng routing sẽ tăng `tool_routing_accuracy` | 0.70 | 0.70 | [v2_B_base_gemini_20261110T194153325112.json](../../starter_v0/runs/v2_B_base_gemini_20261110T194153325112.json) |
| v3 | `tools.yaml` (`b02cf90`) | Sau v2 routing đã 100%, các case FAIL còn lại đều là `wrong_arg_value` (`query` bị nhồi từ chỉ loại tin / thời gian; `clarify` thiếu hoặc sai `response_type`); thêm quy ước args vào description tham số sẽ tăng `argument_accuracy` | 0.70 | 0.90 | [v3_B_base_gemini_20261110T195449033306.json](../../starter_v0/runs/v3_B_base_gemini_20261110T195449033306.json) |

Metric là `summary.case_accuracy`. Cả 4 run: provider `gemini`, model `gemini-3.5-flash-lite`, base suite `data/eval_base.json`, 20/20 case đo được, `provider_error_cases = 0`.

**Toàn bộ metric theo version:**

| Version | `case_accuracy` | `tool_routing_accuracy` | `argument_accuracy` | `multiturn_accuracy` | Case sửa được | Case bị hỏng (regression) |
|---|---:|---:|---:|---:|---|---|
| v0 | 0.65 | 0.80 | 0.65 | 0.67 | — | — |
| v1 | 0.70 | 0.95 | 0.70 | 0.50 | R10, R11 | M01 |
| v2 | 0.70 | **1.00** | 0.70 | 0.67 | M01 | R11 |
| v3 | **0.90** | 1.00 | **0.90** | **0.83** | R03, R11, R13, M02 | — |

**Đọc kết quả:**

- **v1 (giả thuyết được ủng hộ một phần):** R10, R11 chuyển sang hỏi lại đúng như dự đoán, routing tăng 0.80 → 0.95. R12 vẫn FAIL (agent hỏi lại nhưng dùng `response_type="text"` thay vì `yes_no`). Có 1 regression: M01 — agent hỏi lại tài khoản của "Elon Musk" dù tên đã đủ để suy ra handle, tức là bỏ chỉ dẫn "đừng hỏi" làm agent hỏi quá tay.
- **v2 (giả thuyết được ủng hộ):** `tool_routing_accuracy` đạt 1.00 và M01 PASS lại. `case_accuracy` không đổi vì các lỗi còn lại đều là lỗi args, routing không sửa được. R11 chuyển sang FAIL: agent vẫn gọi đúng `clarify` và hỏi đúng ý, nhưng không truyền `response_type` → bị chấm sai (xem B6).
- **v3 (giả thuyết được ủng hộ):** chỉ sửa `tools.yaml`, `argument_accuracy` tăng 0.70 → 0.90, sửa được 4 case, không có regression. Đây là bằng chứng description tham số tự nó thay đổi được hành vi của model. Còn FAIL: R12 (`clarify` hỏi nội dung bản tin bằng `text` thay vì xin xác nhận `yes_no`) và M06 (`query="OpenAI tin tức"` — từ tiếng Việt vẫn lọt vào `query` ở hội thoại nhiều lượt).

**Lưu ý về hash:** `tools_hash` của v1, v2 (`e69bc53ed884`) khác v0 (`41a2894f8ad1`), và `prompt_hash` của v3 (`aeef10d86de9`) khác v2 (`6e4a31497aa1`), nhưng nội dung file không đổi — chỉ khác line ending CRLF/LF giữa các máy chạy eval (xem mục 5). Mỗi version chỉ thay đổi thật đúng một file như cột Changed Artifact.

**Giới hạn:** mỗi version chỉ chạy 1 lần. Thay đổi 1 case (0.05) như v0 → v1 có thể nằm trong độ dao động ngẫu nhiên của model; bước nhảy 4 case của v3 đáng tin hơn.

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
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/wiki/`, `hackernews/`, `github/`, `huggingface/` (`tool.py` + `TOOL.md`, PR #1 `07ed325`); đăng ký trong `starter_v0/tools/__init__.py`; khai báo trong `starter_v0/artifacts/tools.yaml` (`117b59a`) | `wiki`: tìm bài Wikipedia (en/vi); `hackernews`: tìm thảo luận Hacker News theo độ liên quan hoặc mới nhất; `github`: tìm repo theo sao / cập nhật; `huggingface`: tìm model trên Hugging Face Hub. Cả 4 gọi API công khai, không cần key, trả item cùng format (`title`, `url`, `source`, `summary`, `date`, `metrics`) để `format` dùng tiếp | Chỉ đọc, không side effect. Input từ model được làm sạch: query rỗng → error dict và **không gửi request**; `sort`/`lang` ngoài enum → giá trị mặc định; `limit` được kẹp vào khoảng hợp lệ. Lỗi HTTP / mất mạng → error dict, không raise. Rủi ro routing (tool mới giành câu hỏi của `lookup`): xem B5 |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; `pytest` output: **119 passed, 0 failed, 0 skipped** | `wiki` 4 test, `hackernews` 4, `github` 5, `huggingface` 5 (tổng 18). Mỗi tool có đủ 3 loại: happy path (assert cả request gửi đi — URL, params, header — lẫn kết quả map ra), input xấu (sort ngoài enum, `limit` = `500` / `"abc"` / `"0"`, lang không hỗ trợ, payload lạ), nhánh lỗi (HTTP 403/503, `ConnectionError`, query rỗng) | Mọi HTTP bị chặn bởi `tests/conftest.py`, test dùng fixture `fake_http`, không gọi mạng thật, không tốn credit |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py` (Streamlit, commit `964df71`); test `starter_v0/tests/test_chat_ui.py`. **Lệnh chạy:** `cd starter_v0 && pip install -r requirements.txt && streamlit run app.py` (→ `http://localhost:8501`; cấu hình key trong `starter_v0/.env`). **Link dùng thử:** đã deploy bằng Streamlit + Cloudflare Tunnel cho showdown; link `trycloudflare.com` là tạm thời và đã hết hiệu lực khi máy host tắt — xem mục A1 | Chat nhiều lượt với agent; sidebar chọn provider/model (nhóm dùng Google Gemini, `gemini-3.5-flash-lite`), nhãn version, số vòng gọi tool tối đa; hiển thị tool call và kết quả tool; lưu transcript vào `starter_v0/transcripts/`. Đã kiểm tra UI khởi động được (health check Streamlit trả `ok`) | **Guardrail:** khi agent gọi `send`, UI chặn lại trước khi thực thi (trạng thái `awaiting_confirmation`), hiện nguyên nội dung sẽ gửi và chỉ gửi khi người dùng bấm “Xác nhận gửi nội dung này”; nút bị khóa nếu nội dung rỗng. Có test `test_tool_call_guard_pauses_send_before_execution`. **Rủi ro:** link public dùng API key và quota của nhóm — chỉ chia sẻ trong zone, tắt tunnel sau showdown |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

- **Số test đã viết:** 18 test cho 4 tool mới, 4 regression test cho bug trong tool có sẵn, và điền hết 14 stub `pytest.skip(TODO)` của tool có sẵn. Toàn suite: 119 passed, 0 skipped.
- **Ví dụ lỗi unit test bắt được nhưng eval không bắt được:** `timeline` và `social_search` cắt kết quả bằng `items[: int(limit or 5)]`, `lookup` gửi `int(max_results or 5)`. Model hay gửi số dạng chuỗi; `"0"` là chuỗi khác rỗng nên `or 5` không có tác dụng → `limit = 0` → tool trả **danh sách rỗng mà không báo lỗi**. Eval không bắt được vì eval chỉ chấm model gọi tool nào với args gì: `timeline(screenname="sama", limit="0")` vẫn có thể PASS, trong khi user nhận về 0 tweet. Unit test bắt được vì gọi thẳng tool với `limit="0"` và assert số item. Cách sửa: thêm `_clamp(value, default, maximum)` vào `starter_v0/tools/_shared.py` (chuỗi rỗng/không phải số/< 1 → default, quá lớn → maximum). Regression test: `test_clamp_handles_string_zero_junk_and_cap`, `test_timeline_string_zero_limit_falls_back_to_default`, `test_social_search_string_zero_limit_falls_back_to_default`, `test_lookup_string_zero_max_results_falls_back_to_default` (fail trước khi sửa, pass sau khi sửa — xem báo cáo cá nhân của Duy, mục 3.3).

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) | `starter_v0/tools/{wiki,hackernews,github,huggingface}/` (`tool.py` + `TOOL.md`); đăng ký trong `starter_v0/tools/__init__.py` (PR #1, `07ed325`); khai báo trong `starter_v0/artifacts/tools.yaml` (`117b59a`); test trong `starter_v0/tests/test_tools_todo.py` | 4 tool gọi API công khai, không cần key. Mỗi tool có 4–5 test (happy path, input xấu như sort ngoài enum / `limit` = `500`, `"abc"`, `"0"`, nhánh lỗi HTTP 403/503 / mất mạng / query rỗng → trả error dict, không raise). `pytest`: 119 passed, 0 skipped; contract test kiểm tra cả 4 tool sau khi khai báo. Eval case route tới từng tool: đang làm trong `data/eval_group.json` | **Rủi ro:** tool mới “giành” câu hỏi của tool cũ (vd “tin công nghệ hôm nay” bị route sang `hackernews` thay vì `lookup(topic="news")`). **Guardrail:** description mỗi tool mới ghi rõ khi nào dùng / KHÔNG dùng; chạy lại base suite chỉ với thay đổi khai báo này (so với v3 = 0.90, fail R12, M06) để bắt regression; thêm case đối chứng trong `eval_group.json`. |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output: **119 passed, 0 failed, 0 skipped**; `starter_v0/tests/test_tools_todo.py` (commit `3f31924`) | Đạt **cả hai** điều kiện: (1) điền hết 14 stub `pytest.skip(TODO)` của tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) → toàn suite 0 skipped; (2) tìm 1 bug trong tool có sẵn, sửa và giữ 4 regression test | Test không gọi mạng thật (mọi HTTP bị chặn trong `tests/conftest.py`, dùng `fake_http`); regression test được viết trước và **fail** trước khi sửa, pass sau khi sửa (báo cáo cá nhân của Duy, mục 3.3) |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

- **Số bug:** 1 bug, ảnh hưởng 3 tool có sẵn (`timeline`, `social_search`, `lookup`).
- **Bug:** `timeline` và `social_search` cắt kết quả bằng `items[: int(limit or 5)]`, `lookup` gửi `int(max_results or 5)`. Khi model gửi số dạng chuỗi `"0"`, chuỗi khác rỗng nên `or 5` không có tác dụng → `limit = 0` → tool trả danh sách rỗng mà không báo lỗi.
- **Cách sửa:** thêm `_clamp(value, default, maximum)` vào `starter_v0/tools/_shared.py` (không phải số hoặc < 1 → `default`, quá lớn → `maximum`); dùng `_clamp(limit, 5, 100)` cho `timeline`/`social_search` và `_clamp(max_results, 5, 20)` cho `lookup`.
- **Regression test:** `test_clamp_handles_string_zero_junk_and_cap`, `test_timeline_string_zero_limit_falls_back_to_default`, `test_social_search_string_zero_limit_falls_back_to_default`, `test_lookup_string_zero_max_results_falls_back_to_default`.

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

- **Provider Gemini lỗi khi chạy preflight/eval (CP1).** Model mặc định `gemini-3.8-flash` trả `503 UNAVAILABLE` ("model is currently experiencing high demand"); thử `gemini-2.5-flash` thì bị `404 NOT_FOUND` ("no longer available to new users"). Cách xử lý: thêm retry có backoff cho lỗi 503/429 trong `starter_v0/providers/gemini_provider.py`, cho phép đổi model qua biến `GEMINI_MODEL`. Tiếp theo thử `gemini-3.5-flash` nhưng quota hết quá nhanh, nên chuyển sang `gemini-3.5-flash-lite` và chạy lại v0 (mất khoảng 30 phút thử và sai). Một lần chạy eval còn bị truyền `--model` sai, phải mất khoảng 20 phút để phát hiện và chạy lại. Cách xử lý: chốt model `gemini-3.5-flash-lite` cho toàn bộ v0–v3 để so sánh công bằng, và kiểm tra trường `model` trong run JSON trước khi ghi vào `version_log.csv`. Run v0 hợp lệ: `provider_error_cases = 0`, `measured_cases = total_cases = 20`.
- **Twitter API (RapidAPI `twitter-api45`) trả `403 Forbidden` / `429 Too Many Requests`** trong lần chạy v0 đầu tiên (model `gemini-3.5-flash`, run đó đã bỏ khi đổi model). Lỗi này không ảnh hưởng điểm eval (eval chấm tool call + args). Trong run v0 chính thức không còn lỗi Twitter; lỗi tool duy nhất là `send` thiếu `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` (case R12), vì nhóm chưa cấu hình Telegram.
- **Hash artifact khác nhau dù nội dung không đổi (CRLF/LF).** `versioning.py` băm byte của file, nên cùng nội dung nhưng khác line ending ra hash khác. Máy Windows (`core.autocrlf=true`) checkout file thành CRLF: `tools.yaml` bản v0–v2 có hash `41a2894f8ad1` (LF) và `e69bc53ed884` (CRLF); `system_prompt.md` bản v2 có `6e4a31497aa1` (LF) và `aeef10d86de9` (CRLF). Vì vậy v1 trông như đổi cả `tools.yaml`, và v3 trông như đổi cả prompt. Cách xử lý: xác nhận bằng `git diff <commit_cũ> <commit_mới> -- <file>` (rỗng = chỉ khác line ending), tính lại hash của bản CRLF cho khớp run JSON, và ghi rõ trong cột `reason` của `version_log.csv`. Cách sửa triệt để cho lần sau: thêm `.gitattributes` với `starter_v0/artifacts/* text eol=lf`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
