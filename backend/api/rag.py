"""Router RAG query (Phan he B). Hoi dap co tai lieu."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from documents.service import init_docs
from rag.service import rag_query

router = APIRouter(prefix="/api/rag", tags=["rag"])


class RagReq(BaseModel):
    question: str
    k: int = 3


class RagResp(BaseModel):
    contexts: list[str]
    sources: list[str]


@router.post("/query", response_model=RagResp)
def query(req: RagReq) -> RagResp:
    conn = get_conn()
    try:
        init_docs(conn)
        res = rag_query(conn, req.question, req.k)
    finally:
        conn.close()
    return RagResp(**res)
