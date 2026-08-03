"""Test cong cu GHI + xep lich + hoan tac (Phan he A, Chang 3-4) OFFLINE."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from scheduler.tools import doc_lich as doc
from scheduler.tools import ghi_lich as ghi
from scheduler.tools import xep_lich as xl


@pytest.fixture
def isolated_audit(sample_db):
    """Tach audit log ra file tam cho tung test, tranh chia se giua cac test."""
    fd, p = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    ghi.set_audit_log_path(Path(p))
    yield sample_db
    ghi.set_audit_log_path(None)
    os.remove(p)


def test_tao_buoi_hoc_va_audit(isolated_audit) -> None:
    res = ghi.tao_buoi_hoc(isolated_audit, "T9A", "GV01", "P301", 5, 2)
    assert res["ok"] is True
    n = isolated_audit.execute("SELECT COUNT(*) c FROM buoi_hoc").fetchone()["c"]
    assert n == 5  # 4 mau + 1 moi
    log = ghi._audit_path().read_text(encoding="utf-8").strip().splitlines()
    assert len(log) == 1
    assert "tao_buoi_hoc" in log[0]


def test_tao_trung_phong_bi_chan(sample_db) -> None:
    # P301 thu2 ca1 da co (T9A) -> them nua thi UNIQUE chan
    with pytest.raises(Exception):  # sqlite3.IntegrityError
        ghi.tao_buoi_hoc(sample_db, "T10B", "GV02", "P301", 2, 1)


def test_huy_buoi_hoc(isolated_audit) -> None:
    res = ghi.huy_buoi_hoc(isolated_audit, 1)
    assert res["ok"] is True
    n = isolated_audit.execute("SELECT COUNT(*) c FROM buoi_hoc").fetchone()["c"]
    assert n == 3


def test_kiem_tra_xung_dot_khong_co(isolated_audit) -> None:
    bad = ghi.kiem_tra_xung_dot(isolated_audit)
    assert bad == []  # mau dau khong trung


def test_xep_lich_tim_slot(isolated_audit) -> None:
    # Tat ca lop mau deu da co lich -> xep_lich tra ve rong
    plan = xl.xep_lich(isolated_audit)
    assert plan == []
    # Them mot lop chua co lich
    isolated_audit.execute("INSERT INTO lop VALUES ('T11C','Lop 11C','Ly',30)")
    isolated_audit.commit()
    plan = xl.xep_lich(isolated_audit)
    assert len(plan) == 1
    p = plan[0]
    assert p["ma_lop"] == "T11C"
    assert "ma_gv" in p and "ma_phong" in p and "thu" in p and "ca" in p
    gvs = {g["ma_gv"] for g in doc.giao_vien_ranh(isolated_audit, p["thu"], p["ca"])}
    phongs = {q["ma_phong"] for q in doc.phong_trong(isolated_audit, p["thu"], p["ca"])}
    assert p["ma_gv"] in gvs
    assert p["ma_phong"] in phongs


def test_hoan_tac_khoi_phuc(isolated_audit) -> None:
    res = ghi.tao_buoi_hoc(isolated_audit, "T9A", "GV01", "P301", 6, 3)
    rid = res["id"]
    assert isolated_audit.execute("SELECT 1 FROM buoi_hoc WHERE id=?", (rid,)).fetchone()
    undo = ghi.hoan_tac(isolated_audit)
    assert undo["undone"] == 1
    assert isolated_audit.execute("SELECT 1 FROM buoi_hoc WHERE id=?", (rid,)).fetchone() is None
