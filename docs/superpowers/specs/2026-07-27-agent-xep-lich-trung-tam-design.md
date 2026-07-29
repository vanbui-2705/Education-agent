# Thiết kế: Agent quản lý & xếp lịch trung tâm

**Ngày:** 2026-07-27
**Trạng thái:** chờ duyệt
**Người học/xây:** sinh viên IT — làm để lấy kinh nghiệm, đồng thời dùng thật cho một trung tâm dạy thêm

---

## 1. Mục tiêu

Xây một **agent** cho trung tâm dạy thêm, đi qua 5 chặng, mỗi chặng chạy được và học được:

1. Hỏi đáp thường bằng tiếng Việt.
2. Trả lời chính xác về lịch dạy và lịch phòng đang có.
3. Thay đổi được lịch thật (thêm/đổi/huỷ buổi) khi được duyệt.
4. Tự xếp lịch cả tuần cho giáo viên — phòng — lớp mà không trùng.
5. Rút luật từ lịch cũ, đề xuất cho quản lý duyệt, tự chạy nền.

Mục tiêu song song, quan trọng ngang bằng: **người xây — sinh viên IT — học được nghề qua chính dự án này**. Mỗi bước có phần lý thuyết đọc trước, code sau, chạy thử ngay. Dự án đủ thật để đem đi phỏng vấn, không phải bài tập.

## 2. Phạm vi

**Làm:**
- Agent chat qua web (Streamlit), tiếng Việt.
- Dữ liệu nguồn: Google Sheets (và CSV khi thử nghiệm), đồng bộ xuống SQLite.
- Công cụ đọc: tra lịch, tìm phòng trống, tìm giáo viên rảnh.
- Công cụ ghi: tạo/đổi/huỷ buổi học, có bước duyệt của người.
- Bộ xếp lịch tự động (đầu vào: danh sách lớp + giáo viên; đầu ra: thứ, ca, phòng, giáo viên).
- File luật `noi_quy.md` do quản lý tự sửa bằng tiếng Việt.

**Đóng gói:** dự án sẽ chạy trong **Docker image** ở giai đoạn sau. Phiên bản Python được ghim trong `Dockerfile`, nên môi trường máy cá nhân không phải là ràng buộc. Giai đoạn đầu vẫn dùng môi trường ảo để chạy nhanh; Docker thêm vào sau khi có thứ đáng đóng gói. Hệ quả cho thiết kế: mọi đường dẫn đọc từ `config.py`, mọi bí mật đọc từ biến môi trường — không viết cứng đường dẫn Windows vào code.

**Không làm (giai đoạn này):**
- Quản lý học phí, điểm danh, học bạ.
- Nhiều cơ sở/chi nhánh.
- Ứng dụng di động.
- Fine-tune model. Không có bước này, và sẽ giải thích rõ vì sao ở §4.
- Quy tắc chi tiết về phòng học (triển khai sau; hệ thống chừa sẵn chỗ trong `noi_quy.md`).

## 3. Thang bậc: đang ở đâu, đi tới đâu

| Bậc | Tên | Đặc trưng |
|---|---|---|
| 0 | Chatbot | LLM + prompt. Không biết dữ liệu trung tâm. |
| 1 | Chatbot có dữ liệu | Đọc tài liệu trả lời. Chỉ đọc, một lượt. |
| 2 | Trợ lý gọi công cụ | LLM chọn công cụ, Python tra dữ liệu, số liệu đúng. |
| 3 | **Agent** | Có mục tiêu. Nhiều bước. **Ghi được**. Tự kiểm chứng kết quả, sai thì làm lại. Có trí nhớ. |
| 4 | Agent tự chủ | Tự kích hoạt theo lịch/sự kiện. Đề xuất luật mới. |

Đích: Bậc 3 đầy đủ, chạm Bậc 4 ở chặng cuối.

Bốn thứ ngăn cách Bậc 2 và Bậc 3 — đây là xương sống của toàn bộ thiết kế:

1. **Hành động ghi** — đọc sai thì vô hại, ghi sai thì hỏng lịch thật. Ghi bắt buộc đi kèm xem trước + duyệt + log + hoàn tác.
2. **Vòng lặp nhiều bước** — một mục tiêu, agent tự chạy nhiều vòng, không phải hỏi-đáp một lượt.
3. **Tự kiểm chứng** — agent chạy bộ kiểm tra trên chính kết quả mình vừa tạo; còn lỗi thì tự sửa, không đẩy cho người.
4. **Trí nhớ** — ngắn hạn (hội thoại) và dài hạn (luật đã duyệt).

