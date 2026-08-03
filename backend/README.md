# Education Agent — Backend

Backend FastAPI cho **trung tâm dạy thêm**: gộp hai phân hệ dưới một app.

- **Phân hệ A — Agent xếp lịch**: SQLite + LLM tool-calling + human-in-the-loop.
  Không dùng vector DB cho dữ liệu lịch (theo spec, Nguyên tắc 5).
- **Phân hệ B — Gia sư RAG**: upload tài liệu → chunk → embed → truy vấn có căn cứ.
  Vector store tách biệt, chỉ dùng cho văn bản học.

## Chạy nhanh

```bash
pip install -r requirements.txt
cp .env.example .env          # điền OPENAI_API_KEY (Nous/tencent hy3:free)
python -m db.init_db          # tạo data/trung_tam.db
python -m scheduler.ingest.from_csv   # nạp samples/*.csv
uvicorn main:app --reload --port 8000
```

## Cấu trúc

```
core/        config, llm (đa provider), logging, exceptions, security, auth
db/          schema.sql, connection, init_db
scheduler/   Phân hệ A: tools/ (doc/ghi/xep_lich/noi_quy), agent/ (loop, registry, store), ingest/
documents/   Phân hệ B: upload → chunk → embed → lưu
rag/         embedder, chunking, retriever, service (truy vấn)
chat/        dịch vụ gia sư RAG
memory/      hồ sơ học sinh dài hạn
api/         routers FastAPI (health, calendar, agent, approve, scheduler, documents, rag, chat, memory)
tests/       pytest (nghiệp vụ chạy offline, không cần API key)
```

## API chính

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/health` | sống sót |
| GET | `/api/calendar/phong-trong?thu=&ca=` | phòng trống |
| POST | `/api/agent/chat` | chat agent xếp lịch |
| POST | `/api/approve` | duyệt hành động ghi (thực thi thật) |
| POST | `/api/approve/undo` | hoàn tác mọi ghi gần nhất |
| POST | `/api/scheduler/xep-lich` | xếp lịch tự động |
| GET | `/api/scheduler/xung-dot` | kiểm tra xung đột |
| POST | `/api/documents` | upload tài liệu |
| POST | `/api/rag/query` | hỏi đáp có tài liệu |
| POST | `/api/chat` | gia sư RAG |
| GET/PUT | `/api/memory/{user_id}` | hồ sơ học sinh |

## Nguyên tắc

- LLM quyết định *làm gì*, Python quyết định *kết quả* (số liệu từ SQL/solver).
- Mọi ghi đều qua duyệt + `audit_log.jsonl` + hoàn tác được.
- `thu` 2..8 (8=CN), `ca` 1..4 — đọc từ `core/config.py`, không hardcode.
- Tiếng Việt trong code; bí mật/đường dẫn từ `.env` / `core/config.py`.

## Test

```bash
python -m pytest -q
```

Mọi nghiệp vụ chạy offline (không cần API key). RAG dùng embedding local dự
phòng khi chưa có key; đổi sang embedding thật chỉ bằng `.env`.
