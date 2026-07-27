# Chặng 1 — Nền dữ liệu và công cụ đọc

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dựng database SQLite chứa lịch trung tâm, nạp được dữ liệu mẫu, và viết 6 công cụ đọc lịch có test đầy đủ — tất cả bằng Python thuần, chưa đụng tới Gemini.

**Architecture:** Ba tầng tách rời. `db/` mở kết nối và tạo bảng. `ingest/` đổ CSV vào bảng. `tools/` là các hàm nhận một kết nối database và trả về `list[dict]`. Không tầng nào biết tới LLM, nên toàn bộ chạy và test được offline, không tốn một đồng API.

**Tech Stack:** Python 3.10+, `sqlite3` và `csv` (có sẵn trong Python), pytest.

## Global Constraints

Áp dụng cho **mọi** task dưới đây:

- Python **3.10 trở lên** (cần cú pháp `Path | None`). Kiểm tra bằng `python --version`.
- Mọi lệnh chạy từ thư mục gốc `E:\BE_AI\Ai-Agent`, dùng dạng `python -m goi.module`. Không `cd` vào thư mục con rồi chạy.
- `thu`: số nguyên **2–8**, trong đó **8 = Chủ nhật**. `ca`: số nguyên **1–4**. Không dùng chuỗi.
- Mọi công cụ trả **`list[dict]`**. Không trả `sqlite3.Row`, không trả tuple.
- Mọi công cụ nhận **`conn` làm tham số đầu tiên**. Không hàm nào tự mở kết nối bên trong.
- Không tìm thấy thì trả **danh sách rỗng**, không ném lỗi. Chỉ ném lỗi khi *tham số* sai.
- Comment, docstring, thông báo lỗi, tên biến: **tiếng Việt**.
- **Không** import bất cứ thứ gì liên quan Gemini/LLM trong Chặng 1.
- Khoảng hợp lệ của `thu` và `ca` đọc từ `config.py`, không viết cứng trong code.
- Thông điệp commit: **tiếng Việt không dấu** (tránh lỗi mã hoá trên console Windows).
- Không sửa `db/schema.sql`. Hai ràng buộc `UNIQUE` trong đó là lưới an toàn, cấm gỡ.
- Theo Nguyên tắc 5 của spec: tài liệu mô tả chữ ký và hành vi, code thật nằm trong file `.py`.

## Bản đồ file

| File | Trách nhiệm |
|---|---|
| `db/connection.py` | Mở kết nối SQLite, bật khoá ngoại, đặt kiểu dòng trả về |
| `db/init_db.py` | Đọc `schema.sql`, tạo bảng |
| `ingest/from_csv.py` | Đọc CSV trong `samples/` đổ vào database |
| `tools/text_utils.py` | Bỏ dấu tiếng Việt để so khớp gần đúng |
| `tools/doc_lich.py` | 6 công cụ đọc lịch |
| `tests/conftest.py` | Fixture tạo database tạm nạp sẵn dữ liệu mẫu |
| `tests/test_db.py` | Test tạo bảng và ràng buộc UNIQUE |
| `tests/test_ingest.py` | Test nạp CSV |
| `tests/test_doc_lich.py` | Test 5 công cụ tra cứu |
| `tests/test_tim_kiem.py` | Test bỏ dấu và tìm gần đúng |
| `samples/*.csv` | Dữ liệu mẫu cố định, dùng chung cho test |
| `demo_chang1.py` | Chạy tay để nhìn kết quả bằng mắt |

---

## Task 1: Kết nối và tạo bảng

**Files:**
- Create: `db/__init__.py`, `ingest/__init__.py`, `tools/__init__.py`, `tests/__init__.py` (đều rỗng)
- Create: `db/connection.py`, `db/init_db.py`
- Test: `tests/test_db.py`

**Interfaces:**
- Consumes: `config.DB_PATH`, `config.SCHEMA_PATH` (đã có trong `config.py`)
- Produces:
  - `db.connection.get_conn(db_path: Path | None = None) -> sqlite3.Connection`
  - `db.init_db.tao_bang(conn: sqlite3.Connection) -> None`
  - `db.init_db.main() -> None` — chạy được bằng `python -m db.init_db`

### Lý thuyết trước khi làm

**Môi trường ảo.** Máy bạn có một Python dùng chung. Dự án A cần `pandas` bản 1.5, dự án B cần bản 2.0 — cài chung là đá nhau. Môi trường ảo là một bản Python riêng nằm trong thư mục dự án; kích hoạt rồi thì `pip install` chỉ ảnh hưởng dự án này. Thư mục `.venv/` đã bị chặn trong `.gitignore` vì tạo lại được từ `requirements.txt`.

**SQLite.** Database gọn nằm trọn trong **một file**. Không cần cài server, không mật khẩu. Python có sẵn thư viện `sqlite3`. Đủ mạnh cho quy mô dưới 15 giáo viên.

**`row_factory`.** Mặc định SQLite trả mỗi dòng dạng tuple, muốn lấy tên phải viết `dong[1]` — đọc không hiểu số 1 là gì, thêm cột vào giữa là hỏng hết. Đặt `row_factory = sqlite3.Row` rồi thì viết được `dong["ten"]`.

**Khoá ngoại mặc định TẮT.** Khoá ngoại là ràng buộc kiểu "`buoi_hoc.ma_gv` phải tồn tại trong bảng `giao_vien`". Bất ngờ: SQLite **không kiểm tra** trừ khi bật thủ công cho **từng kết nối** bằng một câu PRAGMA. Quên là ghi được dữ liệu rác mà không báo lỗi. Đây chính là lý do mọi nơi phải lấy kết nối qua `get_conn` chứ không ai tự gọi `sqlite3.connect`.

**Chạy nhiều câu lệnh SQL một lượt.** `schema.sql` chứa nhiều lệnh `CREATE TABLE` ngăn cách bằng dấu chấm phẩy. Hàm `execute` chỉ chạy được một lệnh; phải dùng `executescript`.

