"""Phan he B - RAG query: tim doan lien quan nhat voi cau hoi, tra ve + trich dan nguon."""

from __future__ import annotations

import json
import sqlite3

from rag.embedder import embed_query
from rag.retriever import top_k


def rag_query(conn: sqlite3.Connection, question: str, k: int = 3) -> dict:
    """Tim top-k chunk gan nhat, tra ve cac doan + ten tai lieu nguon."""
    q_vec = embed_query(question)
    rows = conn.execute(
        "SELECT c.id, c.text, c.embedding_blob, d.filename "
        "FROM document_chunks c JOIN documents d ON d.id=c.document_id"
    ).fetchall()
    if not rows:
        return {"contexts": [], "sources": []}
    vecs = [json.loads(r["embedding_blob"]) for r in rows]
    idxs = top_k(q_vec, vecs, k)
    contexts = []
    sources = []
    for i in idxs:
        r = rows[i]
        contexts.append(r["text"])
        sources.append(r["filename"])
    return {"contexts": contexts, "sources": sources}
