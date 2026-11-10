# Báo cáo cá nhân — PhamNgocLong-2A202604111

## 1. Thông tin thành viên

- Họ tên: Phạm Ngọc Long
- MSSV: 2A202604111
- Email: 26ai.longpn@vinuni.edu.vn

## 2. Phần việc phụ trách
- Setup .env, preflight, update version_log.
- Theo dõi tiến độ làm bài của team và đốc thúc cổ vũ.
- Check và đảm bảo team làm đúng hình thức bài nộp, theo checklist trong README.MD và SUBMISSION.md
...

## 3. Đóng góp cụ thể
- Chia việc cho team 6 người, trong đó: Tôi, nhóm trưởng, chịu trách nhiệm bao quát và đảm bảo team làm đúng tiến độ, một member sửa system prompt, một member sửa tool, một member viết tool và unit test, một member viết data eval và một member viết web.
- Cùng Thắng và Bào làm lại phần sửa system prompt và tools.yaml; làm rõ đề bài (sửa theo từng tiêu chí, không gộp lại, bao gồm bỏ prompt nguy hiểm, thêm routing, và cuối cùng là sửa tool description, chạy eval theo từng version)
...

## 4. Bằng chứng

- File/commit/PR:

| Commit / PR | Nội dung | File chính |
|---|---|---|
| `eaa1df7` (cp0) | Setup nhóm: điền `TEAM.md`; sửa provider Gemini (retry khi lỗi 503/429, đổi model qua biến `GEMINI_MODEL`); sửa `env_loader.py` bỏ comment cuối dòng trong `.env` | `TEAM.md`, `starter_v0/providers/gemini_provider.py`, `starter_v0/env_loader.py` |
| `6d7b61e` (feat(cp1): add v0 eval run) | Chạy baseline v0 (`gemini-3.5-flash-lite`, 20/20 case đo được, 0 lỗi provider, `case_accuracy` 0.65), ghi dòng v0 vào version log | `starter_v0/runs/v0_B_base_gemini_20261110T181200902036.json`, `starter_v0/artifacts/version_log.csv` |
| `b568b62` (update version_log) | Tổng hợp run v1, v2 của Thắng vào version log (hash, giả thuyết, metric trước/sau) | `starter_v0/artifacts/version_log.csv` |
| `28c25c5` (update group report) | Điền provider/model, dòng v0 bảng B1, bảng B2 (Failure Analysis 7 case FAIL), mục 5 (khó khăn với Gemini/Twitter API); cập nhật checklist README | `report/team/group_report.md`, `README.md` |
| PR #1 (`07ed325`) | Merge PR của Duy: 4 tool mới (`github`, `hackernews`, `huggingface`, `wiki`) + unit test | `starter_v0/tools/`, `starter_v0/tests/test_tools_todo.py` |
| PR #2 (`e8b9f57`) | Merge PR của Duy: sửa báo cáo cá nhân | `report/team/2A202604071_TranDucDuy.md` |

- Review trực tiếp với Thắng (không qua GitHub nên không có comment review). Bằng chứng gián tiếp trong git history:
  - `b26ce2c` (19:02): v1 ban đầu gộp nhiều thay đổi (bỏ chỉ dẫn xấu + routing + quy ước args), đạt 1.0 nhưng vi phạm "mỗi version một giả thuyết".
  - Sau khi review, v1 được làm lại chỉ bỏ chỉ dẫn xấu (`b6763ae`, 19:34), run cũ bị xóa và thay bằng `runs/v1_B_base_gemini_20261110T193341337170.json`.
  - v2 chỉ thêm routing (`3a0640f`, 19:45).
  - Version log được cập nhật theo các run mới (`b568b62`, 19:47).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

  - Dùng Claude Code để xử lý lỗi Gemini (`503 UNAVAILABLE` với `gemini-3.8-flash`, `404 NOT_FOUND` với `gemini-2.5-flash`): thêm retry và biến `GEMINI_MODEL`. Tự kiểm tra bằng `python scripts/preflight_provider.py --provider gemini`. Chọn model theo cách thử và sai: thử `gemini-3.5-flash` trước (run v0 đầu tiên) nhưng quota hết quá nhanh, nên chuyển sang `gemini-3.5-flash-lite` và chạy lại v0; mất khoảng 30 phút để tìm ra model dùng được. Sau đó Thắng chạy eval với tham số `--model` sai nên mất thêm khoảng 20 phút để phát hiện và chạy lại; từ đó nhóm thống nhất mọi run v0–v3 dùng cùng một model `gemini-3.5-flash-lite`.
  - Dùng Claude Code để đọc run JSON, tổng hợp kết quả v0–v2 vào `version_log.csv` và bảng B2. Tự kiểm tra: đối chiếu hash và metric với `summary` trong từng run JSON; kiểm tra `prompt_hash` khớp với `system_prompt.md` ở đúng commit; xác nhận `tools_hash` khác v0 chỉ do line ending CRLF chứ `tools.yaml` không đổi nội dung.
  - Xác nhận `starter_v0/data/eval_base.json` không bị sửa: `git diff c68da4c -- starter_v0/data/eval_base.json` rỗng, và input/expect của 20 case trong các run v0–v2 trùng với file gốc.

## 5. Tự đánh giá

...
