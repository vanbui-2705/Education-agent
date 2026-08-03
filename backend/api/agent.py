"""Router agent xep lich (Phan he A, Chang 2-3).

POST /api/agent/chat  ->  { "reply", "approval_id"? , "preview"? }
- reply: cau tra loi tieng Viet hoac thong bao can duyet.
- approval_id: neu khac null, co hanh dong GHI dang cho duyet (xem /api/approve).
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from scheduler.agent.loop import run

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    approval_id: str | None = None
    preview: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    conn = get_conn()
    try:
        res = run(req.message, conn)
    finally:
        conn.close()
    return ChatResponse(
        reply=res.get("reply", ""),
        approval_id=res.get("approval_id"),
        preview=res.get("preview"),
    )