## 4. Nguyên tắc nền

**Nguyên tắc 1 — LLM quyết định *làm gì*, Python quyết định *kết quả*.**
Gemini đọc câu hỏi tiếng Việt, chọn công cụ, diễn giải kết quả. Nó không bao giờ tự đếm buổi, tự so giờ, tự bịa mã phòng. Mọi con số do SQL hoặc thuật toán sinh ra.
*Vì sao:* mô hình ngôn ngữ dự đoán chữ tiếp theo. Nó rất giỏi diễn đạt và rất dở đếm chính xác. Giao việc đúng sở trường.

**Nguyên tắc 2 — Không có bước "train".**
Gemini đã biết tiếng Việt. Cái nó thiếu là dữ liệu trung tâm bạn — và dữ liệu đó nạp vào *lúc chạy* qua công cụ, không phải *lúc train*. "Dạy" agent nghĩa là: sửa file luật, thêm công cụ, sửa prompt. Cả ba đều là file văn bản, sửa xong chạy lại là có hiệu lực ngay.

**Nguyên tắc 3 — Ghi thì phải duyệt.**
Không có hành động ghi nào chạy thẳng. Luôn: agent trình bản xem trước → người bấm duyệt → ghi + log → có nút hoàn tác.

**Nguyên tắc 4 — Mỗi bước phải chạy được.**
Không có bước nào "viết code 3 ngày rồi mới thấy kết quả". Mỗi bước kết thúc bằng một lệnh chạy và một kết quả nhìn thấy được.

**Nguyên tắc 5 — Tài liệu và prompt không chứa code.**
Spec, kế hoạch thi công, và prompt gửi cho model chỉ mô tả: file nào, hàm nào, **chữ ký hàm** (tên, kiểu tham số, kiểu trả về), hành vi mong đợi, ca kiểm thử, lệnh chạy, kết quả mong đợi. Không dán thân hàm, không dán khối test đầy đủ.

*Vì sao:* code trong tài liệu tốn token gấp nhiều lần phần mô tả, mà lại lỗi thời ngay khi code thật đổi — thành ra hai nguồn sự thật đá nhau. Chữ ký hàm và hành vi thì ổn định; thân hàm thì không. Code thật nằm trong file `.py`, đọc ở đó.

*Ngoại lệ hẹp:* được phép trích tối đa **một dòng** khi chính dòng đó là thứ đang bàn (một câu SQL then chốt, một thông báo lỗi phải khớp chính xác, một lệnh terminal).

## 5. Kiến trúc

```
Trình duyệt (Streamlit)
        │  "thứ 3 ca 2 phòng nào trống?"
        ▼
┌─────────────────────────────────────────┐
│  Vòng lặp Agent  (agent/loop.py)        │
│    ├─ prompt hệ thống + luật            │
│    ├─ trí nhớ hội thoại                 │
│    └─ lặp: hỏi Gemini → gọi tool →      │
│              đưa kết quả lại cho Gemini  │
└───────────────┬─────────────────────────┘
                │
        ┌───────▼────────┐
        │  tools/        │
        │  ĐỌC:  tra_lich, phong_trong, giao_vien_ranh
        │  GHI:  tao_buoi, doi_buoi, huy_buoi   (qua cổng duyệt)
        │  TÍNH: xep_lich, kiem_tra_xung_dot
        └───┬──────────┬─────────────┬──────┘
            │          │             │
        ┌───▼───┐  ┌───▼──────┐  ┌───▼────────┐
        │SQLite │  │noi_quy.md│  │ Solver      │
        └───▲───┘  └──────────┘  └────────────┘
            │
    ┌───────┴────────┐
    │ ingest/        │  Google Sheets / CSV → SQLite
    └────────────────┘
```

Bốn tầng tách rõ, mỗi tầng test riêng được:
- `ingest/` — nạp dữ liệu vào. Không biết gì về LLM.
- `db/` + `tools/` — logic nghiệp vụ thuần Python. Không biết gì về LLM. **Chạy và test được mà không tốn một đồng API nào.**
- `agent/` — nói chuyện với Gemini, điều phối công cụ.
- `app.py` — giao diện.

