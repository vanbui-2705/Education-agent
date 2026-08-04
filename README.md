# Education Agent

Hệ thống hỗ trợ trung tâm dạy thêm, gồm **2 phân hệ** chạy chung 1 database (2 schema riêng biệt):

- **Phân hệ A — Agent xếp lịch trung tâm**: AI agent tra cứu & ghi lịch (phòng, giáo viên, lớp, buổi học) qua tool-calling, có bước duyệt (human-in-the-loop) trước khi ghi.
- **Phân hệ B — Gia sư RAG**: chatbot gia sư trả lời từ kho tài liệu (RAG local, embedder `numpy`), có nhớ hồ sơ học sinh.

> Không dùng vector DB cho lịch (theo spec). Tiếng Việt trong code & giao diện.

## 🔗 Link demo

- **Web (Vercel, public):** https://education-agent-rose.vercel.app
- **API docs:** https://education-agent-rose.vercel.app/docs

## 🧱 Cấu trúc

```
Education-agent/
├── backend/                 # FastAPI backend (Phân hệ A + B)
│   ├── core/                # config, llm (9router / gemini / openai)
│   ├── db/                  # SQLite 2 schema (trung tâm + kho tri thức)
│   ├── scheduler/           # agent xếp lịch (tools, registry, loop, prompts)
│   ├── documents/ rag/ chat/ memory/   # Phân hệ B (RAG, gia sư, hồ sơ)
│   ├── api/                 # routers FastAPI
│   ├── web/index.html       # trang test UI
│   └── samples/             # dữ liệu mẫu (trung_tam.json, tai_lieu/)
├── api/index.py             # Vercel serverless entry (wrap FastAPI)
├── vercel.json              # cấu hình deploy Vercel
├── requirements.txt         # deps (root, cho Vercel)
└── DEPLOY.md                # hướng dẫn deploy
```

## 💻 Chạy local

Yêu cầu: Python 3.10+, [9router](https://github.com/...) đang chạy local (tùy chọn, để xài claude).

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Tạo DB + nạp dữ liệu mẫu
python -m db.init_db
python -m scheduler.ingest.from_json
python -m scripts.nap_tai_lieu_mau

# Chỉnh .env (LLM_PROVIDER=9router hoặc gemini)
cp .env.example .env   # rồi điền key

# Chạy server (chỉ localhost, không public)
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Mở: http://127.0.0.1:8000/ (web test) · http://127.0.0.1:8000/docs (Swagger)

## 🔑 Cấu hình (`.env`)

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `LLM_PROVIDER` | `9router` \| `gemini` \| `openai` | `9router` |
| `NINEROUTER_BASE_URL` | gateway 9router | `http://localhost:20128/v1` |
| `NINEROUTER_MODEL` | model qua 9router | `claude-3-7-sonnet` |
| `GEMINI_API_KEY` | key Gemini (khi dùng gemini) | — |

Xem `backend/.env.example`. **Không commit `.env`.**

## 📡 API chính

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | health check |
| GET | `/api/calendar/phong-trong?thu=&ca=` | phòng trống |
| GET | `/api/calendar/giao-vien-ranh?thu=&ca=` | GV rảnh |
| GET | `/api/scheduler/xung-dot` | kiểm tra xung đột |
| POST | `/api/agent/chat` | agent xếp lịch (chat + tool) |
| POST | `/api/approve` | duyệt hành động ghi |
| POST | `/api/chat` | gia sư RAG |
| POST | `/api/rag/query` | truy vấn RAG thô |
| POST/GET | `/api/documents`, `/api/memory/{uid}` | tài liệu & hồ sơ |

Chi tiết: `backend/README.md`, `backend/PLAN.md`.

## 🚀 Deploy

Xem **`DEPLOY.md`** — deploy frontend + backend lên Vercel (serverless Python).
