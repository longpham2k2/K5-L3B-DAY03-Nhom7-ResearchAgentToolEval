# Báo cáo cá nhân — LeBaNguyen-2A202604100

## 1. Thông tin thành viên

- Họ tên: Lê Bá Nguyên
- MSSV: 2A202604100
- Email: 26ai.nguyenlb2@vinuni.edu.vn

## 2. Phần việc phụ trách

Vai trò **Eval + chat (CP4, CP5)**: viết bộ 10 case eval của nhóm trong `starter_v0/data/eval_group.json`, chạy eval nhóm (`--suite group`) và chat live bằng `chat.py` để lấy transcript. Phạm vi file: `starter_v0/data/eval_group.json`, `starter_v0/transcripts/`.

## 3. Đóng góp cụ thể

### 3.1. Bộ 10 case eval nhóm (`data/eval_group.json`)

Viết đúng 10 case: 5 single turn (`query`) và 5 multi turn (`turns`). Mỗi case có `failure_type`, `expect` và `metadata.what_it_tests`. Case nhắm vào chỗ bộ base (`eval_base.json`) chưa phủ: các tool `papers`, `policy` và 4 tool mới của nhóm.

| Case ID                        | Loại  | Failure type      | Kiểm tra gì                                                                                      | Kỳ vọng                                              |
| ------------------------------ | ----- | ----------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| G01_paper_vs_web_routing       | query | `wrong_tool`      | "Nghiên cứu trên arXiv" phải route sang `papers`, không bị kéo sang `lookup` vì có chữ "gần đây" | `papers`                                             |
| G02_policy_area_topk           | query | `wrong_arg_value` | Hỏi chính sách bảo mật dữ liệu, "chỉ lấy 2 mục"                                                  | `policy(policy_area=data_privacy, top_k=2)`          |
| G03_cooking_out_of_scope       | query | `out_of_scope`    | Hỏi công thức nấu phở, ngoài phạm vi research agent                                              | không gọi tool, từ chối                              |
| G04_clarify_then_social_top    | turns | `missing_info`    | Thiếu chủ đề thì hỏi lại; sau đó chọn tweet "top", 3 tweet                                       | `social_search(search_type=Top, limit=3)`            |
| G05_news_month_limit_carryover | turns | `wrong_arg_value` | Giữ tham số bổ sung qua nhiều lượt: tin trong tháng, 3 kết quả                                   | `lookup(topic=news, timeframe=month, max_results=3)` |
| G06_wiki_definition_routing    | query | `wrong_tool`      | Định nghĩa trên Wikipedia tiếng Việt phải route sang tool mới `wiki`                             | `wiki(lang=vi)`                                      |
| G07_hackernews_routing         | query | `wrong_tool`      | Hỏi cộng đồng Hacker News bàn gì, không phải `social_search` hay `lookup`                        | `hackernews`                                         |
| G08_hackernews_sort_limit      | turns | `wrong_arg_value` | "mới nhất" → `sort=date`, "3 bài" → `limit=3`                                                    | `hackernews(sort=date, limit=3)`                     |
| G09_github_clarify_then_args   | turns | `missing_info`    | Thiếu chủ đề thì hỏi lại; sau đó `sort=updated`, `limit=4`                                       | `github(sort=updated, limit=4)`                      |
| G10_huggingface_sort_limit     | turns | `wrong_arg_value` | "theo lượt thích" → `sort=likes`, "5 model" → `limit=5`                                          | `huggingface(sort=likes, limit=5)`                   |

Nguyên tắc viết `expect`:

- `expect.tool_calls` chỉ chứa tham số cần kiểm tra (so khớp kiểu tập con). Với case chỉ kiểm tra việc chọn tool thì để `"args": {}`. Không ghi giá trị mà model có thể diễn đạt khác nhau (ví dụ từ khóa `query`), để tránh case FAIL oan.
- Case ngoài phạm vi (G03) dùng `no_tool` với `behavior: refuse`, giống R08/R14 của bộ base.
- Tên tool trong `expect` khớp tên đã khai báo trong `artifacts/tools.yaml`, nếu không `run_eval.py` báo lỗi ngay từ đầu.
- 6 case cho tool cũ/core và 4 case cho 4 tool mới (`wiki`, `hackernews`, `github`, `huggingface`), thỏa yêu cầu "ít nhất 1 case route tới tool mới".

### 3.2. Chạy eval nhóm

