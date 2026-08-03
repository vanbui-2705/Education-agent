"""Test tao bang va rang buoc UNIQUE / khoa ngoai (Chang 1)."""

from __future__ import annotations

import pytest
import sqlite3

from core.config import THU_MIN, THU_MAX, CA_MIN, CA_MAX


def test_tao_du_bon_bang(temp_db: sqlite3.Connection) -> None:
    tables = [r["name"] for r in temp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    for t in ("giao_vien", "phong", "lop", "buoi_hoc"):
        assert t in tables, f"thieu bang {t}"


def test_khoa_ngoai_duoc_bat(temp_db: sqlite3.Connection) -> None:
    row = temp_db.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1, "khoa ngoai chua bat"


def test_chan_hai_lop_cung_phong_cung_gio(temp_db: sqlite3.Connection) -> None:
    # nap du lieu nen
    temp_db.execute("INSERT INTO lop VALUES ('L1','Lop 1','Toan',20)")
    temp_db.execute("INSERT INTO giao_vien VALUES ('G1','A')")
    temp_db.execute("INSERT INTO phong VALUES ('P1',30)")
    temp_db.execute("INSERT INTO buoi_hoc (ma_lop,ma_gv,ma_phong,thu,ca) VALUES ('L1','G1','P1',2,1)")
    temp_db.commit()
    # cung phong cung thu cung ca -> phai bi tu choi
    with pytest.raises(sqlite3.IntegrityError):
        temp_db.execute("INSERT INTO buoi_hoc (ma_lop,ma_gv,ma_phong,thu,ca) VALUES ('L2','G2','P1',2,1)")
        temp_db.commit()


def test_chan_giao_vien_day_hai_lop_cung_luc(temp_db: sqlite3.Connection) -> None:
    temp_db.execute("INSERT INTO lop VALUES ('L1','Lop 1','Toan',20)")
    temp_db.execute("INSERT INTO lop VALUES ('L2','Lop 2','Van',20)")
    temp_db.execute("INSERT INTO giao_vien VALUES ('G1','A')")
    temp_db.execute("INSERT INTO phong VALUES ('P1',30)")
    temp_db.execute("INSERT INTO phong VALUES ('P2',30)")
    temp_db.execute("INSERT INTO buoi_hoc (ma_lop,ma_gv,ma_phong,thu,ca) VALUES ('L1','G1','P1',2,1)")
    temp_db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        temp_db.execute("INSERT INTO buoi_hoc (ma_lop,ma_gv,ma_phong,thu,ca) VALUES ('L2','G1','P2',2,1)")
        temp_db.commit()


def test_khoa_ngoai_chan_ma_gv_khong_ton_tai(temp_db: sqlite3.Connection) -> None:
    temp_db.execute("INSERT INTO lop VALUES ('L1','Lop 1','Toan',20)")
    temp_db.execute("INSERT INTO phong VALUES ('P1',30)")
    with pytest.raises(sqlite3.IntegrityError):
        temp_db.execute("INSERT INTO buoi_hoc (ma_lop,ma_gv,ma_phong,thu,ca) VALUES ('L1','GX','P1',2,1)")
        temp_db.commit()


def test_khoang_hop_le_cua_thu_ca() -> None:
    assert THU_MIN == 2 and THU_MAX == 8
    assert CA_MIN == 1 and CA_MAX == 4