**Ràng buộc UNIQUE.** `UNIQUE(ma_phong, thu, ca)` nghĩa là không thể có hai dòng cùng bộ ba đó. Database **tự từ chối**, không cần code kiểm tra. Kể cả code sai, kể cả agent điên, lịch vẫn không trùng phòng. Vi phạm thì Python ném `sqlite3.IntegrityError`.

**`__init__.py`.** File rỗng đánh dấu thư mục là "gói" Python, để `from db.connection import get_conn` chạy được.

**`tmp_path`.** Fixture có sẵn của pytest, tạo thư mục tạm mới cho mỗi test và tự xoá sau. Nhờ nó test không đụng vào `data/trung_tam.db` thật.

### Các bước

- [ ] **Step 1: Tạo môi trường ảo và cài thư viện**

Chạy lần lượt: `python --version`, `python -m venv .venv`, `.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`.

Đầu dòng lệnh phải xuất hiện `(.venv)`. Nếu PowerShell chặn script, chạy một lần: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

- [ ] **Step 2: Tạo 4 file `__init__.py` rỗng**

Tạo thư mục `tests/`, rồi tạo file rỗng trong `db/`, `ingest/`, `tools/`, `tests/`.

- [ ] **Step 3: Viết `tests/test_db.py`**

Bốn test, mỗi test tự tạo database riêng qua `tmp_path`:

| Tên test | Chuẩn bị | Khẳng định |
|---|---|---|
| `test_tao_du_bon_bang` | `get_conn` + `tao_bang` | Truy vấn `sqlite_master` thấy đủ 4 bảng `giao_vien`, `phong`, `lop`, `buoi_hoc` |
| `test_khoa_ngoai_duoc_bat` | chỉ `get_conn` | `PRAGMA foreign_keys` trả về `1` |
| `test_chan_hai_lop_cung_phong_cung_gio` | Tạo bảng; chèn 2 giáo viên, 1 phòng, 2 lớp; chèn 1 buổi `(L1, GV01, P301, thu=3, ca=2)` | Chèn buổi thứ hai `(L2, GV02, P301, thu=3, ca=2)` phải ném `sqlite3.IntegrityError` — dùng `pytest.raises` |
| `test_chan_giao_vien_day_hai_lop_cung_luc` | Tạo bảng; chèn 1 giáo viên, 2 phòng, 2 lớp; chèn 1 buổi `(L1, GV01, P301, thu=3, ca=2)` | Chèn buổi thứ hai `(L2, GV01, P302, thu=3, ca=2)` phải ném `sqlite3.IntegrityError` |

- [ ] **Step 4: Chạy test, xác nhận thất bại**

