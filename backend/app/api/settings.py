"""Settings API endpoints."""
import json
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.settings import AppSettings
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


class SettingResponse(BaseModel):
    key: str
    value: Any
    value_type: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: Any


class BulkSettingsUpdate(BaseModel):
    settings: Dict[str, Any]


# Default settings configuration
DEFAULT_SETTINGS = {
    # Channel Matching
    "fuzzy_match_threshold": {
        "value": 85,
        "type": "int",
        "description": "Threshold for fuzzy matching channel names (0-100). Higher = stricter matching."
    },
    "enable_logo_matching": {
        "value": True,
        "type": "bool",
        "description": "Use logo image comparison for better channel matching"
    },
    "logo_match_threshold": {
        "value": 90,
        "type": "int",
        "description": "Threshold for logo similarity matching (0-100)"
    },

    # Quality Analysis
    "enable_bitrate_analysis": {
        "value": True,
        "type": "bool",
        "description": "Analyze stream bitrate using FFprobe (slower but more accurate)"
    },
    "ffprobe_timeout": {
        "value": 15,
        "type": "int",
        "description": "Timeout in seconds for FFprobe analysis"
    },

    # Health Check - Live TV
    "health_check_enabled": {
        "value": True,
        "type": "bool",
        "description": "Enable automatic health checks for live streams"
    },
    "health_check_schedule": {
        "value": "0 3 * * *",
        "type": "string",
        "description": "Cron schedule for live TV health checks (Daily at 3 AM)"
    },
    "health_check_timeout": {
        "value": 10,
        "type": "int",
        "description": "Timeout in seconds for stream health check"
    },
    "max_concurrent_health_checks": {
        "value": 50,
        "type": "int",
        "description": "Maximum number of streams to check simultaneously"
    },
    "health_check_failure_threshold": {
        "value": 3,
        "type": "int",
        "description": "Number of consecutive failures before marking stream inactive"
    },

    # Health Check - VOD
    "vod_health_check_enabled": {
        "value": False,
        "type": "bool",
        "description": "Enable automatic health checks for VOD content"
    },
    "vod_health_check_schedule": {
        "value": "0 4 * * 0",
        "type": "string",
        "description": "Cron schedule for VOD health checks (Weekly Sunday at 4 AM)"
    },
    "vod_health_check_timeout": {
        "value": 15,
        "type": "int",
        "description": "Timeout in seconds for VOD health check"
    },

    # Provider Sync
    "auto_sync_enabled": {
        "value": True,
        "type": "bool",
        "description": "Automatically sync providers on schedule"
    },
    "auto_sync_schedule": {
        "value": "0 */6 * * *",
        "type": "string",
        "description": "Cron schedule for provider sync (Every 6 hours)"
    },
    "sync_timeout": {
        "value": 3600,
        "type": "int",
        "description": "Maximum time in seconds for provider sync"
    },

    # EPG
    "epg_refresh_enabled": {
        "value": True,
        "type": "bool",
        "description": "Automatically refresh EPG data"
    },
    "epg_refresh_schedule": {
        "value": "0 2 * * *",
        "type": "string",
        "description": "Cron schedule for EPG refresh (Daily at 2 AM)"
    },
    "epg_retention_days": {
        "value": 7,
        "type": "int",
        "description": "Number of days to keep EPG data"
    },

    # Playlist Generation
    "auto_generate_playlists": {
        "value": True,
        "type": "bool",
        "description": "Automatically generate M3U playlists after sync"
    },
    "playlist_include_inactive": {
        "value": False,
        "type": "bool",
        "description": "Include inactive streams in playlists"
    },
    "playlist_prefer_quality": {
        "value": "highest",
        "type": "string",
        "description": "Preferred quality for playlists: highest, 1080p, 720p"
    },

    # STRM Files
    "strm_organize_by_genre": {
        "value": True,
        "type": "bool",
        "description": "Organize STRM files by genre"
    },
    "strm_include_year": {
        "value": True,
        "type": "bool",
        "description": "Include year in STRM file paths"
    },

    # Emby Integration
    "emby_enabled": {
        "value": False,
        "type": "bool",
        "description": "Enable Emby integration"
    },
    "emby_host": {
        "value": "",
        "type": "string",
        "description": "Emby server URL (e.g., http://localhost:8096)"
    },
    "emby_api_key": {
        "value": "",
        "type": "string",
        "description": "Emby API key"
    },
    "emby_auto_refresh_library": {
        "value": True,
        "type": "bool",
        "description": "Automatically refresh Emby library after STRM generation"
    },

    # Logging
    "log_level": {
        "value": "INFO",
        "type": "string",
        "description": "Logging level: DEBUG, INFO, WARNING, ERROR"
    },
    "log_retention_days": {
        "value": 30,
        "type": "int",
        "description": "Number of days to keep log files"
    },

    # Database
    "db_pool_size": {
        "value": 20,
        "type": "int",
        "description": "Database connection pool size"
    },
    "db_max_overflow": {
        "value": 40,
        "type": "int",
        "description": "Maximum database overflow connections"
    },

    # Performance
    "enable_caching": {
        "value": True,
        "type": "bool",
        "description": "Enable Redis caching for API responses"
    },
    "cache_ttl": {
        "value": 300,
        "type": "int",
        "description": "Cache time-to-live in seconds"
    },
}


