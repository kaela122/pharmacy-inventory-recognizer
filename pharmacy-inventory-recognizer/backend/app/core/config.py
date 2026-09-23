"""Application configuration, loaded from environment variables / .env."""
from __future__ import annotations
from functools import lru_cache
try:
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover
    from pydantic import BaseSettings  # type: ignore


class Settings(BaseSettings):
    app_name: str = "PharmaHub — Pharmacy Inventory & Code Recognizer"
    api_prefix: str = "/api"
    # SQLite by default => nothing to install. Point at Postgres in .env if you like.
    database_url: str = "sqlite:///./pharmahub.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
