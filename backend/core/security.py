"""Xác thực đơn giản bằng API key (header X-API-Key).

Dùng cho các router nhạy cảm ở các phase sau. Phase 0 chưa gắn vào /health.
"""

from __future__ import annotations

from fastapi import Header, HTTPException

from core.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not settings.app_secret:
        return ""
    if x_api_key != settings.app_secret:
        raise HTTPException(status_code=401, detail="Thieu hoac sai API key")
    return x_api_key
