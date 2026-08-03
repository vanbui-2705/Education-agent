"""Phan he B - Dich vu hoi thoai gia su co RAG.

Build prompt co context tu rag_query, goi LLM. Neu khong co key, tra thong bao sach.
(Mien phi test: hy3:free qua Nous; sau nay nang cap model khong doi code.)
"""

from __future__ import annotations

import sqlite3

from core.llm import build_llm
from rag.service import rag_query


def tutor_answer(conn: sqlite3.Connection, user_id: str, question: str) -> dict:
    rag = rag_query(conn, question, k=3)
    contexts = rag["contexts"]
    ctx_text = "\n---\n".join(contexts) if contexts else "(khong co tai lieu)"
    prompt = (
        "Ban la gia su mon hoc cua trung tam day them. Tra loi hoc sinh bang tieng Viet, "
        "ngan gon, dung tai lieu duoi day.\n\nTAI LIEU:\n" + ctx_text +
        "\n\nHOI:" + question
    )
    try:
        llm = build_llm()
        out = llm.chat([{"role": "user", "content": prompt}])
        answer = out.get("content", "") if out["type"] == "text" else ""
    except Exception as e:  # noqa: BLE001
        answer = f"(can key LLM de tra loi that) Loi ket noi LLM: {e}"
    return {"answer": answer, "sources": rag["sources"], "contexts": contexts}
