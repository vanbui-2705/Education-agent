"""Xep lich tu dong (Chang 4) — greedy fallback, khong can OR-Tools.

Muc tieu: voi cac lop CHUA co lich, tim (gv, phong, thu, ca) thoa man:
- gv ranh tai (thu,ca) do (chua co buoi nao trung UNIQUE(ma_gv,thu,ca))
- phong trong tai (thu,ca) do
- (tuy chon) lop chua co buoi trung (thu,ca)

Khong can OR-Tools de chay offline. Neu co ortools se dung CP-SAT tot hon,
nhung greedy van dam bao khong vi pham 2 UNIQUE (vi ta kiem tra truoc khi them).

Tra ve danh sach cac buoi da xep (chua ghi DB — goi qua ghi_lich.tao_buoi_hoc).
"""

from __future__ import annotations

import sqlite3
from typing import Any

from core.config import THU_MIN, THU_MAX, CA_MIN, CA_MAX
from scheduler.tools import doc_lich as doc


def _da_co(conn: sqlite3.Connection, ma_lop: str, thu: int, ca: int) -> bool:
    r = conn.execute(
        "SELECT 1 FROM buoi_hoc WHERE ma_lop=? AND thu=? AND ca=? LIMIT 1",
        (ma_lop, thu, ca),
    ).fetchone()
    return r is not None


def _trung_lop(conn: sqlite3.Connection, ma_lop: str, thu: int, ca: int) -> bool:
    # cung lop khong nen hoc 2 buoi trung thu+ca
    r = conn.execute(
        "SELECT 1 FROM buoi_hoc WHERE ma_lop=? AND thu=? AND ca=? LIMIT 1",
        (ma_lop, thu, ca),
    ).fetchone()
    return r is not None


def xep_lich(conn: sqlite3.Connection) -> list[dict]:
    """Xep lich cho moi lop chua du lich. Tra ve cac phuong an (chua ghi DB)."""
    plan: list[dict] = []
    lops = conn.execute("SELECT ma_lop FROM lop ORDER BY ma_lop").fetchall()
    for l in lops:
        ma_lop = l["ma_lop"]
        # Bo qua lop da co it nhat 1 buoi
        if conn.execute("SELECT 1 FROM buoi_hoc WHERE ma_lop=? LIMIT 1", (ma_lop,)).fetchone():
            continue
        # Tim mot slot thoa man
        found = None
        for thu in range(THU_MIN, THU_MAX + 1):
            for ca in range(CA_MIN, CA_MAX + 1):
                if _trung_lop(conn, ma_lop, thu, ca):
                    continue
                gv_ranh = doc.giao_vien_ranh(conn, thu, ca)
                phong_trong = doc.phong_trong(conn, thu, ca)
                if not gv_ranh or not phong_trong:
                    continue
                # Chon GV va phong dau tien
                ma_gv = gv_ranh[0]["ma_gv"]
                ma_phong = phong_trong[0]["ma_phong"]
                found = {"ma_lop": ma_lop, "ma_gv": ma_gv,
                         "ma_phong": ma_phong, "thu": thu, "ca": ca}
                break
            if found:
                break
        if found:
            plan.append(found)
        else:
            plan.append({"ma_lop": ma_lop, "msg": "khong tim duoc slot phu hop"})
    return plan


def xep_lich_va_ghi(conn: sqlite3.Connection) -> dict:
    """Xep lich roi ghi that vao DB qua ghi_lich (co audit_log). Tra ve tom tat."""
    from scheduler.tools import ghi_lich as ghi

    plan = xep_lich(conn)
    ok = 0
    fail = 0
    for p in plan:
        if "msg" in p:
            fail += 1
            continue
        res = ghi.tao_buoi_hoc(conn, p["ma_lop"], p["ma_gv"], p["ma_phong"], p["thu"], p["ca"])
        if res["ok"]:
            ok += 1
        else:
            fail += 1
    return {"da_xep": ok, "that_bai": fail, "chi_tiet": plan}
