# Báo cáo cá nhân — Nguyễn Khắc Bào - 2A202604072

## 1. Thông tin thành viên

- Họ tên: Nguyễn Khắc Bào
- MSSV: 2A202604072
- Email: 26ai.baonk@vinuni.edu.vn
- GitHub: `invzble-z`
- Vai trò trong nhóm: #3 — Tool declaration (phụ trách `starter_v0/artifacts/tools.yaml`)

## 2. Phần việc phụ trách

- Sở hữu file `starter_v0/artifacts/tools.yaml`: viết mô tả tool và quy ước tham số để model chọn đúng tool, truyền đúng args.
- Phối hợp với #2 (Prompt engineer) để mỗi version chỉ đổi **một** artifact: v1, v2 sửa `system_prompt.md` (#2); **v3 sửa `tools.yaml` (tôi)**.
- Khai báo 4 tool mới do #4 viết code (`hackernews`, `github`, `huggingface`, `wiki`) vào `tools.yaml`, giữ khớp với code để contract test xanh.
- Bàn giao kết quả cho #1 (ghi `version_log.csv`), người làm v4 và #5 (eval nhóm) qua `starter_v0/artifacts/handoff_log.md`.

## 3. Đóng góp cụ thể

Mọi run dùng cùng provider/model `gemini` / `gemini-3.5-flash-lite`, cùng `data/eval_base.json`.

### 3.1. v3 — quy ước args trong mô tả tham số

**Phân tích đầu vào (run v2):** sau v2, `tool_routing_accuracy = 1.0` (chọn đúng tool 20/20) nhưng còn 6 case FAIL, **tất cả là `wrong_arg_value`**:

| Case | Model gọi (v2) | Vấn đề |
|---|---|---|
| R03, R13, M02, M06 | `lookup(query="AI news today")`, `"robotics news today"`, `"OpenAI news"`… | `query` bị nhồi từ chỉ loại tin / thời gian |
| R11 | `clarify(question=…)` | bỏ trống `response_type` (kỳ vọng `text`) |
| R12 | `clarify(question=…)` | bỏ trống `response_type` (kỳ vọng `yes_no`) |

Trong `tools.yaml` lúc đó, mô tả tham số chỉ có một từ (`"Truy vấn"`, `"Kiểu trả lời"`, `"Cờ xác nhận"`), không có quy ước nào.

**Giả thuyết:** routing đã đúng, lỗi còn lại nằm ở args vì không chỗ nào nói quy ước. Thêm quy ước vào **mô tả tham số** trong `tools.yaml` sẽ tăng `argument_accuracy`.

**Thay đổi** (chỉ sửa mô tả tham số, không đổi tên tool/tham số, không sửa `system_prompt.md`):

| Tham số | Trước | Sau (tóm tắt) |
|---|---|---|
| `lookup.query` | "Truy vấn" | Chỉ từ khóa chủ đề; không thêm news/tin tức/today/hôm nay vì đã có `topic`, `timeframe` |
| `lookup.topic` | "Phân loại" | `news` khi hỏi tin tức/thời sự; `general` cho tra cứu chung |
| `lookup.timeframe` | "Khoảng thời gian" | hôm nay → `day`, tuần này → `week`…; lượt sau không đổi thì giữ giá trị cũ |
| `clarify.response_type` | "Kiểu trả lời" | Luôn điền; `text` = xin thông tin thiếu; `yes_no` = xác nhận trước khi gửi/đăng. Thêm vào `required` |
| `send.confirmed` | "Cờ xác nhận" | Chỉ `true` khi user đã đồng ý ở lượt trước; chưa có thì gọi `clarify(yes_no)` |

Ví dụ trong mô tả dùng chủ đề **không có trong eval** ("chip bán dẫn") để tránh học thuộc đáp án.

**Kết quả** — run `runs/v3_B_base_gemini_20261110T195449033306.json` (20/20 case đo được, 0 lỗi provider):

