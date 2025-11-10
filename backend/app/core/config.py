"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "IPTV Stream Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Secret key - auto-generate and persist
    _SECRET_KEY_FILE: Path = Path("/app/data/secret.key")

    @property
    def SECRET_KEY(self) -> str:
        """Auto-generate and persist secret key."""
        # Try to load existing key
        if self._SECRET_KEY_FILE.exists():
            return self._SECRET_KEY_FILE.read_text().strip()

        # Generate new key and save it
        new_key = secrets.token_urlsafe(32)
        self._SECRET_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._SECRET_KEY_FILE.write_text(new_key)
        return new_key

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40

    # Redis
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Output Directories
    OUTPUT_DIR: str = "/app/output"
    PLAYLISTS_DIR: str = "/app/output/playlists"
    STRM_DIR: str = "/app/output/strm_files"
    EPG_DIR: str = "/app/output/epg"

    # Stream Health Check Settings
    DEFAULT_HEALTH_CHECK_TIMEOUT: int = 10
    DEFAULT_HEALTH_CHECK_SCHEDULE: str = "0 3 * * *"  # Daily at 3 AM
    MAX_CONCURRENT_HEALTH_CHECKS: int = 50
    VERIFY_SSL: bool = False  # Most IPTV streams don't have valid SSL

    # Channel Matching Settings
    DEFAULT_FUZZY_MATCH_THRESHOLD: int = 85
    ENABLE_LOGO_MATCHING: bool = True
    LOGO_MATCH_THRESHOLD: int = 90

    # Quality Detection
    ENABLE_BITRATE_ANALYSIS: bool = True
    FFPROBE_TIMEOUT: int = 15

    # Emby Integration
    EMBY_HOST: Optional[str] = None
    EMBY_API_KEY: Optional[str] = None
    EMBY_LIBRARY_REFRESH: bool = True

    # HDHomeRun Emulation
    HDHR_PROXY_MODE: str = "direct"  # 'direct' or 'proxy'
    HDHR_DEVICE_ID: str = "IPTV-MGR"
    HDHR_TUNER_COUNT: int = 4
    EXTERNAL_URL: Optional[str] = None  # External URL for HDHR discovery
    API_PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


# Ensure output directories exist (skip in CI/test environments)
try:
    for directory in [
        settings.OUTPUT_DIR,
        settings.PLAYLISTS_DIR,
        settings.STRM_DIR,
        settings.EPG_DIR,
        os.path.dirname(settings.LOG_FILE)
    ]:
        os.makedirs(directory, exist_ok=True)
except (PermissionError, OSError):
    # In CI or restricted environments, directories will be created when needed
    pass
