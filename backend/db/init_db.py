"""Tao bang tu db/schema.sql.

Chay:  python -m db.init_db
Sinh ra data/trung_tam.db.
"""

from __future__ import annotations

import sqlite3

from core.config import db_path, schema_path
from core.logging import get_logger
from db.connection import get_conn

logger = get_logger("db.init_db")


def tao_bang(conn: sqlite3.Connection) -> None:
    sql = schema_path().read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def main() -> None:
    conn = get_conn()
    tao_bang(conn)
    conn.close()
    logger.info("Da tao database tai %s", db_path())


if __name__ == "__main__":
    main()
