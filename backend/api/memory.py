"""Router ho so hoc sinh (Phan he B, memory)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from db.connection import get_conn
from memory.store import init_memory, get_profile, put_profile

router = APIRouter(prefix="/api/memory", tags=["memory"])


class ProfileReq(BaseModel):
    profile: dict


class ProfileResp(BaseModel):
    profile: dict


@router.get("/{user_id}", response_model=ProfileResp)
def get(user_id: str) -> ProfileResp:
    conn = get_conn()
    try:
        init_memory(conn)
        return ProfileResp(profile=get_profile(conn, user_id))
    finally:
        conn.close()


@router.put("/{user_id}", response_model=ProfileResp)
def put(user_id: str, req: ProfileReq) -> ProfileResp:
    conn = get_conn()
    try:
        init_memory(conn)
        put_profile(conn, user_id, req.profile)
        return ProfileResp(profile=get_profile(conn, user_id))
    finally:
        conn.close()
