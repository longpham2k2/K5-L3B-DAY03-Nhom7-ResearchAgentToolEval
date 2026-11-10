# Báo cáo cá nhân — Nguyễn Văn Tuấn

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Tuấn
- MSSV: 2A202604121
- Email: 26ai.tuannv@vinuni.edu.vn
- Vai trò: phụ trách giao diện người dùng (UI) và phần minh chứng liên quan đến UI.

## 2. Phần việc phụ trách

- Xây dựng giao diện chat bằng Streamlit để người dùng thử Research Agent.
- Kết nối UI với provider, prompt, tool declarations và vòng đời chat hiện có.
- Hiển thị hoạt động của tool, lưu transcript và bổ sung bước xác nhận trước khi gửi Telegram từ UI.
- Cập nhật hướng dẫn chạy UI và kiểm tra giao diện bằng test, chạy thử ứng dụng.

## 3. Đóng góp cụ thể

- Tạo [app.py](../../starter_v0/app.py): giao diện chat nhiều lượt; chọn provider, model và version; hiển thị danh sách tool, trạng thái cấu hình, tool arguments/kết quả; cho tải transcript JSON.
- Tạo giao diện theo theme sáng, điều chỉnh màu chữ và nền để các khu vực sidebar, chat, thông báo và ô nhập dễ đọc hơn.
- Bổ sung cơ chế chặn tool `send` trong UI để hiển thị nội dung cần gửi và chờ người dùng xác nhận hoặc hủy. Thêm test kiểm tra tool call bị dừng trước khi thực thi.
- Cập nhật [README.md](../../starter_v0/README.md) và [requirements.txt](../../starter_v0/requirements.txt) để hướng dẫn chạy Streamlit và khai báo dependency.

## 4. Bằng chứng và cách tự kiểm tra

- Mã giao diện: [starter_v0/app.py](../../starter_v0/app.py).
- Kiểm tra xác nhận gửi: [starter_v0/tests/test_chat_ui.py](../../starter_v0/tests/test_chat_ui.py).
- Thay đổi vòng gọi tool: [starter_v0/chat.py](../../starter_v0/chat.py).
- Hướng dẫn và dependency: [starter_v0/README.md](../../starter_v0/README.md), [starter_v0/requirements.txt](../../starter_v0/requirements.txt).
- Lệnh chạy từ thư mục `starter_v0/`: `python -m streamlit run app.py`.
- Kiểm thử: chạy `python -m pytest -q` trong `starter_v0/`; kết quả tại thời điểm hoàn thiện báo cáo là **119 passed**.
- Kiểm tra UI: mở ứng dụng trên trình duyệt tại địa chỉ local do Streamlit in ra; health endpoint trả HTTP 200 trong lần smoke test.
- AI/công cụ đã dùng: GitHub Copilot trong VS Code. Tự kiểm tra bằng cách đọc lại thay đổi, chạy test, mở UI trên trình duyệt và xác nhận ứng dụng phản hồi.

## 5. Tự đánh giá

UI đã kết nối được với luồng chat và cấu hình agent sẵn có, đồng thời có transcript để lưu bằng chứng và có bước xác nhận cho thao tác gửi trong giao diện. Qua phần này, tôi hiểu rõ hơn cách kết nối frontend Streamlit với vòng gọi tool và cách kiểm thử một ranh giới hành động có tác động bên ngoài.

Phần còn cần hoàn thiện là lưu URL demo công khai vào báo cáo nhóm sau khi tạo tunnel/deploy và giữ dịch vụ chạy trong buổi demo.
