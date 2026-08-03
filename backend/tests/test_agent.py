"""Test agent loop + approval (Chang 2-3) OFFLINE.

Dung backend LLM gia (scripted) de khong can API key.
- Lan truong hop 1: LLM goi cong cu DOC -> agent tra ve text co du lieu that.
- Lan truong hop 2: LLM goi cong cu GHI -> agent tra ve approval_id + preview, KHONG ghi DB.
"""

from __future__ import annotations

import pytest

from core.llm import set_llm_override
from scheduler.agent.loop import run
from scheduler.agent.registry import tool_schemas


class _ScriptedLLM:
    """LLM gia: tra ve mot chuoi hanh dong dinh san theo thu tu."""

    def __init__(self, scripted: list[dict]) -> None:
        self._script = list(scripted)
        self._i = 0

    def chat(self, messages, tools=None):
        if self._i < len(self._script):
            out = self._script[self._i]
            self._i += 1
            return out
        return {"type": "text", "content": "xong"}


def test_agent_doc_flow(sample_db) -> None:
    # Buoc 1: LLM muon goi tra_lich_giao_vien(ten=Lan)
    # Buoc 2: LLM tra loi text tong hop
    script = [
        {"type": "tool_call", "name": "tra_lich_giao_vien", "args": {"ten": "Lan"}},
        {"type": "text", "content": "Co Lan day 2 buoi: T9A thu 2 ca 1 va thu 4 ca 1."},
    ]
    set_llm_override(_ScriptedLLM(script))
    res = run("Co Lan day nhung buoi nao?", sample_db)
    assert res["done"] is True
    assert res["approval_id"] is None
    assert "2 buoi" in res["reply"]


def test_agent_write_needs_approval(sample_db) -> None:
    script = [
        {"type": "tool_call", "name": "tao_buoi_hoc",
         "args": {"ma_lop": "T9A", "ma_gv": "GV01", "ma_phong": "P301", "thu": 5, "ca": 2}},
    ]
    set_llm_override(_ScriptedLLM(script))
    res = run("Xep lop T9A co Lan thu 5 ca 2 phong P301", sample_db)
    assert res["done"] is False
    assert res["approval_id"] is not None
    assert "TAO BUOI HOC" in res["preview"]
    # Quan trong: chua ghi that vao DB
    n = sample_db.execute("SELECT COUNT(*) AS c FROM buoi_hoc").fetchone()["c"]
    assert n == 4  # van la 4 buoi mau, chua them
