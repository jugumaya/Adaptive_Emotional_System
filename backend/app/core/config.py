from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL by default; override with your local DB URL in .env if needed
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/aee_db"
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    ALGORITHM: str = "HS256"

    class Config:
        env_file = str(Path(__file__).resolve().parents[1] / ".env")


settings = Settings()
