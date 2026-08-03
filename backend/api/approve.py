"""Router duyet hanh dong ghi (human-in-the-loop, Phan he A, Chang 3-5).

POST /api/approve        {approval_id} -> thuc thi hanh dong ghi that, ghi audit_log
POST /api/approve/undo   {}            -> hoan tac toan bo hanh dong ghi gan nhat
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.connection import get_conn
from scheduler.agent.store import store
from scheduler.tools import ghi_lich as ghi
from scheduler.tools import xep_lich as xl

router = APIRouter(prefix="/api/approve", tags=["approve"])


class ApproveRequest(BaseModel):
    approval_id: str


class ApproveResponse(BaseModel):
    status: str
    tool: str | None = None
    result: dict | None = None


class UndoResponse(BaseModel):
    status: str
    undone: int = 0
    msg: str | None = None


@router.post("", response_model=ApproveResponse)
def approve(req: ApproveRequest) -> ApproveResponse:
    item = store.get(req.approval_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Khong tim thay yeu cau duyet")
    tool = item["tool"]
    args = item["args"]
    conn = get_conn()
    try:
        if tool == "tao_buoi_hoc":
            res = ghi.tao_buoi_hoc(conn, args["ma_lop"], args["ma_gv"],
                                  args["ma_phong"], args["thu"], args["ca"])
        elif tool == "huy_buoi_hoc":
            res = ghi.huy_buoi_hoc(conn, args["id"])
        elif tool == "xep_lich":
            res = xl.xep_lich_va_ghi(conn)
        else:
            raise HTTPException(status_code=400, detail=f"Khong ho tro: {tool}")
    finally:
        conn.close()
    store.pop(req.approval_id)
    return ApproveResponse(status="da_thuc_thi", tool=tool, result=res)


@router.post("/undo", response_model=UndoResponse)
def undo() -> UndoResponse:
    conn = get_conn()
    try:
        res = ghi.hoan_tac(conn)
    finally:
        conn.close()
    return UndoResponse(status="da_hoan_tac", undone=res.get("undone", 0), msg=res.get("msg"))
