"""Đăng ký công cụ cho agent (Phân hệ A).

Mỗi công cụ có: tên, mô tả tiếng Việt cho LLM, chữ ký JSON schema, và hàm Python chạy thật.
Nhóm ĐỌC chạy ngay. Nhóm GHI không chạy ở đây — agent chỉ hẹn id duyệt qua store.
"""

from __future__ import annotations

import sqlite3

from scheduler.tools import doc_lich as doc

# Công cụ ĐỌC: (tên, mô tả, tham số schema, hàm)
READ_TOOLS: list[tuple] = [
    (
        "tra_lich_giao_vien",
        "Tra cac buoi day cua mot giao vien. Truyen ma_gv hoac ten.",
        {
            "type": "object",
            "properties": {
                "ma_gv": {"type": "string"},
                "ten": {"type": "string"},
            },
        },
        lambda conn, ma_gv=None, ten=None: doc.tra_lich_giao_vien(conn, ma_gv=ma_gv, ten=ten),
    ),
    (
        "tra_lich_phong",
        "Tra cac buoi da dat cua mot phong (truyen ma_phong).",
        {
            "type": "object",
            "properties": {"ma_phong": {"type": "string"}},
            "required": ["ma_phong"],
        },
        lambda conn, ma_phong: doc.tra_lich_phong(conn, ma_phong),
    ),
    (
        "tra_lich_lop",
        "Tra cac buoi cua mot lop. Truyen ma_lop hoac ten_lop.",
        {
            "type": "object",
            "properties": {"ma_lop": {"type": "string"}, "ten_lop": {"type": "string"}},
        },
        lambda conn, ma_lop=None, ten_lop=None: doc.tra_lich_lop(conn, ma_lop=ma_lop, ten_lop=ten_lop),
    ),
    (
        "phong_trong",
        "Tra danh sach phong chua ai dat vao mot thu va ca. thu 2..8 (8=CN), ca 1..4.",
        {
            "type": "object",
            "properties": {"thu": {"type": "integer"}, "ca": {"type": "integer"}},
            "required": ["thu", "ca"],
        },
        lambda conn, thu, ca: doc.phong_trong(conn, thu, ca),
    ),
    (
        "giao_vien_ranh",
        "Tra danh sach giao vien chua day vao mot thu va ca. thu 2..8, ca 1..4.",
        {
            "type": "object",
            "properties": {"thu": {"type": "integer"}, "ca": {"type": "integer"}},
            "required": ["thu", "ca"],
        },
        lambda conn, thu, ca: doc.giao_vien_ranh(conn, thu, ca),
    ),
    (
        "tim_giao_vien",
        "Tim giao vien theo ten gan dung (bo dau). Truyen chuoi.",
        {
            "type": "object",
            "properties": {"chuoi": {"type": "string"}},
            "required": ["chuoi"],
        },
        lambda conn, chuoi: doc.tim_giao_vien(conn, chuoi),
    ),
]

# Công cụ GHI (chờ duyệt): tên + mô tả + schema. Hàm thực thi nằm ở ghi_lich (Phase 3).
WRITE_TOOLS: list[tuple] = [
    (
        "tao_buoi_hoc",
        "Tao mot buoi hoc moi (lop, giao vien, phong, thu, ca). CAN DUYET.",
        {
            "type": "object",
            "properties": {
                "ma_lop": {"type": "string"},
                "ma_gv": {"type": "string"},
                "ma_phong": {"type": "string"},
                "thu": {"type": "integer"},
                "ca": {"type": "integer"},
            },
            "required": ["ma_lop", "ma_gv", "ma_phong", "thu", "ca"],
        },
    ),
    (
        "huy_buoi_hoc",
        "Huy mot buoi hoc theo id. CAN DUYET.",
        {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    ),
    (
        "xep_lich",
        "Xep lich tu dong cho cac lop chua co lich (chon gv ranh + phong trong). CAN DUYET.",
        {
            "type": "object",
            "properties": {},
        },
    ),
]


def tool_schemas() -> list[dict]:
    out = []
    for name, desc, schema, *_ in READ_TOOLS + WRITE_TOOLS:
        # Gemini OpenAI-compat yeu cau additionalProperties=False o cap root
        params = dict(schema)
        params.setdefault("additionalProperties", False)
        out.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": params,
                },
            }
        )
    return out


def run_read_tool(name: str, conn: sqlite3.Connection, args: dict) -> list[dict]:
    for tname, _desc, _schema, fn in READ_TOOLS:
        if tname == name:
            return fn(conn, **args)
    raise ValueError(f"cong cu doc khong ton tai: {name}")
