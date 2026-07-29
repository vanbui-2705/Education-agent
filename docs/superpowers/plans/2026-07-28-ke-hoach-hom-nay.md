# Kế hoạch ngày 2026-07-28 — Database chạy thật đầu tiên

## Kết quả cuối ngày

Hoàn thành phần đầu của Chặng 1 bằng code tự viết:

- Mở được kết nối SQLite qua một chỗ duy nhất.
- Tạo đủ bốn bảng từ `db/schema.sql`.
- Bật và kiểm tra được khóa ngoại.
- Có test chứng minh database chặn trùng phòng và trùng giáo viên.
- Chạy `python -m db.init_db` để sinh `data/trung_tam.db`.

Hôm nay chưa làm Gemini, system prompt, giao diện và công cụ xếp lịch. Đây là nền dữ liệu thật mà agent sẽ sử dụng ở các chặng sau.

## Nguyên tắc học trong ngày

1. Tự viết giả mã trước khi viết Python.
2. Không chép nguyên file từ AI.
3. Khi lỗi, tự đọc traceback và ghi một phỏng đoán trước khi hỏi.
4. AI ưu tiên gợi ý theo thứ tự: câu hỏi dẫn đường → chỉ vị trí sai → giả mã → một dòng mẫu.
5. Sau khi test xanh, tự giải thích lại luồng chạy mà không nhìn tài liệu.

## Khối 1 — Đọc thiết kế và xác định luồng dữ liệu (30 phút)

Đọc:

- `config.py`: `DB_PATH` và `SCHEMA_PATH`.
- `db/schema.sql`: bốn bảng, khóa ngoại và hai ràng buộc `UNIQUE`.
- Task 1 trong kế hoạch Chặng 1.

Tự viết vào giấy hoặc ghi chú luồng sau bằng lời của mình:

`main` → mở kết nối → đọc schema → tạo bảng → commit → đóng kết nối.

Checkpoint: giải thích được vì sao mọi nơi không nên tự gọi `sqlite3.connect`.

## Khối 2 — Viết test database trước (60–75 phút)

Tạo:

- `db/__init__.py`
- `ingest/__init__.py`
- `tools/__init__.py`
- `tests/__init__.py`
- `tests/test_db.py`

Viết bốn test:

1. `test_tao_du_bon_bang`
2. `test_khoa_ngoai_duoc_bat`
3. `test_chan_hai_lop_cung_phong_cung_gio`
4. `test_chan_giao_vien_day_hai_lop_cung_luc`

Chạy:

`pytest tests/test_db.py -v`

Checkpoint: test phải đỏ vì `db.connection` hoặc `db.init_db` chưa tồn tại. Tự giải thích vì sao thất bại này là đúng.

## Khối 3 — Viết lớp kết nối SQLite (45–60 phút)

Tạo `db/connection.py` với giao diện:

`get_conn(db_path: Path | None = None) -> sqlite3.Connection`

Hành vi cần tự cài đặt:

- Nếu không truyền đường dẫn, dùng `config.DB_PATH`.
- Tạo thư mục cha nếu chưa tồn tại.
- Mở kết nối SQLite.
- Đặt `row_factory` để đọc cột bằng tên.
- Bật kiểm tra khóa ngoại cho chính kết nối đó.
- Trả về connection.

Chạy riêng test khóa ngoại.

Checkpoint: `PRAGMA foreign_keys` trả về `1`.

## Khối 4 — Viết lệnh tạo bảng (45–60 phút)

Tạo `db/init_db.py` với hai giao diện:

- `tao_bang(conn: sqlite3.Connection) -> None`
- `main() -> None`

Hành vi:

- `tao_bang` đọc nội dung từ `config.SCHEMA_PATH` bằng UTF-8.
- Chạy toàn bộ schema bằng API phù hợp với nhiều câu SQL.
- Commit giao dịch.
- `main` mở kết nối mặc định, gọi `tao_bang`, đóng kết nối và in đường dẫn file vừa tạo.
- Chỉ gọi `main` khi file được chạy như chương trình.

Chạy:

- `pytest tests/test_db.py -v`
- `python -m db.init_db`
- `Get-Item data\trung_tam.db`

Checkpoint: bốn test xanh và file database thật tồn tại.

## Khối 5 — Củng cố để tránh phụ thuộc mẫu (30–45 phút)

Không nhìn code, trả lời bằng lời:

1. Vì sao SQLite phải bật khóa ngoại trên từng connection?
2. Vì sao tạo bảng dùng API chạy script thay vì API chạy một câu SQL?
3. `row_factory` giải quyết vấn đề gì?
4. Hai ràng buộc `UNIQUE` đang bảo vệ điều gì?
5. Vì sao test dùng database tạm thay vì `data/trung_tam.db`?

Sau đó tự thực hiện một thay đổi nhỏ:

- Thêm một test chứng minh không thể chèn `buoi_hoc` với `ma_gv` không tồn tại.

Checkpoint: test mới đỏ nếu bỏ bật khóa ngoại và xanh khi dùng `get_conn`.

## Việc mở rộng nếu còn thời gian

Chỉ làm sau khi toàn bộ checkpoint trên đạt:

- Tạo bốn file `samples/*.csv` theo Task 2 của kế hoạch Chặng 1.
- Chưa viết `ingest/from_csv.py` hôm nay nếu chưa tự giải thích trọn vẹn phần database.

## Điều kiện kết thúc ngày

Ngày hôm nay được tính là hoàn thành khi:

- `pytest tests/test_db.py -v` xanh toàn bộ.
- `data/trung_tam.db` được tạo bằng lệnh module.
- Bạn tự giải thích được luồng từ `main()` đến file database.
- Bạn tự viết được test khóa ngoại bổ sung mà không chép mẫu.
- Ghi lại ba điều đã hiểu và một điểm còn vướng để bắt đầu buổi sau.

Không lấy số dòng code hoặc việc hoàn thành nhiều task làm tiêu chí. Mục tiêu là tự viết, tự chạy và tự giải thích được phần nền đầu tiên của hệ thống.
