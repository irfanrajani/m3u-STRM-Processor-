"""Settings API endpoints."""
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.models.settings import AppSettings

router = APIRouter()


class SettingResponse(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: Any


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    """Get a setting by key."""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    return setting


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, data: SettingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a setting."""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    setting = result.scalar_one_or_none()

    if not setting:
        # Create new setting
        setting = AppSettings(key=key, value=data.value)
        db.add(setting)
    else:
        setting.value = data.value

    await db.commit()
    await db.refresh(setting)

    return setting


@router.get("/")
async def list_settings(db: AsyncSession = Depends(get_db)):
    """List all settings."""
    result = await db.execute(select(AppSettings))
    settings = result.scalars().all()
    return settings


from typing import Optional
