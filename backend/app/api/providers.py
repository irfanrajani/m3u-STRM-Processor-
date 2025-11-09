"""Provider API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.models.provider import Provider
from app.services.provider_manager import ProviderManager

router = APIRouter()


# Pydantic schemas
class ProviderBase(BaseModel):
    name: str
    provider_type: str  # 'xstream' or 'm3u'
    enabled: bool = True
    priority: int = 0
    xstream_host: Optional[str] = None
    xstream_username: Optional[str] = None
    xstream_password: Optional[str] = None
    xstream_backup_hosts: Optional[List[str]] = None
    m3u_url: Optional[str] = None
    m3u_backup_urls: Optional[List[str]] = None
    epg_url: Optional[str] = None
    health_check_enabled: bool = True
    health_check_timeout: int = 10


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    xstream_host: Optional[str] = None
    xstream_username: Optional[str] = None
    xstream_password: Optional[str] = None
    xstream_backup_hosts: Optional[List[str]] = None
    m3u_url: Optional[str] = None
    m3u_backup_urls: Optional[List[str]] = None
    epg_url: Optional[str] = None
    health_check_enabled: Optional[bool] = None
    health_check_timeout: Optional[int] = None


class ProviderResponse(ProviderBase):
    id: int
    total_channels: int
    active_channels: int
    total_vod_movies: int
    total_vod_series: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProviderResponse])
async def list_providers(db: AsyncSession = Depends(get_db)):
    """List all providers."""
    result = await db.execute(select(Provider))
    providers = result.scalars().all()
    return providers


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Get provider by ID."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return provider


@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(provider_data: ProviderCreate, db: AsyncSession = Depends(get_db)):
    """Create a new provider."""
    # Validate provider type
    if provider_data.provider_type not in ['xstream', 'm3u']:
        raise HTTPException(status_code=400, detail="Invalid provider type")

    # Validate required fields
    if provider_data.provider_type == 'xstream':
        if not all([provider_data.xstream_host, provider_data.xstream_username, provider_data.xstream_password]):
            raise HTTPException(status_code=400, detail="Xstream provider requires host, username, and password")
    elif provider_data.provider_type == 'm3u':
        if not provider_data.m3u_url:
            raise HTTPException(status_code=400, detail="M3U provider requires URL")

    # Check for duplicate name
    result = await db.execute(select(Provider).where(Provider.name == provider_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Provider with this name already exists")

    # Create provider
    provider = Provider(**provider_data.model_dump())
    db.add(provider)
    await db.commit()
    await db.refresh(provider)

    return provider


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(provider_id: int, provider_data: ProviderUpdate, db: AsyncSession = Depends(get_db)):
    """Update a provider."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Update fields
    update_data = provider_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    await db.commit()
    await db.refresh(provider)

    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a provider."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    await db.delete(provider)
    await db.commit()


@router.post("/{provider_id}/test")
async def test_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Test provider connection."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    try:
        if provider.provider_type == 'xstream':
            success = await ProviderManager.test_xstream_connection(
                provider.xstream_host,
                provider.xstream_username,
                provider.xstream_password
            )
        else:
            success = await ProviderManager.test_m3u_connection(provider.m3u_url)

        return {"success": success, "message": "Connection successful" if success else "Connection failed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.post("/{provider_id}/sync")
async def sync_provider(provider_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger provider synchronization."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # This will be handled by Celery task in production
    # For now, return accepted status
    return {"status": "accepted", "message": "Sync task queued"}