- Lệnh: `python run_eval.py --provider gemini --model gemini-3.5-flash-lite --version v4 --suite group --eval-cases data/eval_group.json` (chạy từ `starter_v0/`).
- Run hợp lệ: `runs/v4_B_group_gemini_20261110T231401594075.json`, model `gemini-3.5-flash-lite`, `measured_cases = 10/10`, `provider_error_cases = 0`.
- Nhãn `v4` vì bản `tools.yaml` đã có thêm khai báo 4 tool mới (`tools_hash` `64c0eecaf02f`, khác v3).
- Kết quả: **case_accuracy = 0.8 (8/10 PASS)**; `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` đều 0.8.

| Case | Kết quả | Agent đã làm gì |
|---|---|---|
| G01 | PASS | Gọi `papers` |
| G02 | PASS | `policy(policy_area=data_privacy, top_k=2)` |
| G03 | **FAIL** | Gọi `lookup(query="công thức nấu phở bò...")` thay vì từ chối |
| G04 | **FAIL** | Gọi `clarify("Bạn muốn tìm các tweet top về Claude của tài khoản nào?")` thay vì `social_search` |
| G05 | PASS | `lookup(query="chip AI", topic=news, timeframe=month, max_results=3)` |
| G06 | PASS | `wiki(lang=vi)` |
| G07 | PASS | `hackernews` |
| G08 | PASS | `hackernews(sort=date, limit=3)` |
| G09 | PASS | `github(sort=updated, limit=4)` |
| G10 | PASS | `huggingface(sort=likes, limit=5)` |

Cả 5 case route tới tool mới (G06 đến G10) đều PASS, kể cả các case kiểm tra tham số `sort`/`limit` qua nhiều lượt.

**Phân tích 2 case FAIL** (theo `failure_type` của case trong file eval và `actual_tool_calls` trong run JSON):

| Case | Failure type | Actual Tool Calls | What Failed | Hướng sửa |
|---|---|---|---|---|
| G03_cooking_out_of_scope | `out_of_scope` (`unexpected_tool_call`) | `lookup(query="công thức nấu phở bò chuẩn vị Hà Nội", topic=general, timeframe=year)` | Agent coi câu hỏi nấu ăn là câu cần tra web, không nhận ra ngoài phạm vi research agent. Trong `lookup` không có gì cấm tra thông tin ngoài chủ đề nghiên cứu | Thêm rule vào `system_prompt.md`: chỉ làm việc nghiên cứu (tin tức, mạng xã hội, paper, chính sách, repo, model); câu ngoài phạm vi thì từ chối, không gọi tool. Đây là fix thuộc system prompt |
| G04_clarify_then_social_top | `missing_info` (`missing_tool_call`) | `clarify(question="...tweet top về Claude của tài khoản nào?", response_type=text)` | Ở lượt cuối người dùng đã nói rõ chủ đề "Claude" và "top, 3 tweet", nhưng agent hỏi lại "của tài khoản nào" như thể đây là yêu cầu lấy tweet của một người. Đây là hỏi lại thừa, không phải đoán bừa | Làm rõ trong mô tả `social_search`: tìm tweet theo chủ đề không cần tài khoản; `timeline` mới cần tài khoản. Fix thuộc `tools.yaml` |

Lưu ý: hai nhận định "Hướng sửa" ở trên là giả thuyết của mình dựa trên run JSON, chưa kiểm chứng bằng cách sửa và chạy lại. [Nếu nhóm đã sửa và đo lại thì bổ sung kết quả.]

### 3.3. Chat live

- Lệnh: `python chat.py --provider gemini --model gemini-3.5-flash-lite --version v4` (chạy từ `starter_v0/`).
- Transcript: `transcripts/v4_gemini_20261110T231807178159.transcript.json`, 6 lượt, cùng `artifact_version` `v4+paeef10d86de9+t64c0eecaf02f` với run eval nhóm.

