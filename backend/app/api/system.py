"""System information and configuration API endpoints."""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.config import settings, generate_secret_key
from app.core.auth import get_current_user
from app.models.user import User
from app.models.provider import Provider
from app.models.channel import Channel, ChannelStream
from app.models.vod import VODMovie, VODSeries
from pydantic import BaseModel
from typing import List, Dict, Any
import platform
import os
import secrets
from pathlib import Path

router = APIRouter()


@router.get("/info")
async def get_system_info(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system information and configuration.
    Shows important URLs and settings for user reference.
    """
    # Get base URL from request
    scheme = request.url.scheme
    host_header = request.headers.get("host", "localhost:8000")
    base_url = f"{scheme}://{host_header}"

    # Get database stats
    provider_count = await db.scalar(select(func.count(Provider.id)))
    channel_count = await db.scalar(select(func.count(Channel.id)))
    stream_count = await db.scalar(select(func.count(ChannelStream.id)))
    movie_count = await db.scalar(select(func.count(VODMovie.id)))
    series_count = await db.scalar(select(func.count(VODSeries.id)))

    # Build system info
    system_info = {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG
        },
        "platform": {
            "os": platform.system(),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        },
        "urls": {
            "web_ui": base_url,
            "api_base": f"{base_url}/api",
            "hdhr_discover": f"{base_url}/discover.json",
            "hdhr_lineup": f"{base_url}/lineup.json",
            "m3u_playlist": f"{base_url.replace(':8000', ':8080')}/playlists/merged_playlist_all.m3u" if ":8000" in base_url else f"{base_url}/playlists/merged_playlist_all.m3u"
        },
        "hdhr": {
            "enabled": True,
            "device_id": settings.HDHR_DEVICE_ID,
            "tuner_count": settings.HDHR_TUNER_COUNT,
            "proxy_mode": settings.HDHR_PROXY_MODE,
            "instructions": "Add this URL in Emby/Plex: " + base_url
        },
        "stats": {
            "providers": provider_count or 0,
            "channels": channel_count or 0,
            "streams": stream_count or 0,
            "movies": movie_count or 0,
            "series": series_count or 0
        },
        "paths": {
            "strm_output": settings.STRM_DIR,
            "playlists": settings.PLAYLISTS_DIR,
            "epg": settings.EPG_DIR
        },
        "settings": {
            "fuzzy_match_threshold": settings.DEFAULT_FUZZY_MATCH_THRESHOLD,
            "logo_matching": settings.ENABLE_LOGO_MATCHING,
            "bitrate_analysis": settings.ENABLE_BITRATE_ANALYSIS,
            "emby_integration": bool(settings.EMBY_HOST)
        }
    }

    return system_info


@router.get("/health")
async def system_health(db: AsyncSession = Depends(get_db)):
    """Quick system health check."""
    try:
        # Test database connection
        await db.execute(select(func.count(User.id)))
        db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "celery": "available"  # Would need actual Celery check
    }


class ConfigUpdate(BaseModel):
    """Configuration update model."""
    debug: bool = None
    allowed_origins: List[str] = None
    health_check_timeout: int = None
    sync_interval: int = None
    frontend_port: int = None
    backend_port: int = None


class SecretKeyRotate(BaseModel):
    """Secret key rotation response."""
    new_secret_key: str
    message: str


@router.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """
    Get current system configuration (safe values only).
    
    Returns sanitized configuration for display in web interface.
    """
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "health_check_timeout": settings.HEALTH_CHECK_TIMEOUT,
        "health_check_concurrent": settings.HEALTH_CHECK_CONCURRENT,
        "verify_ssl": settings.VERIFY_SSL,
        "max_providers": settings.MAX_PROVIDERS,
        "sync_interval": settings.SYNC_INTERVAL,
        "epg_refresh_interval": settings.EPG_REFRESH_INTERVAL,
        "epg_days": settings.EPG_DAYS,
        "has_secret_key": bool(settings.SECRET_KEY),  # Don't expose the actual key
    }


@router.put("/config")
async def update_configuration(config: ConfigUpdate) -> Dict[str, str]:
    """
    Update system configuration through web interface.
    
    Modifies the .env file with new values.
    """
    env_file = Path("/app/data/.env")  # Changed from /app/.env
    
    if not env_file.exists():
        raise HTTPException(status_code=500, detail=".env file not found")
    
    # Read current .env
    env_lines = env_file.read_text().split('\n')
    updated_lines = []
    
    for line in env_lines:
        if line.startswith('#') or not line.strip():
            updated_lines.append(line)
            continue
            
        if '=' in line:
            key, _ = line.split('=', 1)
            key = key.strip()
            
            # Update values if provided
            if config.debug is not None and key == 'DEBUG':
                updated_lines.append(f'DEBUG={str(config.debug).lower()}')
            elif config.allowed_origins is not None and key == 'ALLOWED_ORIGINS':
                import json
                updated_lines.append(f'ALLOWED_ORIGINS={json.dumps(config.allowed_origins)}')
            elif config.health_check_timeout is not None and key == 'HEALTH_CHECK_TIMEOUT':
                updated_lines.append(f'HEALTH_CHECK_TIMEOUT={config.health_check_timeout}')
            elif config.sync_interval is not None and key == 'SYNC_INTERVAL':
                updated_lines.append(f'SYNC_INTERVAL={config.sync_interval}')
            elif config.frontend_port is not None and key == 'FRONTEND_PORT':
                updated_lines.append(f'FRONTEND_PORT={config.frontend_port}')
            elif config.backend_port is not None and key == 'BACKEND_PORT':
                updated_lines.append(f'BACKEND_PORT={config.backend_port}')
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Write updated .env
    env_file.write_text('\n'.join(updated_lines))
    
    restart_note = ""
    if config.frontend_port is not None or config.backend_port is not None:
        restart_note = " Port changes require: docker-compose down && docker-compose up -d"
    
    return {
        "message": f"Configuration updated successfully.{restart_note}",
        "restart_command": "docker-compose restart backend"
    }


@router.post("/rotate-secret-key")
async def rotate_secret_key() -> SecretKeyRotate:
    """
    Generate a new SECRET_KEY.
    
    ⚠️ WARNING: This will invalidate all existing JWT tokens.
    Users will need to log in again.
    """
    new_key = generate_secret_key()
    
    env_file = Path("/app/data/.env")  # Changed from /app/.env
    if env_file.exists():
        content = env_file.read_text()
        # Replace SECRET_KEY line
        lines = content.split('\n')
        updated_lines = []
        for line in lines:
            if line.startswith('SECRET_KEY='):
                updated_lines.append(f'SECRET_KEY={new_key}')
            else:
                updated_lines.append(line)
        env_file.write_text('\n'.join(updated_lines))
    
    return SecretKeyRotate(
        new_secret_key=new_key,
        message="Secret key rotated successfully. All users must log in again. Restart required."
    )