Chạy: `pytest tests/test_db.py -v`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'db.connection'`

Thấy đúng lỗi này là tốt. Test phải đỏ trước khi có code, để chắc chắn nó thật sự kiểm tra một cái gì đó.

- [ ] **Step 5: Viết `db/connection.py`**

Một hàm `get_conn`. Hành vi:
- Nhận `db_path` tuỳ chọn; bỏ trống thì dùng `config.DB_PATH`.
- Tạo thư mục cha nếu chưa có (không thì `sqlite3` báo lỗi khó hiểu).
- Mở kết nối, đặt `row_factory = sqlite3.Row`, bật `PRAGMA foreign_keys = ON`.
- Trả về kết nối.

Docstring giải thích vì sao mọi nơi phải đi qua hàm này: hai thiết lập bắt buộc chỉ viết một chỗ, không sợ chỗ nào quên.

- [ ] **Step 6: Viết `db/init_db.py`**

Hai hàm:
- `tao_bang(conn)` — đọc `config.SCHEMA_PATH` với `encoding="utf-8"`, chạy bằng `executescript`, rồi `commit`.
- `main()` — mở kết nối mặc định, gọi `tao_bang`, đóng, in đường dẫn database vừa tạo.

Thêm khối `if __name__ == "__main__":` gọi `main()`.

- [ ] **Step 7: Chạy test, xác nhận xanh**

Chạy: `pytest tests/test_db.py -v`
Mong đợi: PASS — 4 test xanh

- [ ] **Step 8: Tạo database thật và nhìn bằng mắt**

Chạy: `python -m db.init_db`
Mong đợi: in ra đường dẫn `data\trung_tam.db`. Kiểm tra file tồn tại bằng `Get-Item data\trung_tam.db`.

- [ ] **Step 9: Commit**

Thêm `db/`, `ingest/__init__.py`, `tools/__init__.py`, `tests/`. Thông điệp: `feat(db): ket noi SQLite va tao bang tu schema.sql` — thân commit ghi rõ `get_conn` bật khoá ngoại, `tao_bang` chạy `schema.sql`, test xác nhận UNIQUE chặn trùng phòng và trùng giáo viên.

---

## Task 2: Dữ liệu mẫu và nạp CSV

**Files:**
- Create: `samples/giao_vien.csv`, `samples/phong.csv`, `samples/lop.csv`, `samples/buoi_hoc.csv`
- Create: `ingest/from_csv.py`
- Test: `tests/test_ingest.py`

**Interfaces:**
- Consumes: `db.connection.get_conn`, `db.init_db.tao_bang`, `config.SAMPLES_DIR`
- Produces:
  - `ingest.from_csv.nap_csv(conn: sqlite3.Connection, samples_dir: Path | None = None) -> dict[str, int]`
    — trả về số dòng đã nạp mỗi bảng, ví dụ `{"giao_vien": 3, "phong": 3, "lop": 4, "buoi_hoc": 5}`
  - `ingest.from_csv.main() -> None` — chạy được bằng `python -m ingest.from_csv`

### Lý thuyết trước khi làm

**Vì sao CSV trước Google Sheets.** Kết nối Sheets cần tài khoản dịch vụ, file khoá, cấp quyền — nhiều bước lằng nhằng mà chưa học được gì về agent. CSV chỉ là file văn bản. Quan trọng hơn: dữ liệu mẫu **cố định** nên test khẳng định được con số chính xác. Chặng 5 đổi nguồn sang Sheets chỉ cần viết thêm một file trả về đúng dạng — mọi thứ phía sau không đổi. Đó là lợi ích của việc tách tầng.

**Thứ tự xoá vì khoá ngoại.** Nạp lại thì phải xoá dữ liệu cũ trước. Nhưng không xoá `giao_vien` trước được — `buoi_hoc` đang tham chiếu tới nó, database sẽ từ chối. Phải xoá **ngược từ bảng con lên bảng cha**: `buoi_hoc`, rồi `lop`, `phong`, `giao_vien`. Lúc chèn thì ngược lại: cha trước, con sau.

**Tham số thay thế.** Nối chuỗi để dựng câu `INSERT` là sai — tên có dấu nháy đơn sẽ làm hỏng câu lệnh, và tệ hơn là mở đường cho SQL injection. Cách đúng: viết dấu `?` ở chỗ giá trị rồi truyền dữ liệu thành tham số riêng, thư viện tự xử lý.

Lưu ý: dấu `?` chỉ thay được **giá trị**, không thay được **tên bảng hay tên cột**. Tên bảng vẫn phải nối chuỗi — an toàn ở đây vì tên lấy từ hằng số trong code, không phải từ người dùng nhập.

**Chèn hàng loạt.** Chèn 100 dòng bằng 100 lần `execute` thì chậm. `executemany` gửi một lượt.

**Mã hoá `utf-8-sig`.** Excel khi lưu CSV hay chèn 3 byte vô hình ở đầu file (BOM). Đọc bằng `utf-8` thường thì tên cột đầu tiên biến thành `\ufeffma_gv` và tra không thấy. `utf-8-sig` tự bỏ 3 byte đó.

**CSV không có kiểu.** Mọi ô đọc lên đều là chuỗi; cột `thu` ra `"3"` chứ không phải `3`. Phải ép sang `int` ngay lúc nạp, để về sau lọc `thu = 3` chắc chắn đúng.

**Đọc hết trước khi ghi.** Đọc cả 4 file vào bộ nhớ trước, rồi mới động vào database. Nếu một file lỗi hoặc thiếu, database vẫn nguyên vẹn thay vì bị xoá nửa chừng.

### Các bước

- [ ] **Step 1: Tạo 4 file CSV mẫu**

Lưu bằng **UTF-8**. Dòng đầu mỗi file là dòng tiêu đề, tên cột đúng như bảng dưới, theo đúng thứ tự.

`samples/giao_vien.csv` — cột `ma_gv, ten`:

| ma_gv | ten |
|---|---|
| GV01 | Nguyễn Thị Lan |
| GV02 | Trần Văn Minh |
| GV03 | Lê Thị Hoa |

`samples/phong.csv` — cột `ma_phong, suc_chua`:

| ma_phong | suc_chua |
|---|---|
| P301 | 15 |
| P302 | 20 |
| P303 | 30 |

`samples/lop.csv` — cột `ma_lop, ten_lop, mon, si_so`:

| ma_lop | ten_lop | mon | si_so |
|---|---|---|---|
| T9A | Toán 9 nâng cao | Toán | 18 |
| T9B | Toán 9 cơ bản | Toán | 12 |
| L10A | Lý 10 | Lý | 14 |
| V8A | Văn 8 | Văn | 20 |

`samples/buoi_hoc.csv` — cột `ma_lop, ma_gv, ma_phong, thu, ca`:

| ma_lop | ma_gv | ma_phong | thu | ca |
|---|---|---|---|---|
| T9A | GV01 | P302 | 2 | 4 |
| T9A | GV01 | P302 | 5 | 4 |
| T9B | GV01 | P301 | 3 | 2 |
| L10A | GV02 | P303 | 2 | 4 |
| V8A | GV03 | P302 | 3 | 2 |

Bộ dữ liệu này cố ý nhỏ và được tính sẵn để test khẳng định con số chính xác. **Không sửa** khi chưa sửa test tương ứng.

- [ ] **Step 2: Viết `tests/test_ingest.py`**

Bốn test, dùng `tmp_path` + `tao_bang` + `nap_csv(conn, config.SAMPLES_DIR)`:

| Tên test | Khẳng định |
|---|---|
| `test_nap_dung_so_dong` | `nap_csv` trả về đúng `{"giao_vien": 3, "phong": 3, "lop": 4, "buoi_hoc": 5}` |
| `test_du_lieu_vao_dung_bang` | Tra `ten` của `GV01` trong bảng `giao_vien` ra `"Nguyễn Thị Lan"` |
| `test_cot_so_luu_dang_so_khong_phai_chuoi` | Lấy một dòng `buoi_hoc`, `thu` và `ca` đều là `int` — không phải chuỗi |
| `test_nap_lai_khong_nhan_doi_du_lieu` | Gọi `nap_csv` hai lần liên tiếp, `COUNT(*)` của `buoi_hoc` vẫn là 5 |

- [ ] **Step 3: Chạy test, xác nhận thất bại**

Chạy: `pytest tests/test_ingest.py -v`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'ingest.from_csv'`

- [ ] **Step 4: Viết `ingest/from_csv.py`**

Hai hằng số ở đầu module:
- Một từ điển ánh xạ **tên bảng → danh sách cột**, xếp theo thứ tự chèn (cha trước con): `giao_vien`, `phong`, `lop`, `buoi_hoc`. Cột của từng bảng đúng như bảng CSV ở Step 1. Comment ghi rõ: thứ tự này là thứ tự chèn, lúc xoá phải đi ngược lại.
- Một tập hợp tên các cột số cần ép `int`: `suc_chua`, `si_so`, `thu`, `ca`.

Một hàm riêng đọc một file CSV thành `list[dict]`: mở với `encoding="utf-8-sig"` và `newline=""`, dùng `csv.DictReader`. File không tồn tại thì ném `FileNotFoundError` kèm đường dẫn.

