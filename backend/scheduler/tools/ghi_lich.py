"""Cong cu GHI lich (Chang 3) + KIEM TRA XUNG DOT + HOAN TAC.

Tat ca ghi deu qua audit_log de hoan tac. Moi ham tra ve dict mo ta ket qua,
va ghi log vao audit_log.jsonl. Khong nem loi khi trung lich — tra thong bao tieng Viet.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from core.config import (
    THU_MIN, THU_MAX, CA_MIN, CA_MAX,
    audit_log_path,
)

# Log path co the bi ghi de o runtime (test dung de cach ly file tam).
_audit_log_override: Path | None = None


def set_audit_log_path(p: Path | None) -> None:
    """Test goi de tro log ra file tam, tranh anh huong data that / chia se giua test."""
    global _audit_log_override
    _audit_log_override = p


def _audit_path() -> Path:
    return _audit_log_override if _audit_log_override is not None else audit_log_path()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(action: str, payload: dict, row_id: int | None = None) -> None:
    """Ghi mot dong vao audit_log.jsonl (append)."""
    entry = {
        "ts": _now_iso(),
        "action": action,
        "payload": payload,
        "row_id": row_id,
    }
    p = _audit_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _check_bounds(thu: int, ca: int) -> None:
    if not (THU_MIN <= thu <= THU_MAX):
        raise ValueError(f"thu phai nam trong {THU_MIN}..{THU_MAX}")
    if not (CA_MIN <= ca <= CA_MAX):
        raise ValueError(f"ca phai nam trong {CA_MIN}..{CA_MAX}")


def tao_buoi_hoc(conn: sqlite3.Connection, ma_lop: str, ma_gv: str,
                 ma_phong: str, thu: int, ca: int) -> dict:
    _check_bounds(thu, ca)
    cur = conn.execute(
        "INSERT INTO buoi_hoc (ma_lop, ma_gv, ma_phong, thu, ca) VALUES (?,?,?,?,?)",
        (ma_lop, ma_gv, ma_phong, thu, ca),
    )
    conn.commit()
    row_id = cur.lastrowid
    _log("tao_buoi_hoc",
         {"ma_lop": ma_lop, "ma_gv": ma_gv, "ma_phong": ma_phong,
          "thu": thu, "ca": ca}, row_id)
    return {"ok": True, "id": row_id,
            "msg": f"Da tao buoi hoc id={row_id} ({ma_lop}, {ma_gv}, {ma_phong}, thu {thu} ca {ca})"}


def huy_buoi_hoc(conn: sqlite3.Connection, id: int) -> dict:
    row = conn.execute(
        "SELECT ma_lop, ma_gv, ma_phong, thu, ca FROM buoi_hoc WHERE id=?", (id,)
    ).fetchone()
    if row is None:
        return {"ok": False, "msg": f"Khong tim thay buoi hoc id={id}"}
    conn.execute("DELETE FROM buoi_hoc WHERE id=?", (id,))
    conn.commit()
    _log("huy_buoi_hoc",
         {"id": id, "ma_lop": row["ma_lop"], "ma_gv": row["ma_gv"],
          "ma_phong": row["ma_phong"], "thu": row["thu"], "ca": row["ca"]}, id)
    return {"ok": True, "msg": f"Da huy buoi hoc id={id}"}


def kiem_tra_xung_dot(conn: sqlite3.Connection) -> list[dict]:
    """Kiem tra cac vi pham UNIQUE: cung phong hoac cung GV trung thu+ca.
    Tra ve danh sach cac cap bi trung (neu co)."""
    bad: list[dict] = []
    # cung phong trung thu,ca
    for r in conn.execute("""
        SELECT a.id aid, b.id bid, a.ma_phong, a.thu, a.ca
        FROM buoi_hoc a JOIN buoi_hoc b
        ON a.ma_phong=b.ma_phong AND a.thu=b.thu AND a.ca=b.ca AND a.id<b.id
    """):
        bad.append({"loai": "trung_phong", "thu": r["thu"], "ca": r["ca"],
                    "ma_phong": r["ma_phong"], "ids": [r["aid"], r["bid"]]})
    # cung GV trung thu,ca
    for r in conn.execute("""
        SELECT a.id aid, b.id bid, a.ma_gv, a.thu, a.ca
        FROM buoi_hoc a JOIN buoi_hoc b
        ON a.ma_gv=b.ma_gv AND a.thu=b.thu AND a.ca=b.ca AND a.id<b.id
    """):
        bad.append({"loai": "trung_gv", "thu": r["thu"], "ca": r["ca"],
                    "ma_gv": r["ma_gv"], "ids": [r["aid"], r["bid"]]})
    return bad


def hoan_tac(conn: sqlite3.Connection, ts_tu: str | None = None) -> dict:
    """Hoan tac cac hanh dong ghi tu mot thoi diem tro lai (mac dinh: moi nhat).
    Doc nguoc audit_log, undo tao_buoi_hoc (DELETE) / huy_buoi_hoc (INSERT lai).
    Tra ve so luong da hoan tac."""
    p = _audit_path()
    if not p.exists():
        return {"ok": True, "undone": 0, "msg": "Khong co audit_log"}
    lines = p.read_text(encoding="utf-8").splitlines()
    done = 0
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        if ts_tu and e["ts"] < ts_tu:
            continue
        if e["action"] == "tao_buoi_hoc":
            rid = e["row_id"]
            conn.execute("DELETE FROM buoi_hoc WHERE id=?", (rid,))
            done += 1
        elif e["action"] == "huy_buoi_hoc":
            pl = e["payload"]
            conn.execute(
                "INSERT OR IGNORE INTO buoi_hoc (id, ma_lop, ma_gv, ma_phong, thu, ca) VALUES (?,?,?,?,?,?)",
                (pl["id"], pl["ma_lop"], pl["ma_gv"], pl["ma_phong"], pl["thu"], pl["ca"]),
            )
            done += 1
    conn.commit()
    return {"ok": True, "undone": done, "msg": f"Da hoan tac {done} hanh dong"}
