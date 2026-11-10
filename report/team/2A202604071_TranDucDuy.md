# Báo cáo cá nhân — TranDucDuy-2A202604071

## 1. Thông tin thành viên

- Họ tên: Trần Đức Duy
- MSSV: 2A202604071
- Email: 26ai.duytd2@vinuni.edu.vn

## 2. Phần việc phụ trách

Vai trò **#4 — Tool dev + test (CP3)**: viết tool mới, `TOOL.md`, đăng ký tool, viết unit test và giữ `pytest` xanh. Phạm vi: `starter_v0/tools/`, `starter_v0/tests/`.

## 3. Đóng góp cụ thể

### 3.1. Bốn tool mới (không cần API key)

| Tool | Hàm | Nguồn | Tham số | Xử lý input xấu từ model |
|---|---|---|---|---|
| `wiki` | `wiki_search` | Wikipedia (MediaWiki API) | `query`, `lang`, `limit` | `lang` ngoài `en`/`vi` → `en`; `limit` ép về 1–20 |
| `hackernews` | `hackernews_search` | Hacker News (Algolia API) | `query`, `sort`, `limit` | `sort` ngoài `relevance`/`date` → `relevance`; bài không có link → dùng link thảo luận HN |
| `github` | `github_search` | GitHub Search API | `query`, `sort`, `limit` | `sort` ngoài `stars`/`updated`/`best_match` → `stars`; `best_match` thì không gửi tham số sort |
| `huggingface` | `hf_models` | Hugging Face Hub API | `query`, `sort`, `limit` | `sort` ngoài `downloads`/`likes`/`lastModified` → `downloads`; API trả dữ liệu lạ → `items` rỗng, không crash |

Quy ước chung của cả 4 tool:

- Mọi tham số có giá trị mặc định; toàn bộ hàm bọc `try/except` và trả `err(...)`, không raise.
- `query` rỗng → trả error dict ngay, không gọi mạng.
- `limit` dạng chuỗi (`"0"`, `"abc"`) hoặc quá lớn (`500`) được ép về giá trị hợp lệ bằng hàm `_clamp` (thêm vào `tools/_shared.py`).
- Mỗi tool có `TOOL.md` đúng frontmatter (`name`, `track`, `kind`, `provider`, `requires_env`, `inputs`, `outputs`, `side_effect`) và được đăng ký trong `TOOL_FUNCTIONS` (`tools/__init__.py`).
- Đã chạy thật cả 4 tool với API thật: đều trả kết quả đúng, không cần key.

### 3.2. Unit test (`tests/test_tools_todo.py`)

- **Tool mới:** 18 test (wiki 4, hackernews 4, github 5, huggingface 5), đủ 3 loại: happy path (assert cả request gửi đi lẫn kết quả map ra), input xấu từ model, nhánh lỗi (HTTP 503/403, mất mạng, query rỗng).
- **Challenge:** viết xong 14 stub còn `skip` của tool có sẵn (clarify, format, send, lookup, fetch, timeline, social_search, policy) → `test_tools_todo.py` không còn test nào bị skip.
- **Challenge+:** phát hiện và sửa bug trong tool có sẵn (xem 3.3).
- Kết quả: `pytest` toàn bộ **98 passed, 0 failed, 0 skipped**; `tests/test_tool_contract.py` xanh.

### 3.3. Bug tìm được bằng unit test (Challenge+, dùng cho B5)

- **Bug:** `timeline`, `social_search` dùng `items[: int(limit or 5)]`; `lookup` gửi `int(max_results or 5)`. Model hay gửi số dạng chuỗi; chuỗi `"0"` là truthy nên `or 5` không có tác dụng → `limit = 0` → tool trả danh sách rỗng mà không báo lỗi.
- **Cách làm:** viết regression test trước (3 test **fail**, chứng minh bug), sau đó sửa bằng `_clamp(limit, 5, 100)` cho timeline/social_search và `_clamp(max_results, 5, 20)` cho lookup → test pass, giữ lại làm regression test.
- **Vì sao eval không bắt được:** eval chỉ chấm tên tool và args model gửi; với `limit="0"` model gọi đúng tool nên eval vẫn PASS, nhưng kết quả tool rỗng. Chỉ unit test (kiểm tra code của tool) mới bắt được.

### 3.4. Phối hợp với nhóm

- Soạn sẵn đoạn khai báo 4 tool mới cho `artifacts/tools.yaml` và gửi người #3 phụ trách file này; đã ghép thử với `tools.yaml` hiện tại và chạy kiểm tra contract (tên tham số khớp chữ ký hàm, có `TOOL.md`, mô tả không rỗng) → đạt.
- Chạy thử baseline v0 trên máy (`--provider gemini --model gemini-3.5-flash-lite`): 12/20 case PASS (case_accuracy 0.60). Run được lưu trong `starter_v0/runs/`, chưa commit, chờ nhóm thống nhất người nộp run v0.

## 4. Bằng chứng

- File:
  - `starter_v0/tools/wiki/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/github/`, `starter_v0/tools/huggingface/` (`tool.py` + `TOOL.md`)
  - `starter_v0/tools/__init__.py` (đăng ký 4 tool), `starter_v0/tools/_shared.py` (`_clamp`, `USER_AGENT`)
  - `starter_v0/tools/timeline/tool.py`, `starter_v0/tools/social_search/tool.py`, `starter_v0/tools/lookup/tool.py` (sửa bug)
  - `starter_v0/tests/test_tools_todo.py`
- Commit/PR: (điền mã commit/PR sau khi push)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng **Claude Code** để viết code 4 tool, unit test, bản sửa bug và đoạn khai báo `tools.yaml`.
  - Tự kiểm tra: chạy regression test trước khi sửa (3 failed) và sau khi sửa (pass); chạy `pytest` toàn bộ (98 passed, 0 failed, 0 skipped); chạy contract test trên bản ghép `tools.yaml` + đoạn khai báo mới; gọi thật từng tool mới với API thật để xác nhận kết quả; quét `runs/` để chắc không có API key trước khi commit.

## 5. Tự đánh giá

- **Đã làm được:** đủ yêu cầu bắt buộc của CP3 cho phần tool (≥ 1 tool mới, ≥ 3 test/tool, `pytest` 0 failed) và cả hai bonus về test (Challenge: 0 skipped; Challenge+: tìm, sửa bug và giữ regression test).
- **Còn phụ thuộc nhóm:** để 4 tool được tính bonus "≥ 4 tool", cần người #3 khai báo 4 tool trong `tools.yaml` và mỗi tool có ít nhất 1 eval case trong `data/eval_group.json`.
- **Điều rút ra:** unit test kiểm tra code của tool, eval kiểm tra lựa chọn của model — hai loại lỗi khác nhau nên cần cả hai. Tool trả error dict thay vì raise để vòng lặp agent không bị dừng, model đọc được lỗi và có thể thử lại hoặc báo người dùng.
