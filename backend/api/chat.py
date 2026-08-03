"""Router hoi thoai gia su RAG (Phan he B)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from documents.service import init_docs
from chat.service import tutor_answer

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatReq(BaseModel):
    user_id: str = "anon"
    question: str


class ChatResp(BaseModel):
    answer: str
    sources: list[str]


@router.post("", response_model=ChatResp)
def chat(req: ChatReq) -> ChatResp:
    conn = get_conn()
    try:
        init_docs(conn)
        res = tutor_answer(conn, req.user_id, req.question)
    finally:
        conn.close()
    return ChatResp(answer=res["answer"], sources=res["sources"])
