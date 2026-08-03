"""Noi quy trung tam (Chang 5) — doc/noi quy.md, de xuat luat.

Noi quy la van ban tieng Viet nguoi quan ly tu sua (data/noi_quy.md).
Agent doc noi quy de tu van, va co the de xuat them luat moi (ghi them vao cuoi file).
"""

from __future__ import annotations

from pathlib import Path

from core.config import noi_quy_path


def doc_noi_quy() -> str:
    p = noi_quy_path()
    if not p.exists():
        return "(chua co noi quy)"
    return p.read_text(encoding="utf-8").strip()


def de_xuat_luat(conn, noi_dung: str) -> dict:
    """Them mot dong noi quy moi vao cuoi file. Tra ve trang thai."""
    p = noi_quy_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write("\n- " + noi_dung.strip() + "\n")
    return {"ok": True, "msg": f"Da them noi quy: {noi_dung}"}
