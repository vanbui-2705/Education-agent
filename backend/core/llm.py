"""Lop truu tuong LLM da provider.

Muc dich: tang agent chi goi `chat(messages, tools)`, khong quan tam đang sau la
Nous (hy3:free), OpenAI hay Gemini. Đoi provider = sua `.env`, khong sua code agent.

- `OpenAIBackend`: client OpenAI-compatible (mac đinh cho hy3:free qua Nous).
  Ho tro native tool-calling (function calling chuan OpenAI).
- `GeminiBackend`: goi Gemini qua endpoint OpenAI-compatible. Vi ban bridge cua
  Gemini voi model thinking (gemini-flash-latest) bat buoc `thought_signature`
  khi dung native function calling ma client OpenAI khong sinh ra, nen o đay
  dung prompt-based tool routing: yeu cau model tra JSON {action, args}.
- `build_llm()`: tra backend theo `settings.llm_provider`.
- `set_llm_override()`: dung cho test (tiem backend gia, khong can API key).
"""

from __future__ import annotations

import json
import re
from typing import Any, Protocol, runtime_checkable

from openai import OpenAI

from core.config import settings


@runtime_checkable
class LLMBackend(Protocol):
    native_tools: bool  # True = ho tro function calling chuan OpenAI

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Tra ve mot trong hai:
        - {"type": "text", "content": str}
        - {"type": "tool_call", "id": str, "name": str, "args": dict}
        """
        ...


class OpenAIBackend:
    native_tools = True

    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        # Client van khoi tao đuoc dau key rong; loi chi nay sinh khi goi API that.
        self._client = OpenAI(api_key=api_key or "EMPTY", base_url=base_url)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        resp = self._client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        if msg.tool_calls:
            tc = msg.tool_calls[0]
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            return {
                "type": "tool_call",
                "id": tc.id,
                "name": tc.function.name,
                "args": args,
            }
        return {"type": "text", "content": msg.content or ""}


class GeminiBackend:
    """Backend Gemini dung prompt-based tool routing (khong native function call).

    Ly do: gemini-flash-latest (model free-tier duy nhat hoat đong voi key nay)
    la thinking model, bridge OpenAI-compatible bat buoc thought_signature o
    function_call ma OpenAI client khong sinh -> 400. Thay vao do, yeu cau model
    tra JSON {action, args} trong phan text.
    """

    native_tools = False

    def __init__(self, api_key: str, model: str):
        self.model = model
        self._client = OpenAI(
            api_key=api_key or "EMPTY",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    @staticmethod
    def _tool_instruction(tools: list[dict]) -> str:
        lines = []
        for t in tools:
            fn = t.get("function", {})
            name = fn.get("name", "")
            desc = fn.get("description", "")
            params = json.dumps(fn.get("parameters", {}), ensure_ascii=False)
            lines.append(f"- {name}: {desc} | params: {params}")
        return (
            "Ban la agent cua trung tam day them. Chi đuoc tra loi bang DUNG MOT "
            "khoi JSON (khong markdown, khong giai thich them ngoai JSON), co dang:\n"
            "  {\"action\": \"<ten_cong_cu>\", \"args\": {<tham_so>}}\n"
            "hoac neu khong can goi cong cu thi:\n"
            "  {\"action\": \"tra_loi\", \"args\": {\"text\": \"<cau tra loi tieng Viet>\"}}\n"
            "Danh sach cong cu:\n" + "\n".join(lines) + "\n"
            "Luu y: chi tra JSON, khong them text khac."
        )

    @staticmethod
    def _extract_json(content: str) -> dict | None:
        # Tim khoi {...} đau tien
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        if not tools:
            resp = self._client.chat.completions.create(model=self.model, messages=messages)
            return {"type": "text", "content": resp.choices[0].message.content or ""}
        # Neu history da co ket qua tool -> de model tra loi tu nhien (khong ep JSON)
        da_co_ket_qua = any(
            isinstance(m.get("content"), str) and m["content"].startswith("[Ket qua tu")
            for m in messages
        )
        if da_co_ket_qua:
            resp = self._client.chat.completions.create(model=self.model, messages=messages)
            return {"type": "text", "content": resp.choices[0].message.content or ""}
        sys_instr = self._tool_instruction(tools)
        # Gop instruction vao system message DAU (tranh 2 system role bi xung dot
        # o mot so model nhu Gemini).
        full = list(messages)
        if full and full[0].get("role") == "system":
            full[0] = {"role": "system", "content": sys_instr + "\n\n" + full[0]["content"]}
        else:
            full = [{"role": "system", "content": sys_instr}] + full
        resp = self._client.chat.completions.create(model=self.model, messages=full)
        content = resp.choices[0].message.content or ""
        data = self._extract_json(content)
        if data is None:
            # Model tra text thuong -> coi nhu tra loi
            return {"type": "text", "content": content}
        action = data.get("action")
        if action and action != "tra_loi":
            return {
                "type": "tool_call",
                "id": "call_gemini",
                "name": action,
                "args": data.get("args", {}),
            }
        return {"type": "text", "content": data.get("args", {}).get("text", content)}


_llm_override: LLMBackend | None = None


def set_llm_override(backend: LLMBackend | None) -> None:
    """Tiem backend gia cho test (khong can goi API that)."""
    global _llm_override
    _llm_override = backend


def build_llm(provider: str | None = None) -> LLMBackend:
    if _llm_override is not None:
        return _llm_override
    provider = provider or settings.llm_provider
    if provider in ("openai", "nous", "hy3"):
        return OpenAIBackend(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.llm_model,
        )
    if provider == "gemini":
        return GeminiBackend(
            api_key=settings.gemini_api_key,
            model="gemini-flash-latest",  # free-tier hoat đong voi key nay
        )
    raise ValueError(f"provider khong ho tro: {provider}")
