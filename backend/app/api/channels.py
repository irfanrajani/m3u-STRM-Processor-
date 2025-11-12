"""Channels API endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.core.database import get_db
from app.models.channel import Channel, ChannelStream
from app.models.provider import Provider
from app.services.health_checker import StreamHealthChecker

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
    normalized_name: Optional[str]

    class Config:
        from_attributes = True


class StreamResponse(BaseModel):
    id: int
    channel_id: int
    provider_id: int
    provider_name: Optional[str] = None
    stream_url: str
    stream_format: Optional[str]
    resolution: Optional[str]
    bitrate: Optional[int]
    codec: Optional[str]
    quality_score: int
    is_active: bool
    priority_order: int
    response_time: Optional[float]
    last_check: Optional[datetime]
    consecutive_failures: int
    failure_reason: Optional[str]
    original_name: Optional[str]
    original_category: Optional[str]

    class Config:
        from_attributes = True


class StreamUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    priority_order: Optional[int] = None


class StreamTestResponse(BaseModel):
    success: bool
    status: str
    response_time: Optional[float]
    quality_score: Optional[int]
    error: Optional[str]


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
    """Get all streams for a channel with provider names."""
    result = await db.execute(
        select(ChannelStream, Provider.name)
        .join(Provider, ChannelStream.provider_id == Provider.id)
        .where(ChannelStream.channel_id == channel_id)
        .order_by(ChannelStream.priority_order, ChannelStream.quality_score.desc())
    )
    
    streams = []
    for stream, provider_name in result.all():
        stream_dict = {
            "id": stream.id,
            "channel_id": stream.channel_id,
            "provider_id": stream.provider_id,
            "provider_name": provider_name,
            "stream_url": stream.stream_url,
            "stream_format": stream.stream_format,
            "resolution": stream.resolution,
            "bitrate": stream.bitrate,
            "codec": stream.codec,
            "quality_score": stream.quality_score or 0,
            "is_active": stream.is_active,
            "priority_order": stream.priority_order or 0,
            "response_time": stream.response_time,
            "last_check": stream.last_check,
            "consecutive_failures": stream.consecutive_failures or 0,
            "failure_reason": stream.failure_reason,
            "original_name": stream.original_name,
            "original_category": stream.original_category,
        }
        streams.append(stream_dict)

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


@router.patch("/streams/{stream_id}", response_model=StreamResponse)
async def update_stream(
    stream_id: int,
    update: StreamUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update stream properties (active status, priority order)."""
    result = await db.execute(select(ChannelStream).where(ChannelStream.id == stream_id))
    stream = result.scalar_one_or_none()

    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Update fields if provided
    if update.is_active is not None:
        stream.is_active = update.is_active
    if update.priority_order is not None:
        stream.priority_order = update.priority_order

    await db.commit()
    await db.refresh(stream)

    # Get provider name
    provider_result = await db.execute(select(Provider.name).where(Provider.id == stream.provider_id))
    provider_name = provider_result.scalar_one_or_none()

    return {
        "id": stream.id,
        "channel_id": stream.channel_id,
        "provider_id": stream.provider_id,
        "provider_name": provider_name,
        "stream_url": stream.stream_url,
        "stream_format": stream.stream_format,
        "resolution": stream.resolution,
        "bitrate": stream.bitrate,
        "codec": stream.codec,
        "quality_score": stream.quality_score or 0,
        "is_active": stream.is_active,
        "priority_order": stream.priority_order or 0,
        "response_time": stream.response_time,
        "last_check": stream.last_check,
        "consecutive_failures": stream.consecutive_failures or 0,
        "failure_reason": stream.failure_reason,
        "original_name": stream.original_name,
        "original_category": stream.original_category,
    }


@router.post("/streams/{stream_id}/test", response_model=StreamTestResponse)
async def test_stream(stream_id: int, db: AsyncSession = Depends(get_db)):
    """Test stream connectivity and update health status."""
    result = await db.execute(select(ChannelStream).where(ChannelStream.id == stream_id))
    stream = result.scalar_one_or_none()

    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    try:
        # Initialize health checker
        health_checker = StreamHealthChecker()

        # Test the stream
        health_result = await health_checker.check_stream(stream.stream_url)

        # Update stream with test results
        stream.last_check = datetime.utcnow()
        stream.response_time = health_result.get('response_time')
        
        # Update quality score if we got new info
        if health_result.get('quality_score'):
            stream.quality_score = health_result['quality_score']
        
        # Update failure tracking
        if health_result.get('status') == 'healthy':
            stream.consecutive_failures = 0
            stream.last_success = datetime.utcnow()
            stream.failure_reason = None
        else:
            stream.consecutive_failures = (stream.consecutive_failures or 0) + 1
            stream.last_failure = datetime.utcnow()
            stream.failure_reason = health_result.get('error')

        await db.commit()

        return {
            "success": health_result.get('status') == 'healthy',
            "status": health_result.get('status', 'unknown'),
            "response_time": health_result.get('response_time'),
            "quality_score": health_result.get('quality_score'),
            "error": health_result.get('error')
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "response_time": None,
            "quality_score": None,
            "error": str(e)
        }
