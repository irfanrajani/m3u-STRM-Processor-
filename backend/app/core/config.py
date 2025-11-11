"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import os
import json


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "IPTV Stream Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str  # REQUIRED - Must be set in .env for production
    ALLOWED_ORIGINS: Union[List[str], str] = '["http://localhost:3000","http://localhost:8000"]'
    
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

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # Redis
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Stream Health Check
    HEALTH_CHECK_TIMEOUT: int = 10
    HEALTH_CHECK_CONCURRENT: int = 50
    VERIFY_SSL: bool = False  # Many IPTV providers use self-signed certs

    # Output Directories
    OUTPUT_DIR: str = "/app/output"
    PLAYLISTS_DIR: str = "/app/output/playlists"
    VOD_DIR: str = "/app/output/vod"
    STRM_DIR: str = "/app/output/strm"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    # HDHomeRun Emulation
    HDHR_DEVICE_ID: str = "12345678"
    HDHR_FRIENDLY_NAME: str = "IPTV Stream Manager"
    HDHR_FIRMWARE_NAME: str = "hdhomerun_iptv"
    HDHR_FIRMWARE_VERSION: str = "1.0.0"
    HDHR_TUNER_COUNT: int = 6

    # Provider Settings
    MAX_PROVIDERS: int = 10
    SYNC_INTERVAL: int = 3600  # 1 hour in seconds

    # EPG Settings
    EPG_REFRESH_INTERVAL: int = 86400  # 24 hours in seconds
    EPG_DAYS: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
