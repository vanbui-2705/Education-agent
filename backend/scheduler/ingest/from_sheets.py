"""Dong bo Google Sheets (Chang 5).

Thuc te: can credentials.json (service account). O day cung cap:
- sao luu DB truoc khi sync (backup .db),
- ham interface dong bo (chua noi voi Sheets that vi thieu creds).

Luu y: chi la interface; khi co creds thi dien them phan goi API Sheets.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from core.config import db_path
from scheduler.ingest.from_csv import nap_tat_ca


def sao_luu_db() -> Path:
    """Sao luu data/trung_tam.db thanh .db.bak.<timestamp> truoc khi sync."""
    src = db_path()
    if not src.exists():
        raise FileNotFoundError("Chua co DB de sao luu")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = src.with_suffix(f".db.bak.{ts}")
    shutil.copy(src, dst)
    return dst


def dong_bo_tu_sheets(conn) -> dict:
    """Interface dong bo. Hien tai: chi sao luu + nap lai tu CSV mau.

    Khi co Google credentials, thay phan nay bang doc Sheets -> ghi bang tam -> nap_tat_ca.
    """
    bak = sao_luu_db()
    # Placeholder: nap lai tu CSV mau (thay the bang doc Sheets that sau).
    nap_tat_ca(conn)
    return {"ok": True, "backup": str(bak), "msg": "da sao luu + nap lai (chua noi Sheets that)"}