| Lượt | Yêu cầu | Tool agent gọi | Kết quả | Nhận xét |
|---|---|---|---|---|
| 1 | "Tin AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news")` → `format` | Trả bản tin có nguồn và link | Yêu cầu thường, route đúng. Điểm yếu: người dùng nói "hôm nay" nhưng agent không điền `timeframe=day`, nên dùng mặc định (tuần) |
| 2 | "Tóm tắt 5 tweet mới nhất" | `clarify(text)` hỏi tài khoản nào | Chờ người dùng | Đúng hành vi: thiếu thông tin thì hỏi lại, không đoán bừa |
| 3 | "Của Elon Musk nhé" | `timeline(screenname="elonmusk", limit=5)` → `format` | Tóm tắt 5 tweet | Giữ đúng `limit=5` từ lượt trước, map đúng handle |
| 4 | "Đăng bản tin này lên Telegram" | `clarify(yes_no)` hỏi có muốn đăng không | Chờ xác nhận, **không** gọi `send` | Đúng ranh giới: xin xác nhận trước khi gửi |
| 5 | "Dân lập trình trên Hacker News bàn gì về Rust?" | `hackernews(query="Rust")` | Trả các chủ đề thảo luận kèm link | Route đúng sang tool mới |
| 6 | "Tìm tweet về Claude" | `social_search(query="Claude AI", search_type="Latest")` | Trả các tweet về Claude | Không hỏi lại thừa; khác với G04 trong eval, nơi agent hỏi "tài khoản nào" |

Nhận xét chung:

- Đủ 3 loại lượt README yêu cầu: yêu cầu thường (lượt 1), thiếu thông tin rồi bổ sung (lượt 2 và 3), yêu cầu gửi (lượt 4). Thêm 1 lượt cho tool mới (lượt 5).
- Chưa thử câu ngoài phạm vi (G03, nấu phở) trong chat live, nên chưa biết hành vi này có lặp lại ngoài eval.
- Lượt 4 dừng ở bước xác nhận, chưa thử trả lời "có" để xem `send` hoạt động. [Bổ sung nếu bạn đã thử.]
- Lượt 6 cho thấy G04 có thể không ổn định: cùng ý hỏi (tweet theo chủ đề) lần này agent làm đúng, trong khi eval nhiều lượt thì hỏi lại thừa. Cần chạy lại vài lần trước khi kết luận.

## 4. Bằng chứng

- File/commit/PR:
  - `starter_v0/data/eval_group.json` (10 case G01 đến G10)
  - Commit `91bb1b6 feat: add 10 group eval cases`
  - `starter_v0/runs/v4_B_group_gemini_20261110T231401594075.json` (run eval nhóm, 8/10 PASS, 0 lỗi provider)
  - `starter_v0/transcripts/v4_gemini_20261110T231807178159.transcript.json` (chat live, 6 lượt)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng **Claude** để giải thích `allowed_failure_types`, phân biệt các loại lỗi, và soạn bản nháp 10 case theo mẫu của `eval_base.json`.
  - Tự kiểm tra: đối chiếu tên tool và tên tham số của từng case với `artifacts/tools.yaml` và `TOOL.md` của tool; kiểm tra file JSON hợp lệ, đủ 10 case (5 `query`, 5 `turns`) và `failure_type` nằm trong `allowed_failure_types`.

## 5. Tự đánh giá

- **Đã làm được:** viết đủ 10 case theo yêu cầu CP4 (5 single turn, 5 multi turn), phủ 4 loại `failure_type` (`wrong_tool`, `wrong_arg_value`, `missing_info`, `out_of_scope`), có case route tới cả 4 tool mới của nhóm. Chạy eval nhóm hợp lệ trên v4: 8/10 PASS, 0 lỗi provider; cả 5 case tool mới đều PASS.
- **Điều eval cho thấy:** 2 case FAIL (G03, G04) chỉ ra hai điểm yếu thật của agent mà bộ base chưa bắt: gọi tool cho câu ngoài phạm vi, và hỏi lại thừa khi người dùng đã đủ thông tin. Nhờ vậy nhóm có giả thuyết rõ cho vòng sửa tiếp theo: một fix thuộc `system_prompt.md`, một fix thuộc `tools.yaml`.
- **Chat live:** 6 lượt, agent hỏi lại đúng khi thiếu thông tin (lượt 2), xin xác nhận trước khi gửi Telegram (lượt 4), và route đúng sang tool mới `hackernews` (lượt 5). Một điểm yếu quan sát được: lượt 1 bỏ sót `timeframe=day` dù người dùng nói "hôm nay".
- **Còn thiếu:** bảng B3 và B4 trong `group_report.md` chưa điền. Hai nhận định "hướng sửa" ở mục 3.2 chưa được kiểm chứng bằng cách sửa rồi chạy lại.
- **Điều rút ra:** eval đo model chọn tool và điền tham số đúng không, còn unit test đo code của tool, hai loại lỗi khác nhau nên cần cả hai. Khi viết `expect`, chỉ nên chấm những tham số thật sự chắc chắn, vì chấm cả giá trị diễn đạt tự do sẽ làm case FAIL oan.
