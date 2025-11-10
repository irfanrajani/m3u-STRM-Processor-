"""Channels API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.core.database import get_db
from app.models.channel import Channel, ChannelStream

router = APIRouter()


class ChannelResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    region: Optional[str]
    variant: Optional[str]
    logo_url: Optional[str]
    epg_id: Optional[str]
    stream_count: int
    enabled: bool

    class Config:
        from_attributes = True


class StreamResponse(BaseModel):
    id: int
    stream_url: str
    resolution: Optional[str]
    bitrate: Optional[int]
    codec: Optional[str]
    is_active: bool
    priority_order: int
    response_time: Optional[float]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ChannelResponse])
async def list_channels(
    category: Optional[str] = None,
    enabled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List channels with optional filtering."""
    query = select(Channel)

    if category:
        query = query.where(Channel.category == category)
    if enabled is not None:
        query = query.where(Channel.enabled == enabled)

    query = query.offset(skip).limit(limit).order_by(Channel.name)

    result = await db.execute(query)
    channels = result.scalars().all()

    return channels


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    """Get channel details."""
    result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return channel


@router.get("/{channel_id}/streams", response_model=List[StreamResponse])
async def get_channel_streams(channel_id: int, db: AsyncSession = Depends(get_db)):
    """Get all streams for a channel."""
    result = await db.execute(
        select(ChannelStream)
        .where(ChannelStream.channel_id == channel_id)
        .order_by(ChannelStream.priority_order)
    )
    streams = result.scalars().all()

    return streams


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all channel categories."""
    result = await db.execute(
        select(Channel.category, func.count(Channel.id))
        .group_by(Channel.category)
        .order_by(Channel.category)
    )
    categories = [{"name": cat, "count": count} for cat, count in result.all() if cat]

    return categories
