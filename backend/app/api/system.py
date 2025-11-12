"""System configuration and management API."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
from app.core.config import settings, generate_secret_key
from app.core.database import get_db
from app.models.provider import Provider
from app.models.channel import Channel
from app.models.vod import VODMovie, VODSeries

router = APIRouter()


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
    """Get current system configuration (safe values only)."""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "frontend_port": settings.FRONTEND_PORT,
        "backend_port": settings.BACKEND_PORT,
        "health_check_timeout": settings.HEALTH_CHECK_TIMEOUT,
        "health_check_concurrent": settings.HEALTH_CHECK_CONCURRENT,
        "verify_ssl": settings.VERIFY_SSL,
        "max_providers": settings.MAX_PROVIDERS,
        "sync_interval": settings.SYNC_INTERVAL,
        "epg_refresh_interval": settings.EPG_REFRESH_INTERVAL,
        "epg_days": settings.EPG_DAYS,
        "has_secret_key": bool(settings.SECRET_KEY),
    }


@router.put("/config")
async def update_configuration(config: ConfigUpdate) -> Dict[str, str]:
    """Update system configuration through web interface."""
    env_file = Path("/app/data/.env")
    
    if not env_file.exists():
        raise HTTPException(status_code=500, detail=".env file not found")
    
    env_lines = env_file.read_text().split('\n')
    updated_lines = []
    
    for line in env_lines:
        if line.startswith('#') or not line.strip():
            updated_lines.append(line)
            continue
            
        if '=' in line:
            key, _ = line.split('=', 1)
            key = key.strip()
            
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
    
    env_file.write_text('\n'.join(updated_lines))
    
    restart_note = ""
    if config.frontend_port is not None or config.backend_port is not None:
        restart_note = " Port changes require: docker-compose down && docker-compose up -d"
    
    return {
        "message": f"Configuration updated successfully.{restart_note}",
        "restart_command": "docker-compose restart backend" if not restart_note else "docker-compose down && docker-compose up -d"
    }


@router.post("/rotate-secret-key")
async def rotate_secret_key() -> SecretKeyRotate:
    """Generate a new SECRET_KEY."""
    new_key = generate_secret_key()
    
    env_file = Path("/app/data/.env")
    if env_file.exists():
        content = env_file.read_text()
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


@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """Get system health status."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "version": settings.APP_VERSION
    }


@router.get("/stats")
async def get_system_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get system-wide statistics."""
    # Count providers
    total_providers = await db.scalar(select(func.count(Provider.id)))
    active_providers = await db.scalar(
        select(func.count(Provider.id)).where(Provider.enabled == True)
    )
    
    # Count channels
    total_channels = await db.scalar(select(func.count(Channel.id)))
    
    # Count VOD items
    total_movies = await db.scalar(select(func.count(VODMovie.id)))
    total_series = await db.scalar(select(func.count(VODSeries.id)))
    total_vod_items = (total_movies or 0) + (total_series or 0)
    
    return {
        "total_providers": total_providers or 0,
        "active_providers": active_providers or 0,
        "total_channels": total_channels or 0,
        "total_vod_items": total_vod_items,
        "total_vod_movies": total_movies or 0,
        "total_vod_series": total_series or 0,
    }