async def initialize_default_settings(db: AsyncSession):
    """Initialize default settings if they don't exist."""
    for key, config in DEFAULT_SETTINGS.items():
        result = await db.execute(select(AppSettings).where(AppSettings.key == key))
        existing = result.scalar_one_or_none()

        if not existing:
            setting = AppSettings(
                key=key,
                value=json.dumps(config["value"]),
                value_type=config["type"],
                description=config["description"]
            )
            db.add(setting)

    await db.commit()


@router.get("/")
async def list_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all settings."""
    # Initialize defaults if needed
    await initialize_default_settings(db)

    result = await db.execute(select(AppSettings))
    settings = result.scalars().all()

    # Convert to dict with proper types
    settings_dict = {}
    for setting in settings:
        try:
            value = json.loads(setting.value) if setting.value else None
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse setting {setting.key}: {e}")
            value = setting.value

        settings_dict[setting.key] = {
            "value": value,
            "type": setting.value_type,
            "description": setting.description
        }

    return settings_dict


@router.get("/{key}")
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific setting."""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()

    if not setting:
        # Return default if exists
        if key in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[key]
        raise HTTPException(status_code=404, detail="Setting not found")

    try:
        value = json.loads(setting.value) if setting.value else None
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse setting {key}: {e}")
        value = setting.value

    return {
        "value": value,
        "type": setting.value_type,
        "description": setting.description
    }


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific setting."""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()

    value_str = json.dumps(data.value)

    if not setting:
        # Create new setting
        setting = AppSettings(
            key=key,
            value=value_str,
            value_type=type(data.value).__name__,
            description=DEFAULT_SETTINGS.get(key, {}).get("description")
        )
        db.add(setting)
    else:
        setting.value = value_str

    await db.commit()
    await db.refresh(setting)

    return {
        "key": setting.key,
        "value": data.value,
        "type": setting.value_type,
        "description": setting.description
    }


@router.post("/bulk-update")
async def bulk_update_settings(
    data: BulkSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update multiple settings at once."""
    updated = []

    for key, value in data.settings.items():
        result = await db.execute(select(AppSettings).where(AppSettings.key == key))
        setting = result.scalar_one_or_none()

        value_str = json.dumps(value)

        if not setting:
            setting = AppSettings(
                key=key,
                value=value_str,
                value_type=type(value).__name__,
                description=DEFAULT_SETTINGS.get(key, {}).get("description")
            )
            db.add(setting)
        else:
            setting.value = value_str

        updated.append(key)

    await db.commit()

    return {
        "updated": updated,
        "count": len(updated)
    }


@router.post("/reset-defaults")
async def reset_to_defaults(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset all settings to default values."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can reset settings")

    # Delete all existing settings
    result = await db.execute(select(AppSettings))
    settings = result.scalars().all()
    for setting in settings:
        await db.delete(setting)

    # Reinitialize defaults
    await initialize_default_settings(db)

    return {"message": "Settings reset to defaults"}


@router.get("/categories/list")
async def get_settings_categories(
    current_user: User = Depends(get_current_user)
):
    """Get settings organized by category."""
    return {
        "Channel Matching": [
            "fuzzy_match_threshold",
            "enable_logo_matching",
            "logo_match_threshold"
        ],
        "Quality Analysis": [
            "enable_bitrate_analysis",
            "ffprobe_timeout"
        ],
        "Health Checks - Live TV": [
            "health_check_enabled",
            "health_check_schedule",
            "health_check_timeout",
            "max_concurrent_health_checks",
            "health_check_failure_threshold"
        ],
        "Health Checks - VOD": [
            "vod_health_check_enabled",
            "vod_health_check_schedule",
            "vod_health_check_timeout"
        ],
        "Provider Sync": [
            "auto_sync_enabled",
            "auto_sync_schedule",
            "sync_timeout"
        ],
        "EPG": [
            "epg_refresh_enabled",
            "epg_refresh_schedule",
            "epg_retention_days"
        ],
        "Playlists": [
            "auto_generate_playlists",
            "playlist_include_inactive",
            "playlist_prefer_quality"
        ],
        "STRM Files": [
            "strm_organize_by_genre",
            "strm_include_year"
        ],
        "Emby Integration": [
            "emby_enabled",
            "emby_host",
            "emby_api_key",
            "emby_auto_refresh_library"
        ],
        "System": [
            "log_level",
            "log_retention_days",
            "db_pool_size",
            "db_max_overflow",
            "enable_caching",
            "cache_ttl"
        ]
    }
