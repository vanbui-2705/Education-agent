"""Điểm vào ứng dụng FastAPI.

Chạy:  uvicorn main:app --reload --port 8000
( từ thư mục gốc backend/ )
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.agent import router as agent_router
from api.approve import router as approve_router
from api.calendar import router as calendar_router
from api.health import router as health_router
from core.exceptions import register_exception_handlers
from core.logging import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Education Agent Backend khoi dong")
    yield
    logger.info("Education Agent Backend dung")


app = FastAPI(title="Education Agent Backend", version="0.2.0", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(health_router)
app.include_router(calendar_router)
app.include_router(agent_router)
app.include_router(approve_router)
