"""Nhoms cong cu DOC lich (Chang 1).

Quy tac chung (theo spec):
- Moi cong cu nhan `conn` (ket noi db) lam tham so dau tien.
- Tra ve luon la list[dict].
- Khong tim thay thi tra danh sach rong, khong nem loi.
- Chi nem ValueError khi *tham so* sai.
"""

from __future__ import annotations

import sqlite3

from core.config import THU_MIN, THU_MAX, CA_MIN, CA_MAX
from scheduler.tools.text_utils import bo_dau


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    cur = conn.execute(sql, params)
    return [dict(r) for r in cur.fetchall()]


def tra_lich_giao_vien(conn: sqlite3.Connection, ma_gv: str | None = None, ten: str | None = None) -> list[dict]:
    if ma_gv:
        return _rows(conn, "SELECT * FROM buoi_hoc WHERE ma_gv=?", (ma_gv,))
    if ten:
        gvs = _rows(conn, "SELECT ma_gv FROM giao_vien WHERE ten LIKE ?", (f"%{ten}%",))
        out: list[dict] = []
        for g in gvs:
            out += _rows(conn, "SELECT * FROM buoi_hoc WHERE ma_gv=?", (g["ma_gv"],))
        return out
    raise ValueError("phai truyen ma_gv hoac ten")


def tra_lich_phong(conn: sqlite3.Connection, ma_phong: str) -> list[dict]:
    return _rows(conn, "SELECT * FROM buoi_hoc WHERE ma_phong=?", (ma_phong,))


def tra_lich_lop(conn: sqlite3.Connection, ma_lop: str | None = None, ten_lop: str | None = None) -> list[dict]:
    if ma_lop:
        return _rows(conn, "SELECT * FROM buoi_hoc WHERE ma_lop=?", (ma_lop,))
    if ten_lop:
        lops = _rows(conn, "SELECT ma_lop FROM lop WHERE ten_lop LIKE ?", (f"%{ten_lop}%",))
        out: list[dict] = []
        for l in lops:
            out += _rows(conn, "SELECT * FROM buoi_hoc WHERE ma_lop=?", (l["ma_lop"],))
        return out
    raise ValueError("phai truyen ma_lop hoac ten_lop")


def phong_trong(conn: sqlite3.Connection, thu: int, ca: int) -> list[dict]:
    if not (THU_MIN <= thu <= THU_MAX):
        raise ValueError(f"thu phai nam trong {THU_MIN}..{THU_MAX}")
    if not (CA_MIN <= ca <= CA_MAX):
        raise ValueError(f"ca phai nam trong {CA_MIN}..{CA_MAX}")
    sql = """
        SELECT * FROM phong
        WHERE ma_phong NOT IN (
            SELECT ma_phong FROM buoi_hoc WHERE thu=? AND ca=?
        )
        ORDER BY ma_phong
    """
    return _rows(conn, sql, (thu, ca))


def giao_vien_ranh(conn: sqlite3.Connection, thu: int, ca: int) -> list[dict]:
    if not (THU_MIN <= thu <= THU_MAX):
        raise ValueError(f"thu phai nam trong {THU_MIN}..{THU_MAX}")
    if not (CA_MIN <= ca <= CA_MAX):
        raise ValueError(f"ca phai nam trong {CA_MIN}..{CA_MAX}")
    sql = """
        SELECT * FROM giao_vien
        WHERE ma_gv NOT IN (
            SELECT ma_gv FROM buoi_hoc WHERE thu=? AND ca=?
        )
        ORDER BY ma_gv
    """
    return _rows(conn, sql, (thu, ca))


def tim_giao_vien(conn: sqlite3.Connection, chuoi: str) -> list[dict]:
    if not chuoi:
        return []
    key = bo_dau(chuoi)
    gvs = _rows(conn, "SELECT ma_gv, ten FROM giao_vien")
    return [dict(g) for g in gvs if key in bo_dau(g["ten"])]
