# Deploy — Vercel (frontend + FastAPI backend)

Dự án deploy toàn bộ (web tĩnh + backend FastAPI) lên Vercel dưới 1 project.
Backend chạy trên **Vercel Serverless Functions (Python 3.12)**, region mặc định (iad1).
DB dùng SQLite trong `/tmp` (reset mỗi cold-start, tự nạp lại dữ liệu mẫu).

> ⚠️ Vercel serverless: filesystem **chỉ ghi được `/tmp`**, không gọi được `localhost`
> của máy dev. Do đó trên Vercel LLM dùng **Gemini cloud** (không phải 9router local).

## 1. Chuẩn bị code cho serverless

- `api/index.py` — entrypoint Vercel, wrap FastAPI `app`, init DB `/tmp` + nạp mẫu khi cold-start.
- `core/config.py` — `db_path()` / `audit_log_path()` → `/tmp` khi `VERCEL=1`.
- `backend/scheduler/ingest/from_json.py` — bỏ ghi file `noi_quy.md` khi `VERCEL=1`.
- `vercel.json` — route `/api/*`,`/health`,`/docs` → serverless; `/` → web tĩnh; env `LLM_PROVIDER=gemini`, `VERCEL=1`.
- `api/requirements.txt` + root `requirements.txt` — deps (fastapi, uvicorn, pydantic-settings, python-dotenv, openai, numpy).
- `.vercelignore` — loại `*.db`, `.env`, `.env.local`.

## 2. Cài CLI + login

```bash
npm install -g vercel
vercel login          # mở browser xác thực
```

## 3. Link project

```bash
cd "/c/Users/TTS-VanBv/Documents/Follower/Bip/Education-agent"
vercel link --yes --project education-agent
```

## 4. Biến môi trường (Secret)

```bash
echo "AQ.Ab8...AJQ" | vercel env add GEMINI_API_KEY production
```

Thêm các env khác nếu cần: `LLM_PROVIDER`, `VERCEL` (đã set sẵn trong `vercel.json`).

## 5. Deploy

```bash
vercel deploy --prod
```

Kết quả: alias `https://education-agent-rose.vercel.app`

Mỗi lần sửa code backend → chạy lại lệnh trên để cập nhật.

## 6. Lỗi thường gặp & cách sửa

| Lỗi | Nguyên nhân | Sửa |
|---|---|---|
| `No module named 'fastapi'` | build không cài deps | bỏ `builds` khỏi `vercel.json`; đặt `api/requirements.txt` cạnh entrypoint |
| `Read-only file system` | code ghi file vào `backend/data/` | chỉ ghi `/tmp`, bỏ ghi file khi `VERCEL=1` |
| `/health` 404 | route thiếu | thêm route `/health`, `/docs` → `api/index.py` |
| API trả `[]` | DB chưa nạp (cold-start lỗi) | sửa init chỉ `INSERT` DB, không ghi file |

## 7. Verify sau deploy

```bash
curl https://education-agent-rose.vercel.app/health
curl "https://education-agent-rose.vercel.app/api/calendar/phong-trong?thu=2&ca=1"
curl -X POST https://education-agent-rose.vercel.app/api/chat -H "Content-Type: application/json" -d '{"user_id":"u1","question":"Hoc phi khoa Toan la bao nhieu?"}'
```

## 8. Commit

```bash
git add -A && git commit -m "deploy: Vercel ..." && git push origin main
```

## Giới hạn

- DB `/tmp` **không bền** (mất khi function tái tạo / deploy). Demo OK; sản xuất nên dùng Postgres.
- Cold-start lần đầu chậm (~vài giây init DB).
- Không gọi được 9router local → LLM dùng Gemini cloud.

Để có DB bền + xài 9router: deploy backend sang Railway / Render / Fly.io (container luôn bật).
