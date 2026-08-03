# Kế hoạch Backend — Education Agent (gộp 2 phân hệ)

> **Trạng thái thư mục `backend/`:** 9 folder rỗng (`api, calendar, chat, core, db,
> documents, memory, rag, tests`) + `.gitkeep`.
> **Nguồn sự thật:** `../CLAUDE.md` và
> `../docs/superpowers/specs/2026-07-27-agent-xep-lich-trung-tam-design.md`.
> **Quyết định:** gộp **Agent xếp lịch trung tâm** (theo spec) + **Module gia sư RAG**
> vào một FastAPI backend.

---

## 0. Cách giải quyết xung đột

`backend/` có skeleton gợi ý "gia sư RAG" (`rag, documents, memory, chat, calendar`).
Nhưng `CLAUDE.md` ở thư mục cha mô tả sản phẩm **khác**: *Agent xếp lịch trung tâm
dạy thêm*, dùng SQLite + Gemini + tool-calling + human-in-the-loop, và **cấm vector
database / fine-tune cho dữ liệu bảng** (Nguyên tắc 5, §9 spec).

→ Gộp bằng cách tách thành **hai phân hệ độc lập**, chung một vỏ FastAPI:

- **Phân hệ A — Agent xếp lịch (theo spec):** giữ nguyên triết lý spec. Công cụ là
  hàm Python thuần, LLM chỉ quyết định *gọi công cụ nào*, ghi phải qua duyệt, có
  `audit_log` và `hoan_tac`. **KHÔNG dùng vector DB** cho dữ liệu lịch.
- **Phân hệ B — Gia sư RAG:** module riêng, dùng vector store **cho tài liệu học**
  (miền dữ liệu khác, không vi phạm cấm của spec vì spec cấm vector DB *cho dữ liệu
  bảng lịch*, không cấm RAG cho văn bản). Hoạt động tách biệt với Phân hệ A.

---

## 1. Nguyên tắc bất di bất dịch (giữ nguyên từ spec)

1. **LLM quyết định *làm gì*, Python quyết định *kết quả*.** Mọi con số do SQL/solver
   sinh ra, không do LLM bịa.
2. **Tầng nghiệp vụ không biết LLM.** `db/`, `calendar/ingest/`, `calendar/tools/`
   là Python thuần, import/test được không cần API key. Chỉ `calendar/agent/` và
   `api/` chạm LLM.
3. **Hành động ghi luôn qua cổng duyệt.** Xem trước → người duyệt → thực thi →
   ghi `audit_log.jsonl` → hoàn tác được.
4. **Tài liệu/prompt không chứa code.** Plan/spec mô tả file, chữ ký hàm, hành vi,
   ca kiểm thử, lệnh chạy. Code thật nằm trong `.py`.
5. **Mỗi bước phải chạy được** và kết thúc bằng kết quả nhìn thấy được.
6. **Tiếng Việt** cho comment, docstring, tên biến, thông báo.
7. **Không viết cứng** đường dẫn Windows / bí mật — đọc từ `core/config.py` / `.env`.

---

## 2. Cấu trúc thư mục (map skeleton ↔ spec)

`backend/` là project root (PYTHONPATH = backend). Mỗi folder là package.

| Folder backend | Trách nhiệm | Tương ứng spec |
|---|---|---|
| `main.py` | App factory FastAPI, mount routers, lifespan | (mới, thay `app.py` Streamlit) |
| `core/` | `config.py` (pydantic-settings), `llm.py` (bọc LLM đa provider), `security.py` (API key), `logging.py`, `exceptions.py` | `config.py` + bọc API |
| `db/` | `schema.sql` (4 bảng scheduling), `connection.py`, `init_db.py`, + module vector store cho RAG | `db/` (spec) |
| `scheduler/` | **Phân hệ A:** `tools/` (doc_lich, ghi_lich, xep_lich, noi_quy), `agent/` (loop, prompts, gemini client), `ingest/` (csv/sheets), `service.py` | `tools/`, `agent/`, `ingest/` spec |
| `documents/` | **Phân hệ B:** upload + parse (txt/md/pdf/docx) → chunk | (mới) |
| `rag/` | **Phân hệ B:** `chunking.py`, `embedder.py`, `retriever.py`, `rerank.py` | (mới) |
| `memory/` | **Phân hệ B:** hồ sơ học sinh dài hạn (khác `audit_log` của A) | (mới) |
| `chat/` | **Phân hệ B:** dịch vụ hội thoại gia sư có RAG, streaming | (mới) |

