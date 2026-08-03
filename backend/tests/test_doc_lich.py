"""Test 5 cong cu DOC lich (Chang 1)."""

from __future__ import annotations

import pytest

from scheduler.tools import doc_lich as d


def test_tra_lich_giao_vien_theo_ma(sample_db) -> None:
    rows = d.tra_lich_giao_vien(sample_db, ma_gv="GV01")
    assert len(rows) == 2
    assert all(r["ma_gv"] == "GV01" for r in rows)


def test_tra_lich_giao_vien_theo_ten(sample_db) -> None:
    rows = d.tra_lich_giao_vien(sample_db, ten="Lan")
    assert len(rows) == 2


def test_tra_lich_phong(sample_db) -> None:
    rows = d.tra_lich_phong(sample_db, "P301")
    assert len(rows) == 2


def test_tra_lich_lop(sample_db) -> None:
    rows = d.tra_lich_lop(sample_db, ten_lop="Toan")
    # T9A va T9B deu co 'Toan' trong ten_lop
    assert len(rows) == 3


def test_phong_trong(sample_db) -> None:
    # P302 va P303 chua ai dat vao thu 2 ca 1
    rows = d.phong_trong(sample_db, 2, 1)
    ma = {r["ma_phong"] for r in rows}
    assert "P302" in ma and "P303" in ma
    assert "P301" not in ma  # P301 da co T9A thu 2 ca 1


def test_giao_vien_ranh(sample_db) -> None:
    rows = d.giao_vien_ranh(sample_db, 3, 2)
    ma = {r["ma_gv"] for r in rows}
    assert "GV02" not in ma  # GV02 dang day thu 3 ca 2
    assert "GV01" in ma


def test_tim_giao_vien_khong_dau(sample_db) -> None:
    rows = d.tim_giao_vien(sample_db, "lan")
    assert any(r["ten"] == "Nguyen Thi Lan" for r in rows)


def test_phong_trong_tham_so_sai(sample_db) -> None:
    with pytest.raises(ValueError):
        d.phong_trong(sample_db, 1, 1)  # thu 1 nam ngoai 2..8
