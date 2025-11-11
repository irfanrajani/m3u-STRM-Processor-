"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import os
import json
import secrets
from pathlib import Path


def generate_secret_key() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)


def ensure_env_file():
    """Create .env file with secure defaults if it doesn't exist."""
    env_file = Path("/app/data/.env")
    
    if not env_file.exists():
        # Generate secure defaults
        secret_key = generate_secret_key()
        
        env_content = f"""# Auto-generated configuration
# You can modify these values through the web interface at http://localhost:3001/settings

# Security
SECRET_KEY={secret_key}

# Database (auto-configured for Docker)
DATABASE_URL=postgresql+asyncpg://iptv_user:iptv_secure_pass_change_me@db:5432/iptv_db

# Redis (auto-configured for Docker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3001","http://localhost:8000"]

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3001
"""
        
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(env_content)
        print(f"✅ Auto-generated secure configuration at {env_file}")


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "IPTV Stream Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = generate_secret_key()
    ALLOWED_ORIGINS: Union[List[str], str] = '["http://localhost:3001","http://localhost:8000"]'
    
    # Ports
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3001
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string or list."""
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    # Database - auto-configured for Docker
    DATABASE_URL: str = "postgresql+asyncpg://iptv_user:iptv_secure_pass_change_me@db:5432/iptv_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # Redis - auto-configured for Docker
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Stream Health Check
    HEALTH_CHECK_TIMEOUT: int = 10
    HEALTH_CHECK_CONCURRENT: int = 50
    VERIFY_SSL: bool = False  # Many IPTV providers use self-signed certs

    # Output Directories
    OUTPUT_DIR: str = "/app/output"
    PLAYLISTS_DIR: str = "/app/output/playlists"
    VOD_DIR: str = "/app/output/vod"
    STRM_DIR: str = "/app/output/strm"
    EPG_DIR: str = "/app/output/epg"  # Add missing EPG_DIR

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    # HDHomeRun Emulation
    HDHR_DEVICE_ID: str = "12345678"
    HDHR_FRIENDLY_NAME: str = "IPTV Stream Manager"
    HDHR_FIRMWARE_NAME: str = "hdhomerun_iptv"
    HDHR_FIRMWARE_VERSION: str = "1.0.0"
    HDHR_TUNER_COUNT: int = 6
    HDHR_PROXY_MODE: str = "direct"  # Add missing HDHR_PROXY_MODE

    # Provider Settings
    MAX_PROVIDERS: int = 10
    SYNC_INTERVAL: int = 3600  # 1 hour in seconds

    # EPG Settings
    EPG_REFRESH_INTERVAL: int = 86400  # 24 hours in seconds
    EPG_DAYS: int = 7

    class Config:
        env_file = "/app/data/.env"
        case_sensitive = False


# Ensure .env exists with secure defaults
ensure_env_file()

settings = Settings()
