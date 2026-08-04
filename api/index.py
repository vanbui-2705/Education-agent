"""Vercel Python runtime entry.

Chay FastAPI tu backend/ tren Vercel. SQLite dung /tmp (writable).
Khi cold start, tao DB + nap du lieu mau neu chua co.
"""
import os
import sys
from pathlib import Path

# them backend/ vao sys.path
BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

# Danh dau dang chay tren Vercel de db/connection dung /tmp
os.environ.setdefault("VERCEL", "1")

# Import app (main.py nam o backend/)
from main import app  # noqa: E402

# Lazy init DB tren Vercel (chi lan dau)
_vercel_inited = False
def _ensure_db():
    global _vercel_inited
    if _vercel_inited:
        return
    try:
        import importlib
        from core.config import db_path
        dbp = db_path()
        if not dbp.exists():
            from db.init_db import tao_bang
            import sqlite3
            conn = sqlite3.connect(str(dbp))
            tao_bang(conn)
            conn.close()
            # nap du lieu mau (chi insert DB, khong ghi file vi Vercel read-only FS)
            try:
                import runpy
                runpy.run_module("scheduler.ingest.from_json", run_name="__main__")
            except Exception as e:  # noqa
                print("from_json loi:", e)
            try:
                from documents.service import add_document
                from db.connection import get_conn
                mau = BACKEND / "samples" / "tai_lieu" / "khoa_hoc.txt"
                if mau.exists():
                    txt = mau.read_text(encoding="utf-8")
                    c = get_conn()
                    try:
                        add_document(c, "khoa_hoc.txt", txt)
                        c.commit()
                    finally:
                        c.close()
            except Exception as e:  # noqa
                print("nap tai lieu mau loi:", e)
        _vercel_inited = True
    except Exception as e:  # noqa
        print("ensure_db loi:", e)

# Vercel Python goi app truc tiep (ASGI). Hook init bang startup event da co
# trong main.py (lifespan). Nhung de chac chan, goi ensure_db truoc tiep nhan.
try:
    _ensure_db()
except Exception:  # noqa
    pass
