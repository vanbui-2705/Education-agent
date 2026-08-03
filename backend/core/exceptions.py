"""Xử lý lỗi nghiệp vụ tập trung.

AppError mang thông báo tiếng Việt, được bắt ở đây trả về JSON cho client.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Lỗi nghiệp vụ, luôn có thông báo tiếng Việt cho người dùng."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
