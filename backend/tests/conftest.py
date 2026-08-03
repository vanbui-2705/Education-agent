"""Fixture chung: tao database tam nap san du lieu mau co dinh.

Dung tempfile de khong anh huong data/trung_tam.db that. Moi test co mot DB moi.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import sqlite3

from db.connection import get_conn
from db.init_db import tao_bang
from scheduler.ingest.from_csv import nap_tat_ca  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def real_db_ready():
    """Dam bao data/trung_tam.db that co bang + du lieu de cac API test khong bi 'no such table'."""
    from core.config import db_path

    p = db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        conn = get_conn()
        tao_bang(conn)
        nap_tat_ca(conn)
        conn.close()
    yield


@pytest.fixture
def temp_db() -> sqlite3.Connection:
    """Database tam, da tao 4 bang, CHUA co du lieu."""
    fd, path = tempfile.mkstemp(suffix=".db")
    import os
    os.close(fd)
    conn = get_conn(Path(path))
    tao_bang(conn)
    yield conn
    conn.close()
    os.remove(path)


@pytest.fixture
def sample_db(temp_db: sqlite3.Connection) -> sqlite3.Connection:
    """Database tam da nap du lieu mau tu samples/."""
    nap_tat_ca(temp_db)
    return temp_db
