"""Entry điểm chạy agent từ terminal (không cần web), dùng để test nhanh.

Chạy:  python -m scheduler.agent
Nhập câu hỏi tiếng Việt, Ctrl+C để thoát. Dùng DB thật data/trung_tam.db.
"""

from __future__ import annotations

from db.connection import get_conn
from scheduler.agent.loop import run


def main() -> None:
    conn = get_conn()
    print("Agent xep lich (go cau hoi, Ctrl+C thoat)")
    try:
        while True:
            q = input("\nBan: ").strip()
            if not q:
                continue
            res = run(q, conn)
            print("Agent:", res.get("reply"))
            if res.get("approval_id"):
                print(res.get("preview"))
                print("  (id duyet:", res["approval_id"], ")")
    except (KeyboardInterrupt, EOFError):
        print("\nThoat.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
