"""Application configuration."""
from __future__ import annotations
import os
import json
import secrets
from pathlib import Path
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _gen_secret() -> str:
    return secrets.token_urlsafe(32)


def _ensure_env() -> None:
    env_file = Path("/app/data/.env")
    if env_file.exists():
        return
    
    db_user = os.getenv("POSTGRES_USER", "iptv_user")
    db_pass = os.getenv("POSTGRES_PASSWORD", "iptv_secure_pass_change_me")
    db_name = os.getenv("POSTGRES_DB", "iptv_db")
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    backend_port = os.getenv("BACKEND_PORT", "8000")
    database_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(f"""SECRET_KEY={_gen_secret()}
DATABASE_URL={database_url}
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:{backend_port}","http://127.0.0.1:{backend_port}","http://localhost:8000","http://localhost:3001"]
BACKEND_PORT={backend_port}
FRONTEND_PORT=3001
APP_NAME=IPTV Stream Manager
APP_VERSION=0.1.0
LOG_FILE=/app/data/logs/app.log
LOG_LEVEL=INFO
""")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="/app/data/.env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "IPTV Stream Manager"
    APP_VERSION: str = "0.1.0"
    LOG_FILE: str = "/app/data/logs/app.log"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://iptv_user:iptv_secure_pass_change_me@db:5432/iptv_db"
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    DEBUG: bool = False
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3001
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000","http://127.0.0.1:8000","http://localhost:3001"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            if v:
                return [x.strip() for x in v.split(",") if x.strip()]
        return ["http://localhost:8000","http://127.0.0.1:8000","http://localhost:3001"]


# ← THIS IS THE CRITICAL PART - EXPORT settings INSTANCE
_ensure_env()
settings = Settings()