> **Ghi chú đặt tên:** thư mục Phân hệ A đặt là `scheduler/` (không phải `calendar/`)
> vì `calendar` là tên module chuẩn của Python — giữ `calendar/` sẽ đè lên stdlib và
> làm hỏng cả FastAPI TestClient lẫn mọi import `import calendar`. Đã đổi trong code thực tế.
| `api/` | routers FastAPI: `health`, `calendar`, `agent`, `documents`, `rag`, `chat`, `memory`, `approve`, `deps` | (mới, vỏ HTTP) |
| `tests/` | pytest: nghiệp vụ A chạy offline; B có test RAG | `tests/` spec |

---

## 3. Tech Stack

| Hạng mục | Lựa chọn |
|---|---|
| Web | **FastAPI** + Pydantic v2 + Uvicorn (đã cài) |
| Config | **pydantic-settings** (đã cài) |
| Scheduling DB | **sqlite3** thuần (spec bắt buộc), `schema.sql`, khoá ngoại bật |
| RAG store | dev: SQLite lưu embedding + cosine bằng Python; prod: tuỳ chọn pgvector/Chroma |
| LLM | `core/llm.py` đa provider: mặc định **OpenAI-compatible** (client đã cài, dùng
>   endpoint Nous/tencent), hỗ trợ **Gemini** (theo spec) |
| Embeddings | OpenAI-compatible embeddings (hoặc local `sentence-transformers` sau) |
| Test | **pytest** + httpx (đã cài) |
| Đóng gói | Docker image giai đoạn sau (spec §2) |

> Gói cần thêm `requirements.txt`: `pytest`. Các gói RAG (pdf/docx parse, vector)
> thêm khi bắt Phân hệ B.

---

## 4. Phân hệ A — Agent xếp lịch (theo spec, 5 chặng)

### 4.1 Dữ liệu (`db/`)
- `schema.sql`: 4 bảng `giao_vien`, `phong`, `lop`, `buoi_hoc`.
- `buoi_hoc`: `ma_lop, ma_gv, ma_phong, thu(2–8, 8=CN), ca(1–4)` — ba mã là khoá ngoại.
- Hai ràng buộc `UNIQUE(ma_phong, thu, ca)` và `UNIQUE(ma_gv, thu, ca)` — **cấm gỡ**.
- `connection.py`: `get_conn(db_path=None) -> sqlite3.Connection` (tạo thư mục cha,
  `row_factory` theo tên, bật khoá ngoại).
- `init_db.py`: `tao_bang(conn)`, `main()` sinh `data/trung_tam.db`.

### 4.2 Công cụ (`calendar/tools/`) — Python thuần, offline
Mọi công cụ: nhận **db handle làm tham số đầu**, trả **`list[dict]`**, không tìm thấy
thì trả danh sách rỗng, chỉ ném lỗi khi *tham số* sai.
- ĐỌC: `tra_lich_giao_vien`, `tra_lich_phong`, `tra_lich_lop`, `phong_trong`,
  `giao_vien_ranh`, `tim_giao_vien` (khớp gần đúng, bỏ dấu).
- GHI (qua cổng duyệt): `tao_buoi_hoc`, `doi_buoi_hoc`, `huy_buoi_hoc`, `hoan_tac`.
- TÍNH: `kiem_tra_xung_dot`, `xep_lich` (OR-Tools CP-SAT ở Chặng 4).
- LUẬT: `doc_noi_quy`, `de_xuat_luat`.