Tách như vậy vì: 80% lỗi sẽ nằm ở tầng nghiệp vụ, và tầng đó test bằng pytest trong 1 giây, không cần gọi API.

## 6. Mô hình dữ liệu

Bốn bảng SQLite. Định nghĩa đầy đủ nằm trong `db/schema.sql` — đây là bản tóm tắt.

| Bảng | Cột | Ghi chú |
|---|---|---|
| `giao_vien` | `ma_gv` (khoá chính), `ten` | |
| `phong` | `ma_phong` (khoá chính), `suc_chua` | |
| `lop` | `ma_lop` (khoá chính), `ten_lop`, `mon`, `si_so` | |
| `buoi_hoc` | `id` (khoá chính, tự tăng), `ma_lop`, `ma_gv`, `ma_phong`, `thu`, `ca` | ba cột mã đều là khoá ngoại |

Hai ràng buộc `UNIQUE` trên `buoi_hoc`: một trên bộ ba (`ma_phong`, `thu`, `ca`), một trên bộ ba (`ma_gv`, `thu`, `ca`).

`buoi_hoc` là bảng lõi: mỗi dòng = một buổi cố định trong tuần. Mọi câu hỏi về lịch đều quy về việc lọc bảng này.

Hai ràng buộc `UNIQUE` chặn trùng **ngay ở tầng database**. Nghĩa là kể cả code sai, kể cả agent điên, database vẫn từ chối ghi hai lớp vào cùng phòng cùng giờ. Đây là lưới an toàn cuối cùng.

**Quy ước — chốt một lần, đổi về sau rất đau:**
- `thu`: số nguyên 2–8, trong đó 8 = Chủ nhật. Không dùng chữ.
- `ca`: số nguyên 1–4. Giờ giấc thật để trong bảng tra (`config.GIO_CA`), không nhét vào tên.

**Còn treo:** giờ giấc cụ thể của 4 ca và số ca thực tế — cần hỏi lại phía trung tâm. Chỗ này nằm gọn trong `config.py`, đổi không ảnh hưởng code khác.

Nguồn dữ liệu: Google Sheets là nơi quản lý sửa hằng ngày. SQLite chỉ là bản sao để agent tra nhanh, đồng bộ lại bất cứ lúc nào bằng một lệnh. Giai đoạn đầu dùng CSV mẫu trong `samples/` để khỏi vướng phần xác thực Google.

## 7. Danh mục công cụ

Mỗi công cụ là một hàm Python bình thường, có mô tả bằng tiếng Việt để Gemini biết khi nào nên gọi.

**Nhóm ĐỌC** (Chặng 1)

| Công cụ | Vào | Ra |
|---|---|---|
| `tra_lich_giao_vien` | mã hoặc tên giáo viên | các buổi dạy trong tuần |
| `tra_lich_phong` | mã phòng | các buổi đã đặt |
| `tra_lich_lop` | mã hoặc tên lớp | các buổi của lớp |
| `phong_trong` | thứ, ca | danh sách phòng chưa ai đặt |
| `giao_vien_ranh` | thứ, ca | danh sách giáo viên chưa dạy giờ đó |
| `tim_giao_vien` | chuỗi tên gần đúng | danh sách khớp (xử lý gõ thiếu dấu) |

**Nhóm GHI** (Chặng 3) — mọi hàm đi qua cổng duyệt

| Công cụ | Vào | Ra |
|---|---|---|
| `tao_buoi_hoc` | lớp, giáo viên, phòng, thứ, ca | bản xem trước + id sau khi duyệt |
| `doi_buoi_hoc` | id buổi, trường cần đổi | bản xem trước trước/sau |
| `huy_buoi_hoc` | id buổi | bản xem trước |
| `hoan_tac` | id thao tác trong log | trạng thái đã khôi phục |

**Nhóm TÍNH** (Chặng 4)

| Công cụ | Vào | Ra |
|---|---|---|
| `kiem_tra_xung_dot` | (không) hoặc một phương án | danh sách lỗi trùng/vi phạm luật |
| `xep_lich` | danh sách lớp cần xếp | phương án đầy đủ + điểm đánh giá |

