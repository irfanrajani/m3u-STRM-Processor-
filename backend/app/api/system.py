"""System information API endpoints."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.user import User
from app.models.provider import Provider
from app.models.channel import Channel, ChannelStream
from app.models.vod import VODMovie, VODSeries
import platform
import os

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
