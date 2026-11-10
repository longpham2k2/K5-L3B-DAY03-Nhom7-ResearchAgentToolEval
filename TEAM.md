# Team

## Thông tin nhóm

- Tên nhóm: Nhóm 7
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhom7-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - URL repo: https://github.com/longpham2k2/K5-L3B-DAY03-Nhom7-ResearchAgentToolEval.git
  - Nhánh nộp: `main`
  - Commit chốt (đúng hạn): `a9b73ef3ec584d27bbff07afee87cadbc51d1611` (`a9b73ef`, "update group_report and individual report", 23:59 ngày 10/11/2026)
  - Bổ sung sau deadline (commit mới, không sửa commit cũ, theo `RULES.md`):
    - `4944df4` (00:07 ngày 11/11/2026): điền mục A3 (câu hỏi mẫu) và B6 (Reflection) trong `report/team/group_report.md`, cập nhật checklist `SUBMISSION.md`.
    - Commit cập nhật `TEAM.md` này: ghi commit chốt, vai trò và đóng góp từng thành viên.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Phạm Ngọc Long | 2A202604111 | 26ai.longpn@vinuni.edu.vn | longpham2k2 | Nhóm trưởng, #1 Eval runner — setup, baseline v0, `version_log.csv`, group report, kiểm tra checklist nộp bài |
| 2 | Nguyễn Khắc Bào | 2A202604072 | 26ai.baonk@vinuni.edu.vn | invzble-z | #3 Tool declaration — `tools.yaml` (v3), khai báo 4 tool mới |
| 3 | Trần Đức Duy | 2A202604071 | 26ai.duytd2@vinuni.edu.vn | tran85122-afk | #4 Tool developer — 4 tool mới, unit test, sửa bug tool có sẵn |
| 4 | Lê Bá Nguyên | 2A202604100 | 26ai.nguyenlb2@vinuni.edu.vn | lbNGuyen06 | #5 Eval designer — 10 case group eval, run v4, transcript chat live |
| 5 | Nguyễn Văn Tuấn | 2A202604121 | 26ai.tuannv@vinuni.edu.vn | tuannguyen-cell | UI — Streamlit `app.py`, deploy Cloudflare Tunnel |
| 6 | Đào Hồng Thắng | 2A202604076 | 26ai.thangdh2@vinuni.edu.vn | myblue-ai | #2 Prompt engineer — `system_prompt.md` (v1, v2) |

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/MSSV_HoTen.md` (chi tiết phần việc, bằng chứng, công cụ AI đã dùng và tự đánh giá). Tóm tắt đóng góp và commit kỹ thuật chính:

| Thành viên | Phần việc phụ trách | Đóng góp cụ thể | Commit / bằng chứng chính | Báo cáo cá nhân |
|---|---|---|---|---|
| Phạm Ngọc Long | Nhóm trưởng, chạy eval, tổng hợp | Chia việc 6 vai trò; setup `.env`, xử lý lỗi provider Gemini; chạy baseline v0; ghi `version_log.csv` v0–v4; review trực tiếp v1 với Thắng (làm lại theo từng giả thuyết); soạn `group_report.md`; kiểm tra checklist nộp bài | `eaa1df7`, `6d7b61e`, `b568b62`, `28c25c5`, `a9b73ef`; merge PR #1, #2 | [2A202604111_PhamNgocLong.md](report/team/2A202604111_PhamNgocLong.md) |
| Đào Hồng Thắng | `system_prompt.md` | v1: bỏ 3 chỉ dẫn xấu của starter (0.65 → 0.70); v2: thêm bảng routing (`tool_routing_accuracy` 1.00) | `b6763ae`, `3a0640f` | [2A202604076_DaoHongThang.md](report/team/2A202604076_DaoHongThang.md) |
| Nguyễn Khắc Bào | `tools.yaml` | v3: quy ước args trong mô tả tham số (0.70 → 0.90); khai báo 4 tool mới với "khi nào dùng / KHÔNG dùng"; phát hiện lệch hash do CRLF/LF | `b02cf90`, `117b59a` | [2A202604072_NguyenKhacBao.md](report/team/2A202604072_NguyenKhacBao.md) |
| Trần Đức Duy | Tool mới + unit test | 4 tool mới (`wiki`, `hackernews`, `github`, `huggingface`) với `TOOL.md`; 18 test cho tool mới, điền hết stub test của tool có sẵn (0 skipped); tìm và sửa bug `limit="0"` (`_clamp`) kèm regression test | `3f31924` (PR #1) | [2A202604071_TranDucDuy.md](report/team/2A202604071_TranDucDuy.md) |
| Lê Bá Nguyên | Group eval | 10 case trong `data/eval_group.json` (5 single + 5 multi turn, mỗi tool mới có case route tới); chạy group eval v4 (0.80); transcript chat live v4 | `9db20cf`, `083e09f` | [2A202604100_LeBaNguyen.md](report/team/2A202604100_LeBaNguyen.md) |
| Nguyễn Văn Tuấn | UI | UI Streamlit `starter_v0/app.py` (chat nhiều lượt, hiển thị tool call, lưu transcript, chặn `send` để người dùng xác nhận); test UI; deploy bằng Cloudflare Tunnel cho Team showdown | `964df71` | [2A202604121_NguyenVanTuan.md](report/team/2A202604121_NguyenVanTuan.md) |
