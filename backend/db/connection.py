"""Mo ket noi SQLite qua mot cho duy nhat.

Moi noi khong duoc tu goi sqlite3.connect. Luon thong qua get_conn de:
- tu tao thu muc cha neu chua co,
- doc dong tra ve theo ten cot (row_factory),
- bat kiem tra khoa ngoai cho chinh ket noi do.
"""

from __future__ import annotations

from pathlib import Path

import sqlite3

from core.config import db_path


def get_conn(db_path_arg: Path | None = None) -> sqlite3.Connection:
    path = db_path_arg if db_path_arg is not None else db_path()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
