"""Điểm vào ứng dụng FastAPI.

Chạy:  uvicorn main:app --reload --port 8000
( từ thư mục gốc backend/ )
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.agent import router as agent_router
from api.approve import router as approve_router
from api.calendar import router as calendar_router
from api.chat import router as chat_router
from api.documents import router as documents_router
from api.health import router as health_router
from api.memory import router as memory_router
from api.rag import router as rag_router
from api.scheduler import router as scheduler_router
from core.exceptions import register_exception_handlers
from core.logging import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Education Agent Backend khoi dong")
    yield
    logger.info("Education Agent Backend dung")


app = FastAPI(title="Education Agent Backend", version="0.4.0", lifespan=lifespan)
register_exception_handlers(app)

# CORS: mo cho phep frontend local (dev). Tighten o prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(calendar_router)
app.include_router(agent_router)
app.include_router(approve_router)
app.include_router(scheduler_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(chat_router)
app.include_router(memory_router)
