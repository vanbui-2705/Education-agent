"""Router tai lieu hoc (Phan he B). Upload text/md -> chunk -> embed -> luu."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.connection import get_conn
from documents.service import init_docs, add_document, list_documents, delete_document

router = APIRouter(prefix="/api/documents", tags=["documents"])


class UploadReq(BaseModel):
    filename: str
    text: str
    mime: str = "text/plain"


class DocItem(BaseModel):
    id: int
    filename: str
    mime: str
    status: str


@router.post("", response_model=DocItem)
def upload(req: UploadReq) -> DocItem:
    conn = get_conn()
    try:
        init_docs(conn)
        did = add_document(conn, req.filename, req.text, req.mime)
        row = conn.execute(
            "SELECT id, filename, mime, status FROM documents WHERE id=?", (did,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(status_code=500, detail="luu that bai")
    return DocItem(**dict(row))


@router.get("", response_model=list[DocItem])
def list_docs() -> list[DocItem]:
    conn = get_conn()
    try:
        init_docs(conn)
        return [DocItem(**dict(r)) for r in list_documents(conn)]
    finally:
        conn.close()


@router.delete("/{doc_id}")
def delete(doc_id: int) -> dict:
    conn = get_conn()
    try:
        delete_document(conn, doc_id)
    finally:
        conn.close()
    return {"ok": True}


@router.post("/nap-mau")
def nap_mau() -> dict:
    """Nap nhanh cac tai lieu mau (thong tin khoa hoc) vao Schema B de test RAG."""
    import json as _json
    from pathlib import Path
    from rag.chunking import chunk_text
    from rag.embedder import embed_texts
    from core.config import samples_dir

    conn = get_conn()
    try:
        init_docs(conn)
        src = samples_dir() / "tai_lieu"
        added = []
        if src.exists():
            for f in sorted(src.glob("*.txt")):
                text = f.read_text(encoding="utf-8")
                conn.execute(
                    "INSERT INTO documents (filename, mime, status) VALUES (?,?,?)",
                    (f.name, "text/plain", "ready"),
                )
                did = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                chunks = chunk_text(text)
                if chunks:
                    vecs = embed_texts(chunks)
                    for i, (ch, vec) in enumerate(zip(chunks, vecs)):
                        conn.execute(
                            "INSERT INTO document_chunks (document_id, idx, text, embedding_blob) VALUES (?,?,?,?)",
                            (did, i, ch, _json.dumps(vec)),
                        )
                added.append(f.name)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "added": added}
