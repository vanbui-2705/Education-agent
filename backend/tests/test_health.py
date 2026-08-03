"""Test health endpoint (Phase 0) — offline, khong can API key."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_health() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
