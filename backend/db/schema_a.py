"""Schema A: du lieu trung tam (Phan he A - xep lich)."""

SCHEMA_A = """-- Schema A: du lieu trung tam day them (Phan he A - xep lich)
-- Quy uoc: thu 2..8 (8 = Chu nhat); ca 1..4.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS giao_vien (
    ma_gv   TEXT PRIMARY KEY,
    ten     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS phong (
    ma_phong   TEXT PRIMARY KEY,
    suc_chua   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS lop (
    ma_lop    TEXT PRIMARY KEY,
    ten_lop   TEXT NOT NULL,
    mon       TEXT NOT NULL,
    si_so     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS buoi_hoc (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_lop    TEXT NOT NULL,
    ma_gv     TEXT NOT NULL,
    ma_phong  TEXT NOT NULL,
    thu       INTEGER NOT NULL CHECK (thu BETWEEN 2 AND 8),
    ca        INTEGER NOT NULL CHECK (ca BETWEEN 1 AND 4),
    FOREIGN KEY (ma_lop)   REFERENCES lop(ma_lop),
    FOREIGN KEY (ma_gv)    REFERENCES giao_vien(ma_gv),
    FOREIGN KEY (ma_phong) REFERENCES phong(ma_phong),
    UNIQUE (ma_phong, thu, ca),
    UNIQUE (ma_gv, thu, ca)
);

-- Nhat ky ghi (audit) de hoan tac. Thuoc Schema A (trung tam).
CREATE TABLE IF NOT EXISTS audit_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT NOT NULL,
    hanh_dong TEXT NOT NULL,
    mo_ta     TEXT,
    thanh_cong INTEGER NOT NULL DEFAULT 1
);
"""