### 4.3 Ingest (`calendar/ingest/`)
- `from_csv.py`: nạp `samples/*.csv` → SQLite.
- `from_sheets.py`: đồng bộ Google Sheets (Chặng 5), sao lưu `.db` trước khi sync.

### 4.4 Agent (`calendar/agent/`)
- `gemini_client.py`: bọc lời gọi LLM (qua `core/llm.py` đa provider).
- `prompts.py`: prompt hệ thống + nội dung `noi_quy.md`.
- `loop.py`: vòng lặp tối đa 25 vòng — gửi lịch sử + lược đồ công cụ → nếu model trả
  văn bản → trả người dùng; nếu trả gọi công cụ → chạy, đưa kết quả lại lịch sử.
  Công cụ GHI chưa duyệt → hiện bản xem trước, dừng chờ người. Lỗi công cụ → trả
  thông báo, agent tự thử cách khác.

### 4.5 Trí nhớ (Phân hệ A)
- Ngắn hạn: hội thoại trong phiên (biến FastAPI/Streamlit).
- Dài hạn: `data/noi_quy.md` (người sửa được).
- Sự kiện: `data/audit_log.jsonl` (mọi ghi → hoàn tác).

---

## 5. Phân hệ B — Gia sư RAG (module riêng, không dính lịch)

- `documents/service.py` + `parsers.py`: upload (multipart) → parse → chunk.
- `rag/chunking.py`: tách đoạn; `rag/embedder.py`: embedding qua `core/llm.py`;
  `rag/retriever.py`: top-k; `rag/rerank.py` (tuỳ chọn).
- `chat/service.py`: build prompt có context RAG → LLM streaming (SSE).
- `memory/store.py`: hồ sơ học sinh dài hạn (bảng riêng, khác `audit_log` của A).
- Vector store **tách biệt** DB scheduling; cosine tính bằng Python ở dev.

---

## 6. Data Model tóm tắt

**Scheduling (`db/schema.sql`):** `giao_vien(ma_gv, ten)`, `phong(ma_phong, suc_chua)`,
`lop(ma_lop, ten_lop, mon, si_so)`, `buoi_hoc(id, ma_lop, ma_gv, ma_phong, thu, ca)`
+ 2 UNIQUE. Quy ước `thu` 2–8, `ca` 1–4 đọc từ `core/config.py`.

**RAG (dev, SQLite):** `documents(id, owner_id, filename, mime, status, meta)`,
`document_chunks(id, document_id, idx, text, embedding_blob)`.

---

## 7. API endpoints (FastAPI routers trong `api/`)

| Router | Endpoint | Mục đích |
|---|---|---|
| `health` | `GET /health` | sống sót |
| `calendar` | `GET /api/calendar/phong-trong?thu=&ca=` … | truy vấn lịch (nhóm ĐỌC) |
| `agent` | `POST /api/agent/chat` | chat → agent xếp lịch (SSE) |
| `approve` | `POST /api/approve` | người duyệt hành động GHI (human-in-the-loop) |
| `documents` | `POST /api/documents`, `GET /api/documents`, `DELETE /api/documents/{id}` | upload/tra cứu RAG |
| `rag` | `POST /api/rag/query` | hỏi đáp có tài liệu |
| `chat` | `POST /api/chat` | hội thoại gia sư RAG (SSE) |
| `memory` | `GET/PUT /api/memory/{user_id}` | hồ sơ học sinh |

---

## 8. LLM client (`core/llm.py`)

Abstraction đa provider, interface:
- `chat(messages, tools=None) -> TextResponse | ToolCallResponse`
- `embed(texts: list[str]) -> list[list[float]]`
- Mặc định OpenAI-compatible (dùng client đã cài + base_url Nous/tencent);
  cấu hình Gemini qua env. Giữ spec: model **chỉ** trả "muốn gọi hàm X" hoặc văn bản.

