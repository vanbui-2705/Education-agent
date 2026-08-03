"""Router tra cuu lich truc tiep (Phan he A, Chang 1) — khong can LLM."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from scheduler.tools import doc_lich as doc

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class Slot(BaseModel):
    thu: int
    ca: int


@router.get("/phong-trong")
def phong_trong(thu: int, ca: int) -> list[dict]:
    conn = get_conn()
    try:
        return doc.phong_trong(conn, thu, ca)
    finally:
        conn.close()


@router.get("/giao-vien-ranh")
def giao_vien_ranh(thu: int, ca: int) -> list[dict]:
    conn = get_conn()
    try:
        return doc.giao_vien_ranh(conn, thu, ca)
    finally:
        conn.close()


@router.get("/giao-vien/{ma_gv}")
def lich_giao_vien(ma_gv: str) -> list[dict]:
    conn = get_conn()
    try:
        return doc.tra_lich_giao_vien(conn, ma_gv=ma_gv)
    finally:
        conn.close()
