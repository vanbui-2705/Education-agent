"""Cấu hình chung của backend.

Mọi đường dẫn và bí mật đọc từ đây / biến môi trường, không viết cứng vào code
nghiệp vụ (theo CLAUDE.md). Gốc dự án là thư mục chứa backend/ này.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Gốc thư mục backend/ (file này nằm ở backend/core/config.py)
BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM (đa provider) ---
    llm_provider: str = "openai"  # "openai" | "gemini"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.nousresearch.com/v1"
    llm_model: str = "tencent/hy3:free"
    gemini_api_key: str = ""

    # --- Xác thực ---
    app_secret: str = "dev-secret-thay-doi"

    # --- Đường dẫn (ghi đè qua biến môi trường nếu cần) ---
    data_dir: Path = BACKEND_ROOT / "data"
    samples_dir: Path = BACKEND_ROOT / "samples"


settings = Settings()

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