**Nhóm LUẬT** (Chặng 2 trở đi)

| Công cụ | Vào | Ra |
|---|---|---|
| `doc_noi_quy` | (không) | nội dung `noi_quy.md` |
| `de_xuat_luat` | luật mới bằng tiếng Việt | chờ người duyệt rồi ghi vào file |

## 8. Vòng lặp agent

Trái tim của Bậc 3. Diễn giải từng bước:

1. Khởi tạo lịch sử hội thoại: prompt hệ thống, nội dung `noi_quy.md`, các lượt trao đổi cũ.
2. Thêm câu hỏi mới của người dùng vào lịch sử.
3. Lặp, tối đa 25 vòng:
   - Gửi lịch sử kèm danh mục công cụ cho Gemini.
   - Nếu model trả về **văn bản thường** — đưa cho người dùng, kết thúc.
   - Nếu model trả về **yêu cầu gọi công cụ**:
     - Công cụ thuộc nhóm GHI và chưa được duyệt: hiện bản xem trước, dừng chờ người bấm duyệt.
     - Chạy công cụ, thêm kết quả vào lịch sử, sang vòng sau.

Ba chi tiết quyết định chất lượng:
- **Giới hạn 25 vòng** — chặn agent lặp vô tận, đốt tiền API.
- **Kết quả công cụ luôn quay lại lịch sử** — đó là cách agent "nhìn thấy" hậu quả hành động của mình. Bỏ bước này thì nó mù.
- **Công cụ lỗi thì trả thông báo lỗi, không làm sập chương trình** — agent đọc lỗi và tự thử cách khác. Đây chính là khả năng tự phục hồi.

## 9. Trí nhớ

| Lớp | Chứa gì | Lưu ở đâu | Sống bao lâu |
|---|---|---|---|
| Ngắn hạn | Hội thoại đang diễn ra | Biến trong phiên Streamlit | Đến khi đóng tab |
| Dài hạn | Luật, quyết định đã duyệt | `data/noi_quy.md` | Vĩnh viễn, người đọc và sửa được |
| Sự kiện | Mọi thao tác ghi | `data/audit_log.jsonl` | Vĩnh viễn, để hoàn tác và truy vết |

Cố ý **không** dùng vector database. Quy mô nhỏ (dưới 15 giáo viên, dưới 10 phòng), toàn bộ nội quy nhét thẳng vào prompt vẫn thừa chỗ. Thêm vector database lúc này chỉ tăng thứ phải học mà không giải quyết vấn đề nào.

## 10. An toàn

- Hành động ghi **không bao giờ** tự chạy. Luôn xem trước → duyệt → thực thi.
- Mọi thao tác ghi vào `audit_log.jsonl`: thời điểm, câu hỏi gốc, công cụ, tham số, trạng thái trước, kết quả.
- `hoan_tac` đọc log, khôi phục trạng thái trước.
- Ràng buộc `UNIQUE` ở database là lưới cuối, độc lập với mọi tầng code.
- API key chỉ nằm trong `.env`, đã chặn trong `.gitignore`.
- Trước mỗi lần đồng bộ từ Sheets: sao lưu file `.db` kèm dấu thời gian.

## 11. Lộ trình 5 chặng

Mỗi chặng: **lý thuyết đọc trước → code → chạy thử → tiêu chí hoàn thành.**
Không sang chặng sau khi chặng trước chưa đạt tiêu chí.

### Chặng 1 — Nền dữ liệu và công cụ đọc  (Bậc 2)

*Lý thuyết cần nắm:* môi trường ảo Python là gì và vì sao cần; biến môi trường và vì sao không nhét key vào code; database quan hệ, khoá chính, khoá ngoại, ràng buộc UNIQUE; SQL `SELECT ... WHERE`, `JOIN`, `NOT IN`; hàm và kiểu dữ liệu trong Python; pytest.

*Việc làm:* dựng khung dự án; viết `schema.sql`; nạp CSV mẫu vào SQLite; viết 6 công cụ đọc, mỗi công cụ kèm test.

*Xong khi:* `pytest` xanh toàn bộ; gọi `phong_trong(3, 2)` trong terminal ra đúng danh sách phòng. **Chưa đụng gì tới Gemini.**

### Chặng 2 — Agent biết gọi công cụ  (chớm Bậc 3)