| Metric | v2 | v3 |
|---|---:|---:|
| case_accuracy | 0.70 | **0.90** |
| tool_routing_accuracy | 1.00 | 1.00 |
| argument_accuracy | 0.70 | **0.90** |
| multiturn_accuracy | 0.67 | **0.83** |

- Sửa được 4 case: R03, R11, R13, M02. Routing không giảm.
- Còn FAIL:
  - **R12** — `clarify(response_type="text")` hỏi lại nội dung bản tin thay vì `yes_no`. User nói "đăng bản tin này" mà không đưa nội dung, nên hỏi lại nội dung cũng hợp lý → đây là case nên review thủ công thay vì chỉ dựa vào chấm tự động.
  - **M06** — `lookup(query="OpenAI tin tức")`: ở hội thoại 3 lượt, từ tiếng Việt "tin tức" vẫn lọt vào `query` dù mô tả đã liệt kê từ này.

### 3.2. Khai báo 4 tool mới

- Thêm `hackernews`, `github`, `huggingface`, `wiki` vào cuối `tools.yaml`. Tên, tham số và enum (`sort`, `lang`) lấy đúng theo code của #4 trong `tools/<tên>/tool.py`; `limit` ghi rõ khoảng 1–20 theo hàm `_clamp`.
- Mỗi mô tả có "làm gì / khi nào dùng / KHÔNG dùng", chỉ sang tool đúng (`lookup`, `social_search`, `papers`) để tool mới không "giành" câu hỏi tin tức của bộ base.
- **Tách khỏi v3:** khối khai báo được viết trước nhưng tôi tạm cất (`git stash`) khi làm v3, để v3 chỉ kiểm chứng một giả thuyết (quy ước args). Sau khi v3 có run mới đưa lại vào; việc đo thay đổi này thuộc v4 (người khác phụ trách).
- `pytest`: 99 → 119 passed (contract test tự kiểm tra thêm 4 tool: có implementation, tham số khớp signature, có `TOOL.md` đúng tên).

### 3.3. Phát hiện lỗi hash do line ending và lập sổ bàn giao

- Phát hiện `prompt_hash` / `tools_hash` đổi giữa các run dù nội dung file không đổi. Kiểm tra bằng cách tính lại SHA-256 của file ở dạng LF và CRLF: cùng nội dung nhưng `system_prompt.md` cho `6e4a31497aa1` (LF) và `aeef10d86de9` (CRLF); `tools.yaml` v0–v2 cho `41a2894f8ad1` / `e69bc53ed884`. Nguyên nhân: `versioning.py` băm byte của file, máy Windows có `core.autocrlf=true` checkout file thành CRLF.
- Hệ quả: run v3 có `prompt_hash` khác v2 dù prompt không đổi — nếu không ghi chú, v3 trông như đổi cả prompt lẫn tools.
- Tạo `starter_v0/artifacts/handoff_log.md`: ghi chú chung về CRLF (cách nhận biết, cách sửa bằng `.gitattributes`), mục bàn giao v3 cho #1 kèm giá trị từng cột của dòng v3, và mục bàn giao 4 tool mới cho người làm v4 và #5 (thứ tự: phải khai báo tool trong `tools.yaml` trước khi thêm case vào `eval_group.json`, nếu không contract test sẽ đỏ).

## 4. Bằng chứng

- Commit:
  - `b02cf90` — feat(v3): add arg conventions to tool parameter descriptions (`tools.yaml` + run v3)
  - `117b59a` — feat(tools.yaml): declare 4 team tools (hackernews, github, huggingface, wiki)
  - `f1a8f1e` — docs: add handoff log for v3 and CRLF hash note
  - `91df6a1` — docs(handoff): hand off 4-tool declaration to v4 owner, #1 and #5
