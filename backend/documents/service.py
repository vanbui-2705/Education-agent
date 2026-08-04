"""Phan he B - Quan ly tai lieu hoc (documents).

Upload (text/md don gian), parse -> chunk -> embed -> luu vao bang documents + document_chunks.
Dev: luu embedding duoi dang JSON blob trong SQLite, tinh cosine bang Python (rag/retriever).
"""

from __future__ import annotations

import json
import sqlite3

from rag.chunking import chunk_text
from rag.embedder import embed_texts
from db.schema_b import SCHEMA_B  # Schema B: kho tri thuc trung tam (chung 1 DB)


def init_docs(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_B)
    conn.commit()


def add_document(conn: sqlite3.Connection, filename: str, text: str,
                mime: str = "text/plain") -> int:
    """Them mot tai lieu, tach chunk, embed, luu. Tra ve document id."""
    cur = conn.execute(
        "INSERT INTO documents (filename, mime, status) VALUES (?,?,?)",
        (filename, mime, "ready"),
    )
    doc_id = cur.lastrowid
    chunks = chunk_text(text)
    if chunks:
        vecs = embed_texts(chunks)
        for i, (ch, vec) in enumerate(zip(chunks, vecs)):
            conn.execute(
                "INSERT INTO document_chunks (document_id, idx, text, embedding_blob) VALUES (?,?,?,?)",
                (doc_id, i, ch, json.dumps(vec)),
            )
    conn.commit()
    return doc_id


def list_documents(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT id, filename, mime, status FROM documents ORDER BY id").fetchall()]


def delete_document(conn: sqlite3.Connection, doc_id: int) -> None:
    conn.execute("DELETE FROM document_chunks WHERE document_id=?", (doc_id,))
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
