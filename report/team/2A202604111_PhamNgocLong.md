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

  - Dùng Claude Code để xử lý lỗi Gemini (`503 UNAVAILABLE` với `gemini-3.8-flash`, `404 NOT_FOUND` với `gemini-2.5-flash`): thêm retry và biến `GEMINI_MODEL`. Tự kiểm tra bằng `python scripts/preflight_provider.py --provider gemini`. Chọn model theo cách thử và sai: thử `gemini-3.5-flash` trước (run v0 đầu tiên) nhưng quota hết quá nhanh, nên chuyển sang `gemini-3.5-flash-lite` và chạy lại v0; mất khoảng 30 phút để tìm ra model dùng được. Sau đó Thắng chạy eval với tham số `--model` sai nên mất thêm khoảng 20 phút để phát hiện và chạy lại; từ đó nhóm thống nhất mọi run v0–v4 dùng cùng một model `gemini-3.5-flash-lite`.
  - Dùng Claude Code để đọc run JSON và tổng hợp kết quả v0–v4 vào `version_log.csv`. Tự kiểm tra: đối chiếu hash và metric với `summary` trong từng run JSON; kiểm tra `prompt_hash`/`tools_hash` khớp với `system_prompt.md`/`tools.yaml` ở đúng commit; xác nhận hash khác nhau giữa các máy chỉ do line ending CRLF (tính lại hash bản CRLF cho khớp run JSON, `git diff` của file rỗng). Với v3, đối chiếu giá trị Bào bàn giao với run JSON trước khi ghi. Với v4, ghi rõ quyết định của nhóm đo trên group suite thay vì base suite.
  - Dùng Claude Code để soạn các phần của `group_report.md` từ dữ liệu thật: A1 (mô tả agent, lệnh chạy UI, link deploy), A2 (14 tool), mục 3 (giải pháp), B1 (bảng version v0–v4 và metric từng bước, case sửa được / bị hỏng), B2 (failure analysis v0), B3 (10 case group eval), B4 (transcript v4), B5a/B5 (tool mới, unit test, UI, test challenge), mục 5 (khó khăn). Tự kiểm tra: mọi số liệu lấy từ run JSON, transcript và `git log`, không tự điền; các case sửa được / bị hỏng giữa các version được tính lại bằng script từ run JSON; nội dung về deploy (link Cloudflare Tunnel, máy của Tuấn tắt) và thời gian xử lý lỗi model là thông tin tôi cung cấp; tự đọc lại từng phần trước khi commit.
  - Dùng Claude Code để kiểm tra theo checklist `SUBMISSION.md`/`RULES.md` trước khi nộp:
    - `eval_base.json` và `eval_research_extension.json` không bị sửa: SHA-256 trùng bản starter `c68da4c`, và input/expect của 20 case trong các run v0–v3 trùng file gốc.
    - Không commit secret: `.env` chưa từng được commit; quét toàn bộ lịch sử git theo mẫu key (Gemini, OpenAI, OpenRouter, Anthropic, Tavily, Firecrawl, Telegram, GitHub, Hugging Face) → 0 kết quả. Lần quét đầu có kết quả giả (chuỗi `sk-` trong URL bài báo như "ri**sk-**behavioral"); đã siết mẫu tìm và thử lại với một mẫu biết chắc có để xác nhận lệnh tìm hoạt động.
    - Chạy lại `pytest` trong môi trường ảo riêng: 119 passed, 0 failed, 0 skipped.
    - Kiểm tra unit test của 4 tool mới theo rubric (≥ 3 test/tool, không gọi mạng thật, có assert, trả error dict) và group eval theo C5 (5 single + 5 multi turn, có `what_it_tests`, mỗi tool mới có case route tới).
  - Những chỗ AI làm sai và tôi đã sửa: AI đoán model `gemini-2.5-flash` thay cho model bị 503 nhưng model này không còn cho người dùng mới (404), nên phải đổi lại; dòng `GEMINI_MODEL` AI thêm vào `.env.example` có comment cuối dòng làm hỏng tên model (lỗi 404 rỗng), sau đó sửa `env_loader.py` để bỏ comment cuối dòng. Bài học: kiểm tra lại mọi thay đổi của AI bằng chạy thật (preflight, eval), không tin ngay kết quả.

## 5. Tự đánh giá
- Đã làm được: 
+ Đã đốc thúc được team hoàn thành bài lab trong ngày (trước 23h59 cùng ngày).
+ Đã theo sát và đảm bảo hình thức bài nộp cho cả đội.
+ Đã hiểu được tầm quan trọng của prompt engineering, sau khi phải làm lại cùng 2 thành viên trong team, cũng như là tự check các runs và tổng hợp thành version_log.
- Chưa làm được:
+ Chọn model và provider cho team, việc này là khởi tạo bài cho nhóm nhưng làm lâu khiến cả nhóm phải chờ.
+ Chưa sát sao trong việc điều phối team nên một thành viên đã làm sai hướng đi đề bài.
+ Tự viết một tool cho agent, phần này do một thành viên đảm nhận toàn bộ.
+ Tự viết các eval test để kiểm chứng agent, phần này do một thành viên đảm nhận toàn bộ.
+ Tự deploy agent lên một web để các nhóm khác có thể chạy được, hay chỉ đạo thành viên trong team deploy một web hoàn chỉnh. Hiện tại mới có một deploy kết nối thông qua cloudflare tunnel.
+ Đang cần AI tổng hợp lại dữ liệu bài làm của team thay vì tự kiểm tra thủ công.
- Học được:
+ Việc sửa system_prompt và tools.yaml đã cho các kết quả ngoài mong đợi. system_prompt có thể cover 100% accuracy nếu đủ kĩ.
+ Việc quản lý nhóm 6 người cần có cách thức trao đổi tường minh hơn và các thành viên báo cáo tiến độ để tôi nắm bắt nhanh hơn trước khi quá muộn.
- Lần sau:
+ Tôi sẽ đặt ra rule giao tiếp trong team để mọi người dễ làm việc với nhau.
+ Nên nhận thêm một phần việc để có nhiều cơ hội tự học hơn.

...