*Lý thuyết cần nắm:* LLM là gì, token, cửa sổ ngữ cảnh; prompt hệ thống khác prompt người dùng; **function calling / tool use** — cơ chế cốt lõi, model không tự chạy code mà trả về "tôi muốn gọi hàm X với tham số Y"; vòng lặp agent; vì sao model đôi khi bịa (ảo giác) và công cụ chặn nó ra sao.

*Việc làm:* lấy Gemini API key; gọi thử một câu; khai báo lược đồ công cụ; viết vòng lặp `agent/loop.py`; dựng chat Streamlit; nhớ hội thoại trong phiên.

*Xong khi:* hỏi "cô Lan dạy những buổi nào?" trên web và nhận đúng lịch, số liệu khớp database.

### Chặng 3 — Agent thay đổi được lịch thật  (Bậc 3)

*Lý thuyết cần nắm:* tác dụng phụ và tính bất biến; vì sao công cụ ghi khác hẳn công cụ đọc; mẫu thiết kế xem trước–duyệt–thực thi (human-in-the-loop); nhật ký kiểm toán; hoàn tác; giao dịch (transaction) trong database.

*Việc làm:* viết `tao_buoi_hoc`, `doi_buoi_hoc`, `huy_buoi_hoc`; cổng duyệt trong Streamlit; `audit_log.jsonl`; `hoan_tac`; xử lý lỗi vi phạm ràng buộc thành thông báo tiếng Việt dễ hiểu.

*Xong khi:* nói "xếp lớp T9A cho cô Lan thứ 5 ca 2 phòng P302" → agent hiện bản xem trước → bấm duyệt → database đổi thật → bấm hoàn tác → trở về như cũ.

### Chặng 4 — Tự xếp lịch và tự kiểm chứng  (Bậc 3 đủ)

*Lý thuyết cần nắm:* bài toán thoả ràng buộc (CSP); ràng buộc cứng và ràng buộc mềm; vì sao LLM không giải được bài toán này còn solver thì giải được; giới thiệu OR-Tools CP-SAT; hàm mục tiêu; vòng lặp tự kiểm chứng của agent.

*Việc làm:* viết `kiem_tra_xung_dot`; viết `xep_lich` bằng OR-Tools; đọc ràng buộc mềm từ `noi_quy.md`; nối vào vòng lặp agent để agent tự kiểm rồi tự sửa; trình bày phương án dạng lưới tuần.

*Xong khi:* đưa 10 lớp chưa có lịch → agent trả về phương án đầy đủ, `kiem_tra_xung_dot` báo 0 lỗi, quản lý duyệt một phát là vào lịch thật.

### Chặng 5 — Rút luật và tự chạy  (Bậc 4)

*Lý thuyết cần nắm:* khác biệt giữa "học từ dữ liệu" và "fine-tune"; thống kê mô tả trên lịch cũ; con người trong vòng lặp ở tầng luật; agent chạy nền theo lịch/sự kiện.

*Việc làm:* thống kê thói quen từ lịch cũ; `de_xuat_luat` trình quản lý duyệt rồi ghi vào `noi_quy.md`; đồng bộ Google Sheets thật; chạy nền phát hiện thay đổi (giáo viên báo nghỉ) và đề xuất phương án thay thế.

*Xong khi:* agent tự nói "tôi thấy cô Lan 90% dạy ca tối — thêm luật ưu tiên ca tối cho cô Lan?" và quản lý bấm đồng ý là luật có hiệu lực ngay lần xếp sau.

## 12. Cấu trúc thư mục