Hàm `nap_csv(conn, samples_dir=None)`:
1. Xác định thư mục — bỏ trống thì dùng `config.SAMPLES_DIR`.
2. Đọc **cả 4 file** vào bộ nhớ trước khi động vào database.
3. Xoá dữ liệu cũ theo thứ tự **ngược** của từ điển bảng.
4. Với mỗi bảng theo thứ tự **xuôi**: dựng câu `INSERT` với dấu `?`, ép kiểu các cột số, cắt khoảng trắng hai đầu các cột chuỗi, chèn bằng `executemany`.
5. `commit`, trả về từ điển số dòng mỗi bảng.

Hàm `main()`: mở kết nối mặc định, gọi `tao_bang` rồi `nap_csv`, in số dòng từng bảng, đóng kết nối.

- [ ] **Step 5: Chạy test, xác nhận xanh**

Chạy: `pytest tests/test_ingest.py -v`
Mong đợi: PASS — 4 test xanh

- [ ] **Step 6: Nạp vào database thật**

Chạy: `python -m ingest.from_csv`
Mong đợi: in `giao_vien: 3`, `phong: 3`, `lop: 4`, `buoi_hoc: 5`.

- [ ] **Step 7: Commit**

Thêm `samples/`, `ingest/from_csv.py`, `tests/test_ingest.py`. Thông điệp: `feat(ingest): nap du lieu mau tu CSV vao SQLite` — thân ghi rõ xoá ngược theo khoá ngoại, ép kiểu số cho `thu`/`ca`/`si_so`/`suc_chua`.

---

## Task 3: Fixture test và 3 công cụ tra lịch

**Files:**
- Create: `tests/conftest.py`, `tools/doc_lich.py`
- Test: `tests/test_doc_lich.py`

**Interfaces:**
- Consumes: `db.connection.get_conn`, `db.init_db.tao_bang`, `ingest.from_csv.nap_csv`
- Produces:
  - Fixture pytest tên `conn` — database tạm đã tạo bảng và nạp sẵn `samples/`
  - `tools.doc_lich.tra_lich_giao_vien(conn, ma_hoac_ten: str) -> list[dict]`
  - `tools.doc_lich.tra_lich_lop(conn, ma_hoac_ten: str) -> list[dict]`
  - `tools.doc_lich.tra_lich_phong(conn, ma_phong: str) -> list[dict]`
  - Mỗi dict trong kết quả có đúng 10 khoá: `id`, `thu`, `ca`, `ma_lop`, `ten_lop`, `mon`, `ma_gv`, `ten_gv`, `ma_phong`, `suc_chua`
  - Kết quả luôn sắp theo `thu` rồi `ca`

### Lý thuyết trước khi làm

**Fixture của pytest.** Ba file test sắp tới đều cần "một database tạm đã nạp dữ liệu mẫu". Chép đoạn đó vào từng test là lặp. Fixture là hàm tạo sẵn thứ đó; test chỉ cần khai tên nó trong tham số là nhận được. Đặt trong `conftest.py` thì mọi file test trong thư mục tự thấy, không phải import.

**`yield` trong fixture.** Code trước `yield` chạy trước test (chuẩn bị), code sau `yield` chạy sau test (dọn dẹp — ở đây là đóng kết nối).

**JOIN.** Bảng `buoi_hoc` chỉ lưu mã: `GV01`, `P302`. Người dùng muốn thấy `Nguyễn Thị Lan`, `phòng 302 sức chứa 20`. `JOIN` ghép bảng theo mã để lấy đủ thông tin trong một câu lệnh.

Vì sao không lưu thẳng tên vào `buoi_hoc` cho gọn? Vì khi cô Lan đổi tên, ta chỉ sửa một dòng ở bảng `giao_vien` thay vì đi sửa hàng trăm dòng `buoi_hoc`. Nguyên tắc: **mỗi sự thật lưu đúng một chỗ**.

**Bí danh cột.** Bảng `lop` có cột `ten_lop`, bảng `giao_vien` có cột `ten`. Ghép lại mà trùng tên thì đụng nhau — dùng `AS` đổi tên cột trong kết quả (`g.ten AS ten_gv`) để phân biệt.

**Sắp xếp rõ ràng.** Không có `ORDER BY` thì database trả dòng theo thứ tự tuỳ ý — hôm nay thế này, mai thế khác. Test sẽ lúc xanh lúc đỏ mà không hiểu vì sao.

**Vì sao truyền `conn` vào hàm thay vì để hàm tự mở.** Truyền vào thì test đưa được database tạm, chương trình thật đưa database thật — cùng một hàm, không sửa dòng nào. Nếu hàm tự mở kết nối bên trong thì test buộc phải đụng vào database thật hoặc dùng thủ thuật vá tạm. Đây gọi là **tiêm phụ thuộc** (dependency injection), và nó là lý do bộ test chạy xong trong một giây.

**Vì sao chuyển sang `dict`.** `sqlite3.Row` tiện nhưng không phải dict thật, không chuyển thành JSON được. Chặng 2 phải gửi kết quả cho Gemini dưới dạng JSON, nên chuyển ngay từ bây giờ.

**Một truy vấn nền dùng chung.** Ba hàm tra cứu chỉ khác nhau ở điều kiện lọc. Viết một chuỗi truy vấn nền (phần `SELECT` + `JOIN` + `ORDER BY`) rồi cắm điều kiện vào — tránh lặp và tránh ba chỗ trả về ba tập cột khác nhau.

### Các bước

- [ ] **Step 1: Viết `tests/conftest.py`**

Một fixture tên `conn`, nhận `tmp_path`. Chuẩn bị: mở kết nối tới `tmp_path/test.db`, gọi `tao_bang`, gọi `nap_csv` với `config.SAMPLES_DIR`. `yield` kết nối. Dọn dẹp: đóng kết nối.

Docstring ghi rõ: mỗi test nhận một database mới tinh nên các test không ảnh hưởng nhau.

- [ ] **Step 2: Viết `tests/test_doc_lich.py`**

Chín test. Con số khớp dữ liệu mẫu ở Task 2 — sửa `samples/` thì phải sửa cả file này (ghi câu này vào docstring đầu file).

