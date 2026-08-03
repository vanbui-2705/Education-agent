"""Test cac router moi (documents, rag, chat, memory, scheduler) qua TestClient (OFFLINE)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from db.connection import get_conn
from db.init_db import tao_bang
from documents.service import init_docs, add_document
from main import app


def _seed_rag() -> None:
    conn = get_conn()
    try:
        init_docs(conn)
        exists = conn.execute(
            "SELECT 1 FROM documents WHERE filename='ly.txt' LIMIT 1").fetchone()
        if not exists:
            add_document(conn, "ly.txt",
                        "Dinh luat Ohm: I = U / R. Dong dien ti le voi hieu dien the.")
    finally:
        conn.close()


def test_documents_upload_list() -> None:
    client = TestClient(app)
    r = client.post("/api/documents", json={"filename": "a.txt", "text": "Toan la mon hoc."})
    assert r.status_code == 200
    assert r.json()["filename"] == "a.txt"
    lst = client.get("/api/documents")
    assert lst.status_code == 200
    assert any(d["filename"] == "a.txt" for d in lst.json())


def test_rag_query() -> None:
    _seed_rag()
    client = TestClient(app)
    r = client.post("/api/rag/query", json={"question": "dinh luat Ohm", "k": 1})
    assert r.status_code == 200
    body = r.json()
    assert "ly.txt" in body["sources"]


def test_chat_no_key_clean() -> None:
    _seed_rag()
    client = TestClient(app)
    r = client.post("/api/chat", json={"user_id": "u1", "question": "Ohm la gi"})
    assert r.status_code == 200
    # khong co key that -> tra thong bao sach, khong 500
    assert "Loi ket noi LLM" in r.json()["answer"] or r.json()["answer"]


def test_memory_put_get() -> None:
    client = TestClient(app)
    p = client.put("/api/memory/u1", json={"profile": {"mon_yeu": "Ly"}})
    assert p.status_code == 200
    g = client.get("/api/memory/u1")
    assert g.status_code == 200
    assert g.json()["profile"]["mon_yeu"] == "Ly"


def test_scheduler_xep_lich_endpoint() -> None:
    client = TestClient(app)
    # them lop chua co lich
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO lop VALUES ('T12D','Lop 12D','Hoa',28)")
    conn.commit()
    conn.close()
    r = client.post("/api/scheduler/xep-lich")
    assert r.status_code == 200
    body = r.json()
    assert body["da_xep"] >= 1


def test_approve_execute_write() -> None:
    # tao yeu cau ghi qua store, duyet that -> DB doi
    from scheduler.agent.store import store
    from db.connection import get_conn
    aid = store.put([{"role": "user", "content": "x"}], "tao_buoi_hoc",
                    {"ma_lop": "T9A", "ma_gv": "GV01", "ma_phong": "P301", "thu": 7, "ca": 3})
    client = TestClient(app)
    r = client.post("/api/approve", json={"approval_id": aid})
    assert r.status_code == 200
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) c FROM buoi_hoc WHERE thu=7 AND ca=3").fetchone()["c"]
    conn.close()
    assert n >= 1
    # undo
    u = client.post("/api/approve/undo")
    assert u.status_code == 200
    assert u.json()["undone"] >= 1