```
Ai-Agent/
├─ .env                    API key thật (không lên git)
├─ .env.example            mẫu để chép
├─ .gitignore
├─ requirements.txt
├─ README.md
├─ config.py               đường dẫn, key, quy ước thứ/ca
├─ app.py                  giao diện Streamlit
├─ data/
│  ├─ trung_tam.db         SQLite (sinh ra, không lên git)
│  ├─ noi_quy.md           luật viết bằng tiếng Việt
│  └─ audit_log.jsonl      nhật ký thao tác ghi
├─ db/
│  ├─ schema.sql
│  ├─ connection.py        mở kết nối SQLite
│  └─ init_db.py           tạo bảng
├─ ingest/
│  ├─ from_csv.py          nạp CSV → SQLite
│  └─ from_sheets.py       nạp Google Sheets → SQLite (Chặng 5)
├─ tools/
│  ├─ registry.py          gom công cụ + lược đồ cho Gemini
│  ├─ doc_lich.py          nhóm ĐỌC
│  ├─ ghi_lich.py          nhóm GHI
│  ├─ xep_lich.py          nhóm TÍNH
│  └─ noi_quy.py           nhóm LUẬT
├─ agent/
│  ├─ gemini_client.py     bọc lời gọi API
│  ├─ prompts.py           prompt hệ thống
│  └─ loop.py              vòng lặp agent
├─ tests/
│  └─ test_*.py
├─ samples/                CSV mẫu để chạy thử
└─ docs/
   ├─ superpowers/specs/   tài liệu thiết kế
   └─ hoc/                 ghi chú lý thuyết từng chặng
```

## 13. Kiểm thử

- **Test nghiệp vụ** (`tests/`) — chạy trên database tạm nạp dữ liệu mẫu cố định. Không gọi API. Chạy trong vài giây. Đây là lưới an toàn chính.
- **Test thủ công agent** — một danh sách câu hỏi mẫu kèm đáp án đúng, chạy tay sau mỗi chặng.
- **Test ràng buộc** — cố tình ghi trùng, khẳng định database từ chối.

## 14. Rủi ro

| Rủi ro | Cách xử |
|---|---|
| Agent bịa số liệu | Mọi số do công cụ sinh; prompt hệ thống cấm tự suy ra số |
| Ghi hỏng lịch thật | Xem trước + duyệt + log + hoàn tác + UNIQUE ở database |
| Hết hạn mức API miễn phí | Test nghiệp vụ không gọi API; giới hạn 25 vòng/câu |
| Quy ước ca đổi về sau | Cô lập trong `config.py` |
| Tên tiếng Việt gõ thiếu dấu | Công cụ `tim_giao_vien` khớp gần đúng |
| Người học đuối vì quá nhiều thứ mới | Mỗi bước một khái niệm mới, kết thúc bằng kết quả chạy được |

## 15. Câu hỏi còn treo

1. Giờ giấc thật của các ca và số ca mỗi ngày.
2. Trung tâm có dạy Chủ nhật không.
3. Một giáo viên tối đa bao nhiêu buổi/tuần.
4. Quy tắc phòng học chi tiết (triển khai sau).

Cả bốn đều nằm trong `config.py` hoặc `noi_quy.md` — trả lời sau không phải sửa kiến trúc.

## 16. Thuật ngữ

| Từ | Nghĩa |
|---|---|
| **LLM** | Mô hình ngôn ngữ lớn. Gemini là một LLM. Nó dự đoán chữ tiếp theo, rất giỏi diễn đạt, dở tính toán chính xác. |
| **Token** | Mẩu chữ. LLM tính tiền và giới hạn theo token, không theo câu. |
| **Prompt hệ thống** | Chỉ dẫn cố định đặt đầu mỗi cuộc trò chuyện, định hình cách agent cư xử. |
| **Function calling / tool use** | Cơ chế model trả về "tôi muốn gọi hàm X với tham số Y" thay vì trả lời thẳng. Code của bạn chạy hàm rồi đưa kết quả lại. Đây là thứ biến chatbot thành agent. |
| **Ảo giác (hallucination)** | Model bịa ra thông tin nghe hợp lý nhưng sai. Chống bằng cách bắt nó lấy số từ công cụ. |
| **Vòng lặp agent** | Chu trình lặp: hỏi model → chạy công cụ → đưa kết quả lại → hỏi tiếp, cho tới khi xong. |
| **CSP** | Bài toán thoả ràng buộc. Xếp thời khoá biểu là một CSP kinh điển. |
| **Ràng buộc cứng / mềm** | Cứng = vi phạm là hỏng (hai lớp một phòng một giờ). Mềm = nên tránh (cô Lan thích ca tối). |
| **Solver** | Chương trình chuyên giải CSP. Dùng OR-Tools của Google. |
| **Human-in-the-loop** | Người duyệt trước khi agent thực hiện hành động có hậu quả. |
| **Nhật ký kiểm toán** | File ghi lại mọi thay đổi, để truy vết và hoàn tác. |