| Tên test | Gọi | Khẳng định |
|---|---|---|
| `test_tra_lich_theo_ma_giao_vien` | `tra_lich_giao_vien(conn, "GV01")` | 3 phần tử |
| `test_tra_lich_theo_ten_giao_vien` | `tra_lich_giao_vien(conn, "Lan")` | 3 phần tử, mọi phần tử có `ma_gv == "GV01"` |
| `test_ket_qua_co_du_thong_tin_nguoi_doc_can` | `tra_lich_giao_vien(conn, "GV01")` | Phần tử đầu có đủ 10 khoá liệt kê ở mục Interfaces; `ten_gv == "Nguyễn Thị Lan"` |
| `test_ket_qua_sap_xep_theo_thu_roi_ca` | `tra_lich_giao_vien(conn, "GV01")` | Dãy cặp `(thu, ca)` bằng chính nó khi đem sắp xếp |
| `test_giao_vien_khong_ton_tai_tra_ve_rong` | `tra_lich_giao_vien(conn, "GV99")` | Danh sách rỗng, **không** ném lỗi |
| `test_tra_lich_lop` | `tra_lich_lop(conn, "T9A")` | 2 phần tử; tập `thu` là `{2, 5}` |
| `test_tra_lich_lop_theo_ten` | `tra_lich_lop(conn, "nâng cao")` | 2 phần tử, mọi phần tử có `ma_lop == "T9A"` |
| `test_tra_lich_phong` | `tra_lich_phong(conn, "P302")` | 3 phần tử |
| `test_tra_lich_phong_trong_hoan_toan` | `tra_lich_phong(conn, "P999")` | Danh sách rỗng |

- [ ] **Step 3: Chạy test, xác nhận thất bại**

