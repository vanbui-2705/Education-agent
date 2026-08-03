"""Xac thuc don gian (Chang 5).

Mac dinh: kiem tra header X-API-Key khop voi APP_SECRET (tu .env).
Khi can JWT that, doi ham nay thanh verify token; cac router chi can them dependency.
"""

from __future__ import annotations

from fastapi import Header, HTTPException

from core.config import settings


def yeu_cau_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Dependency: bat buoc X-API-Key khop APP_SECRET. Tra ve key neu ok."""
    if not settings.app_secret:
        return "no-auth-dev"
    if x_api_key != settings.app_secret:
        raise HTTPException(status_code=401, detail="Sai API key")
    return x_api_key
