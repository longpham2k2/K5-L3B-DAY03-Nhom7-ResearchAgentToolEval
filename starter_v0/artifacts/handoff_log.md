# Handoff log

Sổ bàn giao giữa các thành viên. Mỗi khi có **run mới** hoặc thay đổi cần người khác xử lý tiếp, người bàn giao thêm một mục mới lên **đầu** danh sách bên dưới.

- Người nhận (thường là #1 Eval runner) đọc mục mới, ghi dòng tương ứng vào `version_log.csv`, rồi đánh dấu `[x] Đã xử lý`.
- Không sửa mục cũ của người khác; nếu cần đính chính, thêm mục mới.

## Lưu ý chung: hash khác nhau do line ending (CRLF/LF)

`versioning.py` băm **byte** của file, nên cùng một nội dung nhưng khác line ending sẽ ra hash khác:

| File | Hash khi LF | Hash khi CRLF | Nội dung |
|---|---|---|---|
| `system_prompt.md` (bản v2) | `6e4a31497aa1` | `aeef10d86de9` | giống hệt nhau |
| `tools.yaml` (bản v0–v2) | `41a2894f8ad1` | `e69bc53ed884` | giống hệt nhau |

Máy Windows có `core.autocrlf=true` sẽ checkout file thành CRLF. Vì vậy:

- Khi hash đổi mà `git diff` của file đó **rỗng**, đó là do line ending, không phải thay đổi thật. Ghi chú vào cột `reason` của `version_log.csv`.
- Cách xác nhận nhanh: `git diff <commit_cũ> <commit_mới> -- starter_v0/artifacts/system_prompt.md` không có output.
- Cách sửa triệt để (đề xuất cho #1): thêm `.gitattributes` ở root với dòng `starter_v0/artifacts/* text eol=lf`, để mọi máy băm cùng một bản.

---

## Mục bàn giao

### 2026-11-10 — Khai báo 4 tool mới trong tools.yaml → người làm v4 (+ #1, #5)

- **Người bàn giao:** #3 Tool declaration (invzble zone)
- **Người nhận:** người làm v4; #1 (chạy eval); #5 (eval_group)
- **Commit:** `feat(tools.yaml): declare 4 team tools (hackernews, github, huggingface, wiki)`
- **Đã làm:** thêm block khai báo `hackernews`, `github`, `huggingface`, `wiki` ở cuối `tools.yaml` (code do #4 viết). Tên, tham số, enum khớp code; mỗi description có "khi nào dùng / KHÔNG dùng". `pytest` 119 passed (contract test giờ kiểm tra cả 4 tool).
- **Chưa làm:** chưa chạy eval nào với thay đổi này; không sửa description của 10 tool cũ (kể cả `lookup`).
- **⚠ Lưu ý cho người làm v4:**
  - `tools_hash` hiện là `64c0eecaf02f` (CRLF), khác v3 (`675b7383425c`). Thay đổi này **sẽ nằm trong v4**. Nếu v4 sửa thêm gì khác (prompt, description tool cũ…) thì v4 đổi hai thứ cùng lúc — cân nhắc chạy base ngay với riêng thay đổi này trước, hoặc ghi rõ trong `hypothesis`.
  - Mốc so sánh base: v3 = 0.90, fail đúng 2 case R12, M06. Case khác chuyển sang FAIL = regression do tool mới "giành" câu hỏi (vd R06 "tin công nghệ" bị route sang `hackernews`).
- **Lưu ý cho #5:** giờ đã có thể thêm case route tới 4 tool mới vào `eval_group.json` (trước commit này contract test sẽ đỏ vì tool chưa khai báo). Nên có thêm ít nhất 1 case đối chứng, vd "tin tức công nghệ hôm nay" phải vẫn là `lookup(topic="news")`, không phải `hackernews`.
- **Trạng thái:** [ ] Đã xử lý

### 2026-11-10 — v3 (tools.yaml) → #1

- **Người bàn giao:** #3 Tool declaration (invzble zone)
- **Người nhận:** #1 Eval runner
- **Việc cần làm:** thêm dòng `v3` vào `version_log.csv`
- **Commit:** `feat(v3): add arg conventions to tool parameter descriptions`
- **Run file:** `runs/v3_B_base_gemini_20261110T195449033306.json` (20/20 measured, 0 provider error — hợp lệ)
- **⚠ Lưu ý hash:** `prompt_hash` của v3 là `aeef10d86de9`, của v2 là `6e4a31497aa1`, nhưng **`system_prompt.md` không đổi nội dung** — chỉ khác line ending (xem bảng trên). Bắt buộc ghi rõ điều này trong cột `reason`, nếu không v3 trông như đổi cả prompt lẫn tools.
- **Trạng thái:** [ ] Đã xử lý

Giá trị cho dòng v3:

```text
version: v3
author: invzble zone (#3)
changed_artifact: tools.yaml
artifact_version: v3+paeef10d86de9+t675b7383425c
prompt_hash: aeef10d86de9
tools_hash: 675b7383425c
reason: Chỉ sửa description tham số trong tools.yaml (lookup.query/topic/timeframe, clarify.response_type + thêm vào required, send.confirmed). system_prompt.md KHÔNG đổi nội dung so với v2: prompt_hash khác (aeef10d86de9 vs 6e4a31497aa1) chỉ do line ending CRLF. Model gemini-3.5-flash-lite.
hypothesis: Sau v2 routing đã 100%, 6 case fail còn lại đều là wrong_arg_value (query bị nhồi từ thời gian/loại tin; clarify thiếu/sai response_type). Thêm quy ước args vào description tham số sẽ tăng argument_accuracy.
metric_before: 0.7
metric_after: 0.9
run_file: runs/v3_B_base_gemini_20261110T195449033306.json
```

Kết quả để tham khảo khi viết B1/B2:

| Metric | v2 | v3 |
|---|---:|---:|
| case_accuracy | 0.70 | 0.90 |
| tool_routing_accuracy | 1.00 | 1.00 |
| argument_accuracy | 0.70 | 0.90 |
| multiturn_accuracy | 0.67 | 0.83 |

- Case được sửa: R03, R11, R13, M02.
- Còn fail: **R12** (`clarify` dùng `text` hỏi nội dung bản tin thay vì `yes_no` — hỏi lại nội dung cũng hợp lý, ứng viên cho mục "failure cần review thủ công" ở B6), **M06** (`query="OpenAI tin tức"` — từ tiếng Việt vẫn lọt vào query ở hội thoại 3 lượt).
