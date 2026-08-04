"""Phan he B - Dich vu hoi thoai tren kho tri thuc trung tam (RAG).

Build prompt co context tu rag_query + ho so hoc sinh, goi LLM.
Neu khong co key, tra thong bao sach.
(Mien phi test: hy3:free qua Nous; sau nay nang cap model khong doi code.)
"""

from __future__ import annotations

import sqlite3

from core.llm import build_llm
from rag.service import rag_query
from memory.store import get_profile


def tutor_answer(conn: sqlite3.Connection, user_id: str, question: str) -> dict:
    rag = rag_query(conn, question, k=3)
    contexts = rag["contexts"]
    ctx_text = "\n---\n".join(contexts) if contexts else "(chua co tai lieu nao duoc nap)"

    # Ho so hoc sinh (Schema B) de ca nhan hoa cau tra loi
    profile = get_profile(conn, user_id)
    prof_text = ""
    if profile:
        prof_text = "HO SO HOC SINH (" + user_id + "):\n" + str(profile) + "\n\n"

    prompt = (
        "Ban la tro ly tu van cua trung tam day them. Tra loi bang tieng Viet, than thien, "
        "chi dung thong tin tu KHO TRI THUC va HO SO duoi day, KHONG tu sinh.\n\n"
        + prof_text +
        "KHO TRI THUC TRUNG TAM:\n" + ctx_text + "\n\n"
        "CAU HOI: " + question
    )
    try:
        llm = build_llm()
        out = llm.chat([{"role": "user", "content": prompt}])
        answer = out.get("content", "") if out["type"] == "text" else ""
    except Exception as e:  # noqa: BLE001
        answer = f"(can key LLM de tra loi that) Loi ket noi LLM: {e}"
    return {"answer": answer, "sources": rag["sources"], "contexts": contexts,
            "profile": profile}