Chạy: `pytest tests/test_doc_lich.py -v`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'tools.doc_lich'`

- [ ] **Step 4: Viết `tools/doc_lich.py`**

Docstring đầu module ghi rõ ba quy tắc: nhận `conn` đầu tiên, trả `list[dict]`, không tìm thấy thì trả rỗng. Và một câu: **chỉ đọc, không hàm nào ở đây được phép sửa dữ liệu.**

Một hằng số chuỗi truy vấn nền: `SELECT` lấy `b.id, b.thu, b.ca`, ba cột từ `lop`, `ma_gv` và `g.ten AS ten_gv` từ `giao_vien`, `ma_phong` và `suc_chua` từ `phong`; `JOIN` cả ba bảng theo mã; chỗ điều kiện để trống dạng khuôn (`{dieu_kien}`); kết thúc bằng `ORDER BY b.thu, b.ca`.

Một hàm nội bộ nhận `conn`, chuỗi điều kiện, tuple tham số — cắm điều kiện vào khuôn, chạy, chuyển mỗi dòng sang `dict`, trả về danh sách.

Ba hàm công khai, mỗi hàm chỉ khác điều kiện lọc:
- `tra_lich_giao_vien` — khớp `ma_gv` chính xác **hoặc** `ten` chứa từ khoá (`LIKE` với dấu `%` hai bên). Bọc cả điều kiện trong ngoặc đơn.
- `tra_lich_lop` — tương tự với `ma_lop` và `ten_lop`.
- `tra_lich_phong` — chỉ khớp `ma_phong` chính xác.

Mỗi hàm có docstring ghi tham số, giá trị trả về, và ví dụ đầu vào.

- [ ] **Step 5: Chạy test, xác nhận xanh**

Chạy: `pytest tests/test_doc_lich.py -v` → 9 test xanh
Rồi chạy: `pytest -v` → 17 test xanh (4 + 4 + 9)

- [ ] **Step 6: Commit**

Thêm `tests/conftest.py`, `tools/doc_lich.py`, `tests/test_doc_lich.py`. Thông điệp: `feat(tools): tra lich theo giao vien, lop, phong`.

---

## Task 4: Tìm phòng trống và giáo viên rảnh

**Files:**
- Modify: `tools/doc_lich.py` (thêm hàm vào cuối, thêm `import config` ở đầu)
- Modify: `tests/test_doc_lich.py` (thêm test vào cuối)

**Interfaces:**
- Consumes: `config.THU_HOP_LE`, `config.CA_HOP_LE`
- Produces:
  - `tools.doc_lich.phong_trong(conn, thu: int, ca: int) -> list[dict]` — dict có khoá `ma_phong`, `suc_chua`; sắp theo `ma_phong`
  - `tools.doc_lich.giao_vien_ranh(conn, thu: int, ca: int) -> list[dict]` — dict có khoá `ma_gv`, `ten`; sắp theo `ma_gv`
  - Cả hai ném `ValueError` nếu `thu` hoặc `ca` ngoài khoảng hợp lệ. Thông báo lỗi phải chứa từ `Thu` (cho lỗi thứ) hoặc `Ca` (cho lỗi ca) để test bắt được bằng `match`.

### Lý thuyết trước khi làm

**Đây là hai câu hỏi hay gặp nhất.** "Thứ 3 ca 2 phòng nào trống?" và "Giờ đó ai rảnh?" — quản lý hỏi mỗi ngày. Chúng cũng là nền của Chặng 4: xếp lịch chính là lặp lại hai câu hỏi này rất nhiều lần.

**Tìm cái *không* có mặt.** Truy vấn thường tìm thứ khớp điều kiện. Ở đây ngược lại: lấy **tất cả** phòng, trừ đi những phòng đã bị đặt vào đúng thứ và ca đó — phần còn lại là phòng trống. Cách viết: `WHERE ma_phong NOT IN (truy vấn con lấy phòng bận)`. Truy vấn con chạy trước, truy vấn ngoài loại chúng khỏi danh sách đầy đủ.

**Cạm bẫy `NOT IN` với NULL.** Nếu truy vấn con trả về dù chỉ một giá trị `NULL`, `NOT IN` trả rỗng cho **mọi** dòng — sai âm thầm, không báo lỗi. Ở đây an toàn vì `buoi_hoc.ma_phong` khai báo `NOT NULL`. Ghi nhớ cạm bẫy này, nó cắn rất nhiều người.

**Kiểm tra đầu vào.** Gọi `phong_trong(conn, 9, 2)` — không có thứ 9 — thì truy vấn con rỗng, hàm lặng lẽ trả về "tất cả phòng đều trống". Sai mà không ai biết. Phải chặn ngay từ cửa và ném `ValueError` kèm thông báo rõ.

Điều này còn quan trọng hơn ở Chặng 2: Gemini đôi khi đoán sai tham số. Thông báo lỗi rõ ràng cho phép nó **đọc lỗi và tự sửa**. Thông báo lỗi tốt không chỉ dành cho người — nó là kênh phản hồi cho agent.

**Vì sao đọc khoảng hợp lệ từ `config`.** Giờ giấc và số ca chưa chốt với trung tâm. Khi chốt, sửa `config.py` là xong, không phải lục từng file. Số ma thuật rải khắp code là nguồn lỗi kinh điển.

### Các bước

- [ ] **Step 1: Thêm test vào cuối `tests/test_doc_lich.py`**

Tám test:

| Tên test | Gọi | Khẳng định |
|---|---|---|
| `test_phong_trong_khi_co_phong_ban` | `phong_trong(conn, 3, 2)` | Đúng một phần tử, `ma_phong == "P303"` (thứ 3 ca 2 đang bận P301 và P302) |
| `test_phong_trong_tra_ve_ca_suc_chua` | `phong_trong(conn, 3, 2)` | Phần tử đầu có `suc_chua == 30` |
| `test_phong_trong_khi_khong_ai_hoc` | `phong_trong(conn, 4, 1)` | Cả 3 phòng, thứ tự `P301`, `P302`, `P303` |
| `test_phong_trong_bao_loi_khi_thu_sai` | `phong_trong(conn, 9, 1)` | Ném `ValueError`, thông báo chứa `Thu` |
| `test_phong_trong_bao_loi_khi_ca_sai` | `phong_trong(conn, 3, 7)` | Ném `ValueError`, thông báo chứa `Ca` |
| `test_giao_vien_ranh` | `giao_vien_ranh(conn, 3, 2)` | Đúng một phần tử, `ma_gv == "GV02"`, `ten == "Trần Văn Minh"` |
| `test_giao_vien_ranh_khi_khong_ai_day` | `giao_vien_ranh(conn, 4, 1)` | 3 phần tử |
| `test_giao_vien_ranh_bao_loi_khi_ca_sai` | `giao_vien_ranh(conn, 3, 99)` | Ném `ValueError`, thông báo chứa `Ca` |

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `pytest tests/test_doc_lich.py -v`
Mong đợi: FAIL — `ImportError: cannot import name 'phong_trong'`

- [ ] **Step 3: Thêm hàm vào `tools/doc_lich.py`**

Thêm `import config` ở đầu file.

Một hàm nội bộ kiểm tra tham số: `thu` không nằm trong `config.THU_HOP_LE` thì ném `ValueError` với thông báo nêu khoảng hợp lệ, ghi chú `8 = Chu nhat`, và giá trị nhận được; tương tự cho `ca` với `config.CA_HOP_LE`. Docstring giải thích: không có bước này thì tham số vô nghĩa trả kết quả sai âm thầm, và ở Chặng 2 chính thông báo này là thứ Gemini đọc để tự sửa.

Hai hàm công khai, cùng khuôn:
- Gọi hàm kiểm tra trước tiên.
- `phong_trong` — chọn `ma_phong, suc_chua` từ `phong`, loại những mã xuất hiện trong `buoi_hoc` với đúng `thu` và `ca`, sắp theo `ma_phong`.
- `giao_vien_ranh` — tương tự với bảng `giao_vien`, cột `ma_gv, ten`, sắp theo `ma_gv`.
- Chuyển kết quả sang `list[dict]`.

Docstring mỗi hàm ghi rõ tham số, giá trị trả về, và mục "Ném: ValueError khi...".

- [ ] **Step 4: Chạy test, xác nhận xanh**

Chạy: `pytest tests/test_doc_lich.py -v`
Mong đợi: PASS — 17 test xanh

- [ ] **Step 5: Commit**

Thông điệp: `feat(tools): tim phong trong va giao vien ranh theo thu, ca` — thân ghi rõ dùng `NOT IN` lấy phần bù, kiểm tra tham số ném `ValueError`, khoảng hợp lệ đọc từ `config`.

---

## Task 5: Tìm giáo viên gõ thiếu dấu

**Files:**
- Create: `tools/text_utils.py`
- Modify: `tools/doc_lich.py` (thêm import và một hàm vào cuối)
- Test: `tests/test_tim_kiem.py`

**Interfaces:**
- Produces:
  - `tools.text_utils.bo_dau(chuoi: str) -> str` — bỏ dấu, chuyển chữ thường, cắt khoảng trắng hai đầu
  - `tools.doc_lich.tim_giao_vien(conn, tu_khoa: str) -> list[dict]` — dict có khoá `ma_gv`, `ten`; sắp theo `ma_gv`; từ khoá rỗng trả về danh sách rỗng

### Lý thuyết trước khi làm

**Vấn đề.** Quản lý gõ "co lan" hoặc "nguyen thi lan" thay vì "Nguyễn Thị Lan". Phép `LIKE` của SQLite **không** khớp, vì "Lan" khác "Lán" khác "Làn" ở mức byte.

**Unicode và dấu tổ hợp.** Chữ "ầ" biểu diễn được theo hai cách: một ký tự duy nhất (dạng NFC), hoặc "a" cộng dấu mũ cộng dấu huyền ghép lại (dạng NFD). Chuẩn hoá về NFD rồi vứt bỏ mọi ký tự thuộc loại `Mn` (Mark, nonspacing — tức là các dấu) thì "ầ" thành "a". Thư viện `unicodedata` có sẵn trong Python làm cả hai việc này.

Riêng chữ **đ** không phải "d cộng dấu" — nó là một chữ cái riêng. Phải thay tay trước khi chuẩn hoá, cả chữ thường lẫn chữ hoa.

**Vì sao lọc trong Python thay vì SQL.** SQLite không có sẵn hàm bỏ dấu. Đăng ký hàm Python vào SQLite thì được nhưng phức tạp. Trung tâm dưới 15 giáo viên — lấy hết ra rồi lọc bằng Python chạy dưới một phần nghìn giây.

Đây là một quyết định kỹ thuật đáng ghi nhớ: **quy mô quyết định giải pháp.** Với 15 dòng, giải pháp đơn giản là giải pháp đúng. Với 15 triệu dòng đã phải làm khác. Chọn theo quy mô thật, không theo quy mô tưởng tượng.

**Vì sao tách file riêng.** `bo_dau` không liên quan gì tới lịch học — nó là tiện ích xử lý chữ. Chặng 4 và 5 sẽ dùng lại để so khớp tên lớp, tên môn. Để riêng thì test riêng được và tái sử dụng được.

### Các bước

- [ ] **Step 1: Viết `tests/test_tim_kiem.py`**

Mười test:

| Tên test | Gọi | Khẳng định |
|---|---|---|
| `test_bo_dau_co_ban` | `bo_dau("Nguyễn Thị Lan")` | `"nguyen thi lan"` |
| `test_bo_dau_chu_d_gach_ngang` | `bo_dau("Đặng Đình Đô")` | `"dang dinh do"` |
| `test_bo_dau_chuoi_khong_dau_giu_nguyen` | `bo_dau("Tran Van Minh")` | `"tran van minh"` |
| `test_bo_dau_cat_khoang_trang_thua` | `bo_dau("  Lê Thị Hoa  ")` | `"le thi hoa"` |
| `test_tim_giao_vien_go_thieu_dau` | `tim_giao_vien(conn, "nguyen thi lan")` | 1 phần tử, `ma_gv == "GV01"` |
| `test_tim_giao_vien_chi_go_ten` | `tim_giao_vien(conn, "lan")` | Đúng `["GV01"]` |
| `test_tim_giao_vien_theo_ma` | `tim_giao_vien(conn, "gv02")` | Đúng `["GV02"]` — chữ thường vẫn khớp mã viết hoa |
| `test_tim_giao_vien_co_dau_van_ra` | `tim_giao_vien(conn, "Trần Văn Minh")` | Đúng `["GV02"]` |
| `test_tim_giao_vien_khong_thay_tra_ve_rong` | `tim_giao_vien(conn, "khong co ai ten nay")` | Danh sách rỗng |
| `test_tim_giao_vien_nhieu_ket_qua` | `tim_giao_vien(conn, "thi")` | Tập `ma_gv` là `{"GV01", "GV03"}` |

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Chạy: `pytest tests/test_tim_kiem.py -v`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'tools.text_utils'`

