"""Test nap CSV mau (Chang 1)."""

from __future__ import annotations

from scheduler.ingest.from_csv import nap_tat_ca


def test_nap_csv_day_du(sample_db) -> None:
    # Nap lai de kiem tra so dong (nap lai khong loi vi INSERT OR IGNORE)
    ket_qua = nap_tat_ca(sample_db)
    assert ket_qua["giao_vien"] == 3
    assert ket_qua["phong"] == 3
    assert ket_qua["lop"] == 3
    assert ket_qua["buoi_hoc"] == 4
    # kiem tra that su co du lieu
    n = sample_db.execute("SELECT COUNT(*) AS c FROM buoi_hoc").fetchone()["c"]
    assert n == 4
