# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Trạng thái dự án

Giai đoạn dựng khung. Hiện chỉ có `config.py`, `db/schema.sql`, và tài liệu thiết kế. Chưa có code chạy được — chưa có `app.py`, `tools/`, `agent/`, `db/init_db.py`, `tests/`.

**Nguồn sự thật duy nhất:** `docs/superpowers/specs/2026-07-27-agent-xep-lich-trung-tam-design.md`. Đọc file này trước khi làm bất cứ việc gì. Nó chứa kiến trúc, mô hình dữ liệu, danh mục công cụ, và lộ trình 5 chặng.

## Ngôn ngữ và cách làm việc

Người xây là **sinh viên IT**, làm dự án này để vừa lấy kinh nghiệm vừa dùng thật cho một trung tâm dạy thêm. Có nền tin học, nhưng **chưa từng làm agent/LLM và chưa làm backend thật**. Điều này chi phối mọi thứ:

- Trao đổi, comment trong code, tên biến/hàm, và giao diện: **tiếng Việt**.
- Mỗi bước phải kết thúc bằng một lệnh chạy được và một kết quả nhìn thấy được. Không có bước "viết 500 dòng rồi mới chạy thử".
- Giải thích khái niệm mới trước khi dùng nó. Mỗi bước giới thiệu tối đa một khái niệm mới.
- Không đi tắt bằng thư viện lạ chỉ vì gọn hơn. Ưu tiên thứ giải thích được.

## Nguyên tắc kiến trúc bất di bất dịch

**1. LLM quyết định *làm gì*, Python quyết định *kết quả*.**
Gemini chọn công cụ và diễn giải kết quả. Nó không bao giờ tự đếm buổi, so giờ, hay sinh mã phòng. Mọi con số đến từ SQL hoặc solver. Nếu một thay đổi khiến LLM phải tự tính toán, thay đổi đó sai.

**2. Tầng nghiệp vụ không biết gì về LLM.**
`db/`, `ingest/`, `tools/` là Python thuần, import được và test được mà không cần API key. Chỉ `agent/` và `app.py` chạm tới Gemini. Giữ ranh giới này — nó là lý do bộ test chạy trong vài giây và không tốn tiền.

**3. Hành động ghi luôn qua cổng duyệt.**
Không hàm ghi nào tự chạy. Trình tự bắt buộc: xem trước → người duyệt → thực thi → ghi `data/audit_log.jsonl` → hoàn tác được.

**4. Không fine-tune, không vector database.**
Cả hai đã bị loại có chủ đích (spec §4, §9). "Dạy" agent = sửa `data/noi_quy.md`, thêm công cụ, hoặc sửa prompt hệ thống. Đừng đề xuất lại RAG/embedding cho dữ liệu bảng.

## Quy ước dữ liệu

- `thu`: số nguyên **2–8**, trong đó **8 = Chủ nhật**. Không dùng chuỗi.
- `ca`: số nguyên **1–4**. Giờ giấc thật chỉ nằm trong `config.GIO_CA`, không nhét vào tên hay mã.
- Giờ giấc các ca hiện là **giá trị tạm**, chưa chốt với trung tâm. Mọi thứ phụ thuộc giờ giấc phải đọc từ `config.py`, không hardcode.
- `buoi_hoc` là bảng lõi: một dòng = một buổi cố định trong tuần. Mọi câu hỏi về lịch đều quy về việc lọc bảng này.
- Hai ràng buộc `UNIQUE(ma_phong, thu, ca)` và `UNIQUE(ma_gv, thu, ca)` trong `db/schema.sql` là lưới an toàn cuối cùng chống trùng lịch. **Không được gỡ.** Code phải bắt lỗi vi phạm và dịch thành thông báo tiếng Việt dễ hiểu, thay vì né ràng buộc.

## Lệnh

Môi trường ảo và cài đặt:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Cấu hình: chép `.env.example` thành `.env`, điền `GEMINI_API_KEY` lấy từ https://aistudio.google.com/apikey

**Các lệnh dưới đây thuộc thiết kế nhưng chưa cài đặt** — tạo file tương ứng trước khi dùng:
```powershell
python -m db.init_db          # tạo bảng từ db/schema.sql
python -m ingest.from_csv     # nạp samples/*.csv vào SQLite
pytest                        # chạy toàn bộ test
pytest tests/test_doc_lich.py::test_phong_trong -v   # chạy một test
streamlit run app.py          # mở giao diện chat
```

## Lộ trình

Làm tuần tự, không nhảy cóc. Không sang chặng sau khi chặng trước chưa đạt tiêu chí hoàn thành (spec §11).

1. **Chặng 1** — SQLite + 6 công cụ đọc + test. Chưa đụng Gemini.
2. **Chặng 2** — function calling, vòng lặp agent, chat Streamlit.
3. **Chặng 3** — công cụ ghi + duyệt + nhật ký + hoàn tác.
4. **Chặng 4** — solver OR-Tools xếp lịch + agent tự kiểm chứng.
5. **Chặng 5** — rút luật từ lịch cũ, đồng bộ Google Sheets thật, chạy nền.
