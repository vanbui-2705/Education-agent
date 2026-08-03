"""Router truc tiep cho Phan he A: xep lich, kiem tra xung dot, hoan tac.

Khong can LLM. Dung de test nhanh va cho giao dien khac goi truc tiep.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from scheduler.tools import ghi_lich as ghi
from scheduler.tools import xep_lich as xl

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class XepLichResponse(BaseModel):
    da_xep: int
    that_bai: int
    chi_tiet: list[dict]


@router.post("/xep-lich", response_model=XepLichResponse)
def xep_lich() -> XepLichResponse:
    conn = get_conn()
    try:
        res = xl.xep_lich_va_ghi(conn)
    finally:
        conn.close()
    return XepLichResponse(**res)


@router.get("/xung-dot")
def xung_dot() -> list[dict]:
    conn = get_conn()
    try:
        return ghi.kiem_tra_xung_dot(conn)
    finally:
        conn.close()


class UndoResponse(BaseModel):
    ok: bool
    undone: int
    msg: str | None = None


@router.post("/hoan-tac", response_model=UndoResponse)
def hoan_tac() -> UndoResponse:
    conn = get_conn()
    try:
        res = ghi.hoan_tac(conn)
    finally:
        conn.close()
    return UndoResponse(**res)
