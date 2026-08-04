"""Cấu hình chung của backend.

Mọi đường dẫn và bí mật đọc từ đây / biến môi trường, không viết cứng vào code
nghiệp vụ (theo CLAUDE.md). Gốc dự án là thư mục chứa backend/ này.
"""

from __future__ import annotations

from pathlib import Path

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Gốc thư mục backend/ (file này nằm ở backend/core/config.py)
BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Load .env vao os.environ TRUOC khi Settings doc (fix parsing tren Windows)
load_dotenv(BACKEND_ROOT / ".env", override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM (đa provider) ---
    llm_provider: str = "openai"  # "openai" | "gemini" | "9router"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.nousresearch.com/v1"
    llm_model: str = "tencent/hy3:free"
    gemini_api_key: str = ""
    # 9Router (OpenAI-compatible gateway, local: http://localhost:20128/v1)
    ninrouter_base_url: str = "http://localhost:20128/v1"
    ninrouter_api_key: str = ""  # local free-tier thuong khong can
    ninrouter_model: str = "auto"  # "auto" hoac ten model tren 9router (vd gpt-4o, deepseek-chat)

    # --- Xác thực ---
    app_secret: str = "dev-secret-thay-doi"

    # --- Đường dẫn (ghi đè qua biến môi trường nếu cần) ---
    data_dir: Path = BACKEND_ROOT / "data"
    samples_dir: Path = BACKEND_ROOT / "samples"


settings = Settings()

# Force-read cac truong NINEROUTER_ tu os.environ (pydantic-settings tren Windows
# thuong bo qua mot so bien, nen ta lay truc tiep tu os.environ cho chac chan)
import os as _os
settings.ninrouter_base_url = _os.getenv("NINEROUTER_BASE_URL", settings.ninrouter_base_url)
settings.ninrouter_api_key = _os.getenv("NINEROUTER_API_KEY", settings.ninrouter_api_key) or ""
settings.ninrouter_model = _os.getenv("NINEROUTER_MODEL", settings.ninrouter_model)
settings.llm_provider = _os.getenv("LLM_PROVIDER", settings.llm_provider)
settings.gemini_api_key = _os.getenv("GEMINI_API_KEY", settings.gemini_api_key) or ""

# Quy ước ngày/thứ/ca — NGUỒN DUY NHẤT, đọc từ đây, không hardcode trong code.
# thu: 2..8 (8 = Chủ nhật). ca: 1..4.
THU_MIN: int = 2
THU_MAX: int = 8
CA_MIN: int = 1
CA_MAX: int = 4


def db_path() -> Path:
    return settings.data_dir / "trung_tam.db"


def schema_path() -> Path:
    return BACKEND_ROOT / "db" / "schema.sql"


def samples_dir() -> Path:
    return settings.samples_dir


def audit_log_path() -> Path:
    return settings.data_dir / "audit_log.jsonl"


def noi_quy_path() -> Path:
    return settings.data_dir / "noi_quy.md"
