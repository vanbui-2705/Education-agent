"""Lop truu tuong LLM da provider.

Mục đích: tầng agent chỉ gọi `chat(messages, tools)`, không quan tâm đằng sau là
Nous (hy3:free), OpenAI hay Gemini. Đổi provider = sửa `.env`, không sửa code agent.

- `OpenAIBackend`: dùng client OpenAI-compatible (mặc định cho hy3:free qua Nous).
- `build_llm()`: trả backend theo `settings.llm_provider`.
- `set_llm_override()`: dùng cho test (tiêm backend giả, không cần API key).
"""

from __future__ import annotations

import json
from typing import Any, Protocol, runtime_checkable

from openai import OpenAI

from core.config import settings


@runtime_checkable
class LLMBackend(Protocol):
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Trả về một trong hai:
        - {"type": "text", "content": str}
        - {"type": "tool_call", "name": str, "args": dict}
        """
        ...


class OpenAIBackend:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.model = model
        # Client vẫn khởi tạo được dù key rỗng; lỗi chỉ nảy sinh khi gọi API thật.
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
            return {"type": "tool_call", "name": tc.function.name, "args": args}
        return {"type": "text", "content": msg.content or ""}


_llm_override: LLMBackend | None = None


def set_llm_override(backend: LLMBackend | None) -> None:
    """Tiêm backend giả cho test (không cần gọi API thật)."""
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
        return OpenAIBackend(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model="gemini-2.0-flash",
        )
    raise ValueError(f"provider khong ho tro: {provider}")
