"""Tao ca 2 schema (A + B) vao CUNG 1 file database.

- Schema A (db/schema_a.py): du lieu trung tam (giao vien, phong, lop, buoi_hoc, audit).
- Schema B (db/schema_b.py): kho tri thuc trung tam (documents, document_chunks,
  memory_student) - thong tin khoa hoc, noi quy chi tiet, ho so hoc sinh.

Chay:  python -m db.init_db
Sinh ra data/trung_tam.db voi ca 2 schema cung song tai.
"""

from __future__ import annotations

import sqlite3

from core.config import db_path
from core.logging import get_logger
from db.connection import get_conn
from db.schema_a import SCHEMA_A
from db.schema_b import SCHEMA_B

logger = get_logger("db.init_db")


def tao_bang(conn: sqlite3.Connection) -> None:
    # Ca 2 schema cung nam trong 1 connection -> 1 file DB.
    conn.executescript(SCHEMA_A)
    conn.executescript(SCHEMA_B)
    conn.commit()


def main() -> None:
    conn = get_conn()
    tao_bang(conn)
    conn.close()
    logger.info("Da tao database (Schema A + B) tai %s", db_path())


if __name__ == "__main__":
    main()
