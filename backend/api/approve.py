"""Router duyet hanh dong ghi (human-in-the-loop, Phan he A, Chang 3)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from scheduler.agent.store import store

router = APIRouter(prefix="/api/approve", tags=["approve"])


class ApproveRequest(BaseModel):
    approval_id: str


class ApproveResponse(BaseModel):
    status: str
    tool: str | None = None
    preview: str | None = None


@router.post("", response_model=ApproveResponse)
def approve(req: ApproveRequest) -> ApproveResponse:
    item = store.get(req.approval_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Khong tim thay yeu cau duyet")
    # Phan he A Chang 3 chua thuc thi ghi that; chi tra ban xem truoc va xoa khoi hang doi.
    tool = item["tool"]
    preview = f"{tool}: {item['args']}"
    store.pop(req.approval_id)
    return ApproveResponse(status="da_duyet_cho_xem_truoc", tool=tool, preview=preview)
