"""Nap tai lieu mau (thong tin khoa hoc) vao Schema B de test RAG.

Chay:  python -m scripts.nap_tai_lieu_mau
"""
from __future__ import annotations

from pathlib import Path

from core.config import samples_dir
from db.connection import get_conn
from db.init_db import tao_bang
from documents.service import init_docs, add_document

SRC = samples_dir() / "tai_lieu"


def main() -> None:
    conn = get_conn()
    tao_bang(conn)  # dam bao ca Schema A + B ton tai
    init_docs(conn)
    if not SRC.exists():
        print("Khong tim thay", SRC); return
    for f in SRC.glob("*.txt"):
        text = f.read_text(encoding="utf-8")
        add_document(conn, f.name, text)
        print("Da nap:", f.name)
    conn.close()


if __name__ == "__main__":
    main()
