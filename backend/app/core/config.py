"""
Application settings, loaded from environment variables / `.env`.

Override the defaults by creating `backend/.env` — see `.env.example`.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# _BASE_DIR = backend/  (this file is at backend/app/core/config.py)
_BASE_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BASE_DIR / ".env"


class Settings(BaseSettings):
    # PostgreSQL by default; override with your local DB URL in .env if needed.
    # Examples:
    #   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/aee_db
    #   DATABASE_URL=sqlite:///./aee.db
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/aee_db"

    # IMPORTANT: change this in production. A strong random value is recommended.
    SECRET_KEY: str = "change-this-in-production"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
