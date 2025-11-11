from pathlib import Path
from pydantic import BaseSettings
import os
import secrets

def generate_secret_key():
    return secrets.token_urlsafe(32)

def ensure_env_file():
    env_file = Path("/app/data/.env")
    if env_file.exists():
        return
    db_user = os.getenv("POSTGRES_USER","iptv_user")
    db_pass = os.getenv("POSTGRES_PASSWORD","iptv_secure_pass_change_me")
    db_name = os.getenv("POSTGRES_DB","iptv_db")
    db_host = os.getenv("POSTGRES_HOST","db")
    db_port = os.getenv("POSTGRES_PORT","5432")
    database_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    env_content = f"""SECRET_KEY={generate_secret_key()}
DATABASE_URL={database_url}
REDIS_URL={os.getenv('REDIS_URL','redis://redis:6379/0')}
CELERY_BROKER_URL={os.getenv('CELERY_BROKER_URL','redis://redis:6379/0')}
CELERY_RESULT_BACKEND={os.getenv('CELERY_RESULT_BACKEND','redis://redis:6379/0')}
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3001","http://localhost:8000"]
BACKEND_PORT=8000
FRONTEND_PORT=3001
"""
    with open(env_file, "w") as f:
        f.write(env_content)

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql+asyncpg://iptv_user:iptv_secure_pass_change_me@db:5432/iptv_db")
    REDIS_URL: str = os.getenv("REDIS_URL","redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL","redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND","redis://redis:6379/0")
    DEBUG: bool = os.getenv("DEBUG", "false") == "true"
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "").split(",")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", 3001))

    class Config:
        env_file = "/app/data/.env"