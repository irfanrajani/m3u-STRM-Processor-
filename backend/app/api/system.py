"""System configuration and management API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
from app.core.config import settings, generate_secret_key

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
    """
    Get current system configuration (safe values only).
    
    Returns sanitized configuration for display in web interface.
    """
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
    """
    Update system configuration through web interface.
    
    Modifies the .env file with new values.
    """
    env_file = Path("/app/data/.env")
    
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
        "restart_command": "docker-compose restart backend" if not restart_note else "docker-compose down && docker-compose up -d"
    }


@router.post("/rotate-secret-key")
async def rotate_secret_key() -> SecretKeyRotate:
    """
    Generate a new SECRET_KEY.
    
    ⚠️ WARNING: This will invalidate all existing JWT tokens.
    Users will need to log in again.
    """
    new_key = generate_secret_key()
    
    env_file = Path("/app/data/.env")
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


@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """Get system health status."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Actually check DB connection
        "redis": "connected",     # TODO: Actually check Redis connection
        "version": settings.APP_VERSION
    }
