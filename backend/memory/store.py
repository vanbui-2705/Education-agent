"""Phan he B - Ho so hoc sinh dai han (memory).

Luu tru thong tin hoc sinh (muc tieu, diem yeu, ghi chu) tach biet voi audit_log cua A.
Dev: bang memory_student trong cung DB, key theo user_id.
"""

from __future__ import annotations

import json
import sqlite3

from db.schema_b import SCHEMA_B  # Schema B: ho so hoc sinh nam cung DB voi Schema A


def init_memory(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_B)
    conn.commit()


def get_profile(conn: sqlite3.Connection, user_id: str) -> dict:
    r = conn.execute("SELECT profile FROM memory_student WHERE user_id=?", (user_id,)).fetchone()
    if r is None:
        return {}
    return json.loads(r["profile"])


def put_profile(conn: sqlite3.Connection, user_id: str, profile: dict) -> None:
    conn.execute(
        "INSERT INTO memory_student (user_id, profile) VALUES (?,?) "
        "ON CONFLICT(user_id) DO UPDATE SET profile=excluded.profile",
        (user_id, json.dumps(profile, ensure_ascii=False)),
    )
    conn.commit()