- File:
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/runs/v3_B_base_gemini_20261110T195449033306.json`
  - `starter_v0/artifacts/handoff_log.md`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng **Claude Code** để đọc tài liệu lab và code tool, tổng hợp case FAIL từ run JSON, soạn nháp mô tả trong `tools.yaml`, tính lại hash để kiểm tra lỗi line ending, và thực hiện thao tác git (commit, stash, pull, push).
  - Tự kiểm tra:
    - Chạy `pytest tests/test_tool_contract.py` và toàn bộ `pytest` sau mỗi lần sửa `tools.yaml` (99 passed sau v3; 119 passed sau khi khai báo 4 tool).
    - Kiểm tra run v3 hợp lệ: `summary.provider_error_cases == 0`, `measured_cases == total_cases == 20`, cùng model với v0–v2.
    - So sánh từng case giữa v2 và v3 (không chỉ nhìn tổng điểm) để xác định case được sửa và case còn FAIL.
    - Đối chiếu khai báo 4 tool với signature và enum trong `tools/<tên>/tool.py`.
    - Xác nhận hash lệch là do line ending: `git diff` của `system_prompt.md` giữa v2 và v3 rỗng, và hash tính lại ở dạng LF khớp với hash của run v2.

## 5. Tự đánh giá


**Điều làm được**

- v3 có giả thuyết rõ, xuất phát từ dữ liệu thật: đọc run v2 thấy routing đã 1.0 và cả 6 case FAIL đều là `wrong_arg_value`, nên chỉ sửa mô tả tham số. Kết quả `case_accuracy` 0.70 → 0.90, routing không giảm.
- Giữ được nguyên tắc "mỗi version một thay đổi": tạm cất khối khai báo 4 tool khi làm v3, không sửa `system_prompt.md` của #2.
- Phát hiện lỗi hash do line ending trước khi nó làm sai `version_log.csv`, và để lại cách xử lý cho cả nhóm trong `handoff_log.md`.

**Điều chưa làm được / hạn chế**

- Ban đầu tôi dự đoán các case cần sửa (R02, R05–R07) chỉ dựa vào nội dung eval, chưa đọc run v0; thực tế các case đó đã PASS từ v0. Bài học: phải đọc run JSON trước khi đặt giả thuyết, không đoán.
- Mới viết lại mô tả **tham số**; mô tả cấp tool của 9 tool cũ vẫn là một dòng, chưa có "khi nào dùng / không dùng" như rubric C2 yêu cầu. Việc này cần làm ở version sau.
- Còn 2 case FAIL (R12, M06). Với R12, tôi chưa chắc lỗi thuộc model hay thuộc cách chấm, mới dừng ở mức ghi nhận để review thủ công.
- v3 chỉ có một run trên một model. Tôi chưa chạy lại để biết điểm dao động bao nhiêu giữa các lần chạy, nên mức tăng 0.20 (4 case) chưa được kiểm chứng lặp lại.

**Bài học rút ra**

- Prompt quyết định *chọn tool nào*, còn mô tả tham số trong `tools.yaml` quyết định *truyền args gì*. Lỗi `wrong_arg_value` nên sửa ở mô tả tham số trước.
- Chấm tự động không phải lúc nào cũng đúng ý người dùng (R12): cần đọc từng case FAIL, không chỉ nhìn tổng điểm.
- Hash file là bằng chứng của version, nên phải hiểu nó được tính thế nào; nếu không, một chi tiết như CRLF có thể làm sai cả bảng version.
- Khi nhiều người cùng sửa một vòng tối ưu, cần một nơi bàn giao bằng văn bản (handoff log) để người sau biết thay đổi nào thuộc version nào.

**Nếu có thêm thời gian**

- Viết lại mô tả cấp tool cho 9 tool cũ và đo trên bộ extension (`policy`, `papers` có mô tả mơ hồ nhất).
- Thử thêm ví dụ tiếng Việt vào mô tả `lookup.query` để xem M06 có hết lỗi không.
- Chạy lại v3 thêm 1–2 lần để biết điểm dao động bao nhiêu.