- [ ] **Step 3: Viết `tools/text_utils.py`**

Một hàm `bo_dau`. Thứ tự xử lý:
1. Thay `đ` thành `d` và `Đ` thành `D` (chữ cái riêng, không phải d cộng dấu).
2. Chuẩn hoá chuỗi về dạng NFD bằng `unicodedata.normalize`.
3. Giữ lại các ký tự có `unicodedata.category` khác `"Mn"`.
4. Chuyển chữ thường, cắt khoảng trắng hai đầu.

Docstring nêu hai ví dụ đầu vào–đầu ra và ghi rõ mục đích: so khớp khi người dùng gõ thiếu dấu. Docstring module ghi rõ vì sao tách riêng khỏi `doc_lich.py`.

- [ ] **Step 4: Thêm `tim_giao_vien` vào cuối `tools/doc_lich.py`**

Thêm import `bo_dau` từ `tools.text_utils`.

Hàm `tim_giao_vien(conn, tu_khoa)`:
1. Bỏ dấu từ khoá. Nếu kết quả rỗng, trả danh sách rỗng ngay.
2. Lấy toàn bộ `ma_gv, ten` từ bảng `giao_vien`, sắp theo `ma_gv`.
3. Giữ lại những dòng mà từ khoá đã bỏ dấu nằm trong tên đã bỏ dấu **hoặc** trong mã đã bỏ dấu.
4. Trả `list[dict]`.

Docstring có mục "Ghi chú kỹ thuật" giải thích vì sao lọc trong Python thay vì SQL, và ghi rõ điều đó chấp nhận được ở quy mô dưới 15 giáo viên.

- [ ] **Step 5: Chạy test, xác nhận xanh**

Chạy: `pytest tests/test_tim_kiem.py -v` → 10 test xanh
Rồi chạy: `pytest -v` → 35 test xanh (4 + 4 + 17 + 10)

- [ ] **Step 6: Commit**

Thông điệp: `feat(tools): tim giao vien khi go thieu dau` — thân ghi rõ chuẩn hoá NFD rồi loại ký tự dấu, xử lý riêng chữ `đ`, lọc trong Python vì SQLite không có hàm bỏ dấu.

---

## Task 6: Chạy thử bằng mắt và đóng Chặng 1

**Files:**
- Create: `demo_chang1.py`, `README.md`

**Interfaces:**
- Consumes: toàn bộ 6 công cụ từ Task 3–5, `config.TEN_THU`, `config.GIO_CA`
- Produces: không có gì cho task sau — đây là bước đóng chặng

### Lý thuyết trước khi làm

**Vì sao cần bản chạy thử ngoài test.** Test khẳng định code đúng, nhưng đọc một dòng `assert` không cho bạn cảm giác về sản phẩm. Chạy bản demo và nhìn lịch cô Lan in ra màn hình thì có. Đây cũng là lần đầu `config.TEN_THU` và `config.GIO_CA` được dùng để biến số `2` thành chữ `"Thứ 2 (19:00-20:30)"` — đúng nguyên tắc **lưu số, hiển thị chữ**.

**Vì sao cần README.** Ba tuần nữa quay lại, bạn sẽ không nhớ lệnh nào tạo database. Người xem dự án lúc phỏng vấn cũng mở README đầu tiên. README dở khiến dự án tốt trông như bài tập.

