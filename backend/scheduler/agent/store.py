"""Kho lưu tạm các yêu cầu ghi chờ người duyệt (trong RAM).

Mỗi yêu cầu được gán một id. API /approve đọc lại để thực thi.
Lưu ý: không bền vững qua khởi động lại — đủ cho MVP; sau này có thể đổi sang Redis/DB.
"""

from __future__ import annotations

import uuid
from typing import Any


class ApprovalStore:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}

    def put(self, messages: list[dict], tool: str, args: dict) -> str:
        aid = uuid.uuid4().hex[:12]
        self._items[aid] = {"messages": messages, "tool": tool, "args": args}
        return aid

    def get(self, aid: str) -> dict | None:
        return self._items.get(aid)

    def pop(self, aid: str) -> None:
        self._items.pop(aid, None)


store = ApprovalStore()
