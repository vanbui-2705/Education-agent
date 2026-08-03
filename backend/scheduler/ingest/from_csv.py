"""Nap du lieu mau tu CSV vao SQLite (Chang 1).

Chay tu thu muc goc backend/:  python -m scheduler.ingest.from_csv
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from core.config import samples_dir
from core.logging import get_logger

logger = get_logger("ingest.from_csv")

_BANG_FILE = {
    "giao_vien": "giao_vien.csv",
    "phong": "phong.csv",
    "lop": "lop.csv",
    "buoi_hoc": "buoi_hoc.csv",
}


def nap_csv(conn: sqlite3.Connection, bang: str, file: Path) -> int:
    text = Path(file).read_text(encoding="utf-8").splitlines()
    rows = list(csv.DictReader(text))
    if not rows:
        return 0
    cols = list(rows[0].keys())
    placeholders = ",".join("?" for _ in cols)
    col_sql = ",".join(cols)
    sql = f"INSERT OR IGNORE INTO {bang} ({col_sql}) VALUES ({placeholders})"
    conn.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
    conn.commit()
    return len(rows)


def nap_tat_ca(conn: sqlite3.Connection, samples_dir_arg: Path | None = None) -> dict:
    d = Path(samples_dir_arg) if samples_dir_arg else samples_dir()
    ket_qua = {}
    for bang, file in _BANG_FILE.items():
        n = nap_csv(conn, bang, d / file)
        ket_qua[bang] = n
        logger.info("Nap %s: %d dong vao bang %s", file, n, bang)
    return ket_qua


def main() -> None:
    from db.connection import get_conn

    conn = get_conn()
    nap_tat_ca(conn)
    conn.close()
    logger.info("Hoan tat nap du lieu mau.")


if __name__ == "__main__":
    main()
