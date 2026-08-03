"""Test cac router API (Phan he A) offline, khong can LLM that."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_health() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_calendar_phong_trong() -> None:
    client = TestClient(app)
    res = client.get("/api/calendar/phong-trong", params={"thu": 2, "ca": 1})
    assert res.status_code == 200
    ma = {r["ma_phong"] for r in res.json()}
    assert ma == {"P302", "P303"}


def test_approve_flow() -> None:
    # Duyet mot yeu cau gia da duoc tao san trong store -> thuc thi that + ghi DB
    from scheduler.agent.store import store
    from db.connection import get_conn

    aid = store.put([{"role": "user", "content": "x"}], "tao_buoi_hoc",
                    {"ma_lop": "T9A", "ma_gv": "GV01", "ma_phong": "P301", "thu": 5, "ca": 2})
    client = TestClient(app)
    res = client.post("/api/approve", json={"approval_id": aid})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "da_thuc_thi"
    assert body["tool"] == "tao_buoi_hoc"
    # DB thuc su co them 1 buoi
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) c FROM buoi_hoc WHERE thu=5 AND ca=2").fetchone()["c"]
    conn.close()
    assert n >= 1
    # Sau khi duyet, khoi hang doi bi xoa
    assert store.get(aid) is None


def test_approve_not_found() -> None:
    client = TestClient(app)
    res = client.post("/api/approve", json={"approval_id": "khongtontai"})
    assert res.status_code == 404
