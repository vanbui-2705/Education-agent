"""Test Phan he B: RAG chunk/embed/retrieve + documents + rag query (OFFLINE)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from db.connection import get_conn
from db.init_db import tao_bang
from documents.service import init_docs, add_document, list_documents
from rag.service import rag_query
from rag.chunking import chunk_text
from rag.embedder import embed_texts


def _fresh_db() -> sqlite3.Connection:
    import tempfile, os
    fd, p = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = get_conn(Path(p))
    tao_bang(conn)
    init_docs(conn)
    return conn


def test_chunk_text() -> None:
    text = "Chuong 1. Toan hoc rat hay. " * 40
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) > 1
    assert all(len(c) <= 110 for c in chunks)


def test_embed_deterministic() -> None:
    a = embed_texts(["hello world"])[0]
    b = embed_texts(["hello world"])[0]
    assert a == b
    assert len(a) == 256


def test_rag_query_tra_dung_nguon() -> None:
    conn = _fresh_db()
    try:
        add_document(conn, "ly.txt",
                     "Dinh luat Ohm: I = U / R. Dong dien ti le voi hieu dien the.")
        add_document(conn, "hoa.txt",
                     "Nuoc H2O duoc tao tu hydrogen va oxygen.")
        res = rag_query(conn, "dinh luat Ohm la gi", k=1)
        assert res["sources"] == ["ly.txt"]
        assert "Ohm" in res["contexts"][0]
    finally:
        p2 = Path(conn.execute("PRAGMA database_list").fetchone()[2])
        conn.close()
        p2.unlink(missing_ok=True)