**Ranh giới chặng.** Chặng 1 xong nghĩa là **tầng dữ liệu đáng tin**. Chặng 2 cắm Gemini lên trên. Nếu tầng này còn lung lay, mọi lỗi ở Chặng 2 sẽ khó truy: lỗi do model hiểu sai, hay do công cụ trả sai? Vì thế tiêu chí đóng chặng phải đạt đủ, không nợ lại.

### Các bước

- [ ] **Step 1: Viết `demo_chang1.py`**

Chạy được bằng `python demo_chang1.py` (file ở thư mục gốc, không phải module). Mở kết nối mặc định, gọi `tao_bang` và `nap_csv`, rồi in 8 khối có tiêu đề:

| Khối | Nội dung |
|---|---|
| 1 | Lịch dạy của `GV01` |
| 2 | Lịch dạy tra theo tên `"Lan"` |
| 3 | Lịch của lớp `T9A` |
| 4 | Lịch phòng `P302` |
| 5 | Phòng trống thứ 3 ca 2 (kèm sức chứa) |
| 6 | Giáo viên rảnh thứ 3 ca 2 |
| 7 | Tìm giáo viên với từ khoá `"nguyen thi lan"` |
| 8 | Gọi `phong_trong(conn, 9, 1)` trong khối `try`, bắt `ValueError` và in thông báo |

Một hàm phụ đổi cặp `(thu, ca)` sang chữ cho người đọc, lấy từ `config.TEN_THU` và `config.GIO_CA` — ví dụ `(3, 2)` thành `"Thứ 3 09:45-11:15"`. Một hàm phụ in danh sách buổi thành cột thẳng hàng, danh sách rỗng thì in ghi chú thay vì để trống.

Docstring đầu file ghi rõ: khác pytest, file này không khẳng định gì cả, chỉ in ra để người xem tự nhìn.

- [ ] **Step 2: Chạy thử**

Chạy: `python demo_chang1.py`

Kiểm bằng mắt:
- Khối 1 và 2 ra kết quả giống hệt nhau (tra bằng mã và bằng tên cho cùng đáp án)
- Khối 5 chỉ có `P303`
- Khối 6 chỉ có `GV02  Trần Văn Minh`
- Khối 8 in ra thông báo `ValueError` nêu rõ khoảng hợp lệ và giá trị `9` nhận được

Nếu tiếng Việt hiện thành ô vuông trên PowerShell, chạy `chcp 65001` một lần rồi thử lại.

- [ ] **Step 3: Viết `README.md`**

Các mục cần có:
- **Giới thiệu** — một đoạn: agent trả lời câu hỏi về lịch, từ Chặng 4 tự xếp lịch. Nêu nguyên tắc "LLM quyết định làm gì, Python quyết định kết quả".
- **Tiến độ** — danh sách 5 chặng dạng hộp kiểm, Chặng 1 đã tích.
- **Cài đặt** — tạo môi trường ảo, kích hoạt, `pip install -r requirements.txt`, chép `.env.example` thành `.env` (ghi rõ Chặng 2 mới cần key).
- **Chạy** — bốn lệnh: `python -m db.init_db`, `python -m ingest.from_csv`, `python demo_chang1.py`, `pytest -v`. Kèm ví dụ chạy một test lẻ bằng cú pháp `pytest <file>::<ten_test> -v`.
- **Cấu trúc** — bảng liệt kê từng thư mục và trách nhiệm.
- **Quy ước dữ liệu** — `thu` 2–8 với 8 là Chủ nhật, `ca` 1–4, `buoi_hoc` là bảng lõi, hai ràng buộc `UNIQUE` không được gỡ.
- **Tài liệu** — đường dẫn tới spec và tới chính kế hoạch này.

- [ ] **Step 4: Kiểm tra tiêu chí đóng chặng**

Chạy đủ 4 lệnh, tất cả phải đạt:
- `pytest -v` → 35 test xanh, 0 đỏ, dưới 5 giây
- `python -m db.init_db` → in đường dẫn database
- `python -m ingest.from_csv` → in 3 / 3 / 4 / 5 dòng
- `python demo_chang1.py` → 8 khối, giá trị khớp mục Step 2

Còn dù một test đỏ thì **chưa được sang Chặng 2**.

- [ ] **Step 5: Commit và gắn thẻ**

Thêm `demo_chang1.py`, `README.md`. Thông điệp: `docs: README va ban chay thu, dong Chang 1`. Sau đó gắn thẻ: `git tag chang-1`.

---

## Tiêu chí hoàn thành Chặng 1

| Hạng mục | Đạt khi |
|---|---|
| Database | `data/trung_tam.db` có đủ 4 bảng, khoá ngoại bật |
| Ràng buộc | Test khẳng định `UNIQUE` chặn cả trùng phòng lẫn trùng giáo viên |
| Nạp dữ liệu | Nạp đúng 3/3/4/5 dòng, chạy lại không nhân đôi |
| Công cụ | Đủ 6 hàm, mọi hàm trả `list[dict]`, không tìm thấy thì trả rỗng |
| Kiểm tra đầu vào | `thu`/`ca` sai ném `ValueError` có thông báo rõ ràng |
| Tiếng Việt | Gõ thiếu dấu vẫn tìm ra giáo viên |
| Test | `pytest -v` xanh 35/35, dưới 5 giây, **không gọi API nào** |
| Tài liệu | README chạy theo được mà không cần hỏi ai |
| Git | 6 commit, thẻ `chang-1` |

## Sang Chặng 2 mang theo gì

- **6 hàm trong `tools/doc_lich.py`** thành công cụ Gemini gọi được. Chỉ cần bọc thêm phần mô tả tham số, không sửa logic bên trong.
- **Việc mọi hàm trả `list[dict]`** — chuyển thẳng sang JSON để gửi cho model.
- **Thông báo `ValueError` rõ ràng** — khi Gemini đoán sai tham số, nó đọc chính thông báo này để tự sửa. Đó là vòng phản hồi đầu tiên của agent.
- **Việc tách `conn` ra khỏi hàm** — Chặng 2 mở một kết nối cho cả phiên chat rồi truyền vào, không phải sửa dòng nào trong `tools/`.
