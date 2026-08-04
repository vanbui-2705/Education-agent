"""Vòng lặp agent (Phân hệ A, Chặng 2–3).

Luồng: system prompt + history + tools -> gọi LLM.
- Nếu LLM trả text -> kết thúc, trả text.
- Nếu LLM gọi công cụ ĐỌC -> chạy thật, bỏ kết quả vào history, lặp tiếp.
- Nếu LLM gọi công cụ GHI -> KHÔNG chạy, mà tạo id duyệt, trả bản xem trước, dừng.
Giới hạn 25 vòng chặn lặp vô tận. Mọi lỗi công cụ trả thông báo, agent tự thử cách khác.
"""

from __future__ import annotations

import json
import sqlite3

from core.config import THU_MIN, THU_MAX, CA_MIN, CA_MAX
from core.llm import build_llm
from scheduler.agent.prompts import system_prompt
from scheduler.agent.registry import tool_schemas, run_read_tool
from scheduler.agent.store import store

MAX_ROUNDS = 25
WRITE_NAMES = {"tao_buoi_hoc", "huy_buoi_hoc", "xep_lich"}


def _fmt(tool_result: list[dict]) -> str:
    if not tool_result:
        return "KET QUA: (khong co du lieu)"
    return "KET QUA: " + str(tool_result)


def run(user_message: str, conn: sqlite3.Connection) -> dict:
    llm = build_llm()
    messages: list[dict] = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_message},
    ]
    for _ in range(MAX_ROUNDS):
        try:
            out = llm.chat(messages, tools=tool_schemas())
        except Exception as e:  # noqa: BLE001
            # Loi goi LLM (thieu key, mang, rate-limit) -> tra thong bao sach, khong sap app.
            return {"done": True, "reply": f"Loi ket noi LLM: {e}", "approval_id": None}
        if out["type"] == "text":
            return {"done": True, "reply": out["content"], "approval_id": None}
        # tool call
        name = out["name"]
        args = out.get("args", {})
        tc_id = out.get("id") or f"call_{len(messages)}"
        if name in WRITE_NAMES:
            aid = store.put(messages, name, args)
            preview = _preview_write(name, args)
            return {
                "done": False,
                "reply": "Can ban duyet hanh dong ghi.",
                "approval_id": aid,
                "preview": preview,
            }
        # read tool
        try:
            result = run_read_tool(name, conn, args)
            # Backend native (OpenAI/Nous): format tool_calls chuan.
            # Backend prompt-based (Gemini): append ket qua duoi dang user message.
            if getattr(llm, "native_tools", True):
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tc_id,
                                "type": "function",
                                "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)},
                            }
                        ],
                    }
                )
                messages.append(
                    {"role": "tool", "tool_call_id": tc_id, "content": _fmt(result)}
                )
            else:
                messages.append(
                    {"role": "user", "content": f"[Ket qua tu {name}] {_fmt(result)}"}
                )
        except Exception as e:  # noqa: BLE001
            if getattr(llm, "native_tools", True):
                messages.append(
                    {"role": "tool", "tool_call_id": tc_id, "content": f"LOI cong cu: {e}"}
                )
            else:
                messages.append(
                    {"role": "user", "content": f"[Loi cong cu {name}] {e}"}
                )
    return {"done": True, "reply": "Da vuot qua so vong toi da, dung tai day.", "approval_id": None}


def _preview_write(name: str, args: dict) -> str:
    if name == "tao_buoi_hoc":
        return (
            f"[Xem truoc] TAO BUOI HOC\n"
            f"  Lop   : {args.get('ma_lop')}\n"
            f"  GV    : {args.get('ma_gv')}\n"
            f"  Phong : {args.get('ma_phong')}\n"
            f"  Thu   : {args.get('thu')} (2..8, 8=CN)\n"
            f"  Ca    : {args.get('ca')} (1..4)"
        )
    if name == "huy_buoi_hoc":
        return f"[Xem truoc] HUN BUOI HOC id={args.get('id')}"
    if name == "xep_lich":
        return "[Xem truoc] XEP LICH TU DONG cho cac lop chua co lich"
    return f"[Xem truoc] {name}: {args}"