---

## 9. Lộ trình (milestones)

### Phase 0 — Scaffold (nền móng)
- `requirements.txt`, `.env.example`, `main.py` (app factory + lifespan).
- `core/config.py`, `core/logging.py`, `core/exceptions.py`, `core/security.py`.
- `api/health.py` + `tests/test_health.py`.
- ✅ `uvicorn main:app --reload`, `GET /health` xanh.

### Phase 1 — Phân hệ A, Chặng 1 (DB + công cụ đọc, offline)
- `db/schema.sql`, `db/connection.py`, `db/init_db.py`.
- `calendar/tools/doc_lich.py` (6 công cụ ĐỌC) + `calendar/ingest/from_csv.py`.
- `tests/test_db.py` (2 UNIQUE), `tests/test_doc_lich.py`, `tests/test_ingest.py`.
- ✅ `pytest` xanh; gọi `phong_trong(3,2)` ra đúng. **Chưa đụng LLM.**

### Phase 2 — Phân hệ A, Chặng 2–3 (agent + ghi + duyệt)
- `core/llm.py`, `calendar/agent/{gemini_client,prompts,loop}.py`.
- `calendar/tools/{ghi_lich,noi_quy}.py`, `audit_log`, `hoan_tac`.
- `api/agent.py` (chat SSE) + `api/approve.py` + `api/calendar.py`.
- ✅ "cô Lan dạy buổi nào?" → đúng; "xếp T9A cô Lan T5C2 P302" → xem trước →
  duyệt → DB đổi → hoàn tác về cũ.

### Phase 3 — Phân hệ A, Chặng 4 (xếp lịch tự động)
- `calendar/tools/xep_lich.py` (OR-Tools), `kiem_tra_xung_dot`.
- ✅ 10 lớp chưa lịch → phương án đầy đủ, `kiem_tra_xung_dot` báo 0 lỗi.

### Phase 4 — Phân hệ B (Gia sư RAG) — track song song
- `documents/`, `rag/`, `chat/`, `memory/`, routers tương ứng.
- ✅ upload 1 file → query trả đúng đoạn + cite nguồn.

### Phase 5 — Phân hệ A, Chặng 5 + hoàn thiện
- `de_xuat_luat`, thống kê từ lịch cũ, `from_sheets.py`, chạy nền.
- Auth JWT, CORS, docs, suite pytest đầy đủ, Docker.

---

## 10. Checklist tuân thủ spec
- [ ] Công cụ A nhận db handle đầu, trả `list[dict]`, offline-testable.
- [ ] 2 UNIQUE trên `buoi_hoc` không bị gỡ; vi phạm → thông báo tiếng Việt.
- [ ] Ghi A luôn qua duyệt + `audit_log` + `hoan_tac`.
- [ ] Không vector DB cho dữ liệu bảng lịch (RAG chỉ dùng cho tài liệu).
- [ ] `thu`/`ca` đọc từ `core/config.py`, không hardcode.
- [ ] Tiếng Việt trong code + comment; path/secret từ config/env.
- [ ] Mỗi phase kết thúc bằng lệnh chạy được + kết quả thấy được.

---

## 11. Câu hỏi còn treo (spec §15 — nằm gọn trong config, đổi sau không đau)
1. Giờ giấc thật của 4 ca và số ca/ngày.
2. Trung tâm có dạy Chủ nhật không.
3. Một giáo viên tối đa bao nhiêu buổi/tuần.
4. Quy tắc phòng học chi tiết.

---

## 12. Bước tiếp theo
Sau khi duyệt, bắt đầu **Phase 0 + Phase 1** (scaffold + DB + công cụ đọc), chạy
`pytest` và `GET /health` để có artifact chạy được ngay — đúng tinh thần "mỗi bước
phải chạy được" của spec.
