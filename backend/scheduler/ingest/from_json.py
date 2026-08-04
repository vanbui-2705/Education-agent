"""Nap du lieu trung tam tu MOT file JSON duy nhat (de demo/chinh sua).

File mau: samples/trung_tam.json chua cac bang giao_vien, phong, lop, buoi_hoc, noi_quy.
Tat ca vao Schema A (cung 1 DB voi Schema B).

Chay:  python -m scheduler.ingest.from_json
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.config import samples_dir
from db.connection import get_conn
from db.init_db import tao_bang

SRC = samples_dir() / "trung_tam.json"


def nap_tat_ca(conn: sqlite3.Connection) -> dict:
    """Nap sach Schema A tu file JSON. Tra ve so dong da nap tung bang."""
    data = json.loads(SRC.read_text(encoding="utf-8"))
    cur = conn.cursor()
    # Xoa sach de nap lai (demo)
    for t in ("buoi_hoc", "lop", "phong", "giao_vien"):
        cur.execute(f"DELETE FROM {t}")
    counts = {}
    for gv in data.get("giao_vien", []):
        cur.execute("INSERT INTO giao_vien (ma_gv, ten) VALUES (?,?)",
                    (gv["ma_gv"], gv["ten"]))
    counts["giao_vien"] = len(data.get("giao_vien", []))
    for p in data.get("phong", []):
        cur.execute("INSERT INTO phong (ma_phong, suc_chua) VALUES (?,?)",
                    (p["ma_phong"], p["suc_chua"]))
    counts["phong"] = len(data.get("phong", []))
    for l in data.get("lop", []):
        cur.execute("INSERT INTO lop (ma_lop, ten_lop, mon, si_so) VALUES (?,?,?,?)",
                    (l["ma_lop"], l["ten_lop"], l["mon"], l["si_so"]))
    counts["lop"] = len(data.get("lop", []))
    for b in data.get("buoi_hoc", []):
        cur.execute(
            "INSERT INTO buoi_hoc (ma_lop, ma_gv, ma_phong, thu, ca) VALUES (?,?,?,?,?)",
            (b["ma_lop"], b["ma_gv"], b["ma_phong"], b["thu"], b["ca"]),
        )
    counts["buoi_hoc"] = len(data.get("buoi_hoc", []))
    # Noi quy -> ghi vao data/noi_quy.md
    nr = data.get("noi_quy", [])
    if nr:
        from core.config import noi_quy_path
        p = Path(noi_quy_path())
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join("- " + x for x in nr), encoding="utf-8")
    conn.commit()
    return counts


def main() -> None:
    conn = get_conn()
    tao_bang(conn)
    counts = nap_tat_ca(conn)
    conn.close()
    print("Da nap Schema A tu", SRC.name, "->", counts)


if __name__ == "__main__":
    main()
