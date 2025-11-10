"""Analytics and viewing history API endpoints."""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User, ViewingHistory
from app.models.channel import Channel
from app.models.vod import VODMovie, VODSeries

router = APIRouter()


# Schemas
class ViewingHistoryCreate(BaseModel):
    """Schema for creating viewing history entry."""
    channel_id: Optional[int] = None
    vod_movie_id: Optional[int] = None
    vod_series_id: Optional[int] = None
    stream_url: Optional[str] = None


class ViewingHistoryUpdate(BaseModel):
    """Schema for updating viewing history entry."""
    duration_seconds: Optional[int] = None
    completed: Optional[bool] = None


class ChannelInfo(BaseModel):
    """Channel information."""
    id: int
    name: str


class MovieInfo(BaseModel):
    """Movie information."""
    id: int
    title: str


class SeriesInfo(BaseModel):
    """Series information."""
    id: int
    title: str


class ViewingHistoryResponse(BaseModel):
    """Schema for viewing history response."""
    id: int
    user_id: int
    channel: Optional[ChannelInfo] = None
    vod_movie: Optional[MovieInfo] = None
    vod_series: Optional[SeriesInfo] = None
    duration_seconds: Optional[int]
    completed: bool
    started_at: str
    ended_at: Optional[str]

    class Config:
        from_attributes = True


class PopularChannel(BaseModel):
    """Popular channel statistics."""
    channel_id: int
    channel_name: str
    view_count: int
    total_watch_time_seconds: int
    unique_viewers: int


class ViewingStats(BaseModel):
    """User viewing statistics."""
    total_views: int
    total_watch_time_seconds: int
    channels_watched: int
    movies_watched: int
    series_watched: int
    avg_watch_time_seconds: int


class SystemStats(BaseModel):
    """System-wide analytics."""
    total_views_today: int
    total_views_week: int
    total_views_month: int
    unique_viewers_today: int
    most_watched_today: List[PopularChannel]


# Endpoints
@router.post("/history", response_model=ViewingHistoryResponse, status_code=status.HTTP_201_CREATED)
async def start_viewing_session(
    history_data: ViewingHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new viewing session."""
    # Validate that exactly one ID is provided
    ids_provided = sum([
        history_data.channel_id is not None,
        history_data.vod_movie_id is not None,
        history_data.vod_series_id is not None
    ])

    if ids_provided != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly one of channel_id, vod_movie_id, or vod_series_id must be provided"
        )

    # Create viewing history entry
    new_history = ViewingHistory(
        user_id=current_user.id,
        channel_id=history_data.channel_id,
        vod_movie_id=history_data.vod_movie_id,
        vod_series_id=history_data.vod_series_id,
        stream_url=history_data.stream_url,
        completed=False
    )

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    # Load relationships
    result = await db.execute(
        select(ViewingHistory)
        .options(
            selectinload(ViewingHistory.channel),
            selectinload(ViewingHistory.vod_movie),
            selectinload(ViewingHistory.vod_series)
        )
        .where(ViewingHistory.id == new_history.id)
    )
    new_history = result.scalar_one()

    return ViewingHistoryResponse(
        id=new_history.id,
        user_id=new_history.user_id,
        channel=ChannelInfo(
            id=new_history.channel.id,
            name=new_history.channel.name
        ) if new_history.channel else None,
        vod_movie=MovieInfo(
            id=new_history.vod_movie.id,
            title=new_history.vod_movie.title
        ) if new_history.vod_movie else None,
        vod_series=SeriesInfo(
            id=new_history.vod_series.id,
            title=new_history.vod_series.title
        ) if new_history.vod_series else None,
        duration_seconds=new_history.duration_seconds,
        completed=new_history.completed,
        started_at=new_history.started_at.isoformat(),
        ended_at=new_history.ended_at.isoformat() if new_history.ended_at else None
    )


@router.patch("/history/{history_id}", response_model=ViewingHistoryResponse)
async def update_viewing_session(
    history_id: int,
    update_data: ViewingHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a viewing session (e.g., mark as completed)."""
    # Get history entry
    result = await db.execute(
        select(ViewingHistory)
        .options(
            selectinload(ViewingHistory.channel),
            selectinload(ViewingHistory.vod_movie),
            selectinload(ViewingHistory.vod_series)
        )
        .where(
            ViewingHistory.id == history_id,
            ViewingHistory.user_id == current_user.id
        )
    )
    history = result.scalar_one_or_none()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viewing history not found"
        )

    # Update fields
    if update_data.duration_seconds is not None:
        history.duration_seconds = update_data.duration_seconds
    if update_data.completed is not None:
        history.completed = update_data.completed
        if update_data.completed and not history.ended_at:
            history.ended_at = datetime.utcnow()

    await db.commit()
    await db.refresh(history)

    return ViewingHistoryResponse(
        id=history.id,
        user_id=history.user_id,
        channel=ChannelInfo(
            id=history.channel.id,
            name=history.channel.name
        ) if history.channel else None,
        vod_movie=MovieInfo(
            id=history.vod_movie.id,
            title=history.vod_movie.title
        ) if history.vod_movie else None,
        vod_series=SeriesInfo(
            id=history.vod_series.id,
            title=history.vod_series.title
        ) if history.vod_series else None,
        duration_seconds=history.duration_seconds,
        completed=history.completed,
        started_at=history.started_at.isoformat(),
        ended_at=history.ended_at.isoformat() if history.ended_at else None
    )


@router.get("/history", response_model=List[ViewingHistoryResponse])
async def get_viewing_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's viewing history."""
    result = await db.execute(
        select(ViewingHistory)
        .options(
            selectinload(ViewingHistory.channel),
            selectinload(ViewingHistory.vod_movie),
            selectinload(ViewingHistory.vod_series)
        )
        .where(ViewingHistory.user_id == current_user.id)
        .order_by(ViewingHistory.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    history = result.scalars().all()

    return [
        ViewingHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            channel=ChannelInfo(id=h.channel.id, name=h.channel.name) if h.channel else None,
            vod_movie=MovieInfo(id=h.vod_movie.id, title=h.vod_movie.title) if h.vod_movie else None,
            vod_series=SeriesInfo(id=h.vod_series.id, title=h.vod_series.title) if h.vod_series else None,
            duration_seconds=h.duration_seconds,
            completed=h.completed,
            started_at=h.started_at.isoformat(),
            ended_at=h.ended_at.isoformat() if h.ended_at else None
        )
        for h in history
    ]


@router.get("/stats", response_model=ViewingStats)
async def get_user_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's viewing statistics."""
    since_date = datetime.utcnow() - timedelta(days=days)

    # Total views
    total_views = await db.scalar(
        select(func.count(ViewingHistory.id)).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.started_at >= since_date
        )
    )

    # Total watch time
    total_watch_time = await db.scalar(
        select(func.sum(ViewingHistory.duration_seconds)).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.started_at >= since_date,
            ViewingHistory.duration_seconds.isnot(None)
        )
    )

    # Channels watched
    channels_watched = await db.scalar(
        select(func.count(func.distinct(ViewingHistory.channel_id))).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.started_at >= since_date,
            ViewingHistory.channel_id.isnot(None)
        )
    )

    # Movies watched
    movies_watched = await db.scalar(
        select(func.count(func.distinct(ViewingHistory.vod_movie_id))).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.started_at >= since_date,
            ViewingHistory.vod_movie_id.isnot(None)
        )
    )

    # Series watched
    series_watched = await db.scalar(
        select(func.count(func.distinct(ViewingHistory.vod_series_id))).where(
            ViewingHistory.user_id == current_user.id,
            ViewingHistory.started_at >= since_date,
            ViewingHistory.vod_series_id.isnot(None)
        )
    )

    # Average watch time
    avg_watch_time = 0
    if total_views and total_watch_time:
        avg_watch_time = int(total_watch_time / total_views)

    return ViewingStats(
        total_views=total_views or 0,
        total_watch_time_seconds=int(total_watch_time or 0),
        channels_watched=channels_watched or 0,
        movies_watched=movies_watched or 0,
        series_watched=series_watched or 0,
        avg_watch_time_seconds=avg_watch_time
    )


@router.get("/popular", response_model=List[PopularChannel])
async def get_popular_channels(
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most popular channels based on viewing history."""
    since_date = datetime.utcnow() - timedelta(days=days)

    # Get popular channels
    result = await db.execute(
        select(
            ViewingHistory.channel_id,
            Channel.name,
            func.count(ViewingHistory.id).label('view_count'),
            func.sum(ViewingHistory.duration_seconds).label('total_watch_time'),
            func.count(func.distinct(ViewingHistory.user_id)).label('unique_viewers')
        )
        .join(Channel, ViewingHistory.channel_id == Channel.id)
        .where(
            ViewingHistory.started_at >= since_date,
            ViewingHistory.channel_id.isnot(None)
        )
        .group_by(ViewingHistory.channel_id, Channel.name)
        .order_by(desc('view_count'))
        .limit(limit)
    )

    rows = result.all()

    return [
        PopularChannel(
            channel_id=row.channel_id,
            channel_name=row.name,
            view_count=row.view_count,
            total_watch_time_seconds=int(row.total_watch_time or 0),
            unique_viewers=row.unique_viewers
        )
        for row in rows
    ]


@router.get("/admin/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get system-wide analytics (admin only)."""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Views today
    views_today = await db.scalar(
        select(func.count(ViewingHistory.id)).where(
            ViewingHistory.started_at >= today
        )
    )

    # Views this week
    views_week = await db.scalar(
        select(func.count(ViewingHistory.id)).where(
            ViewingHistory.started_at >= week_ago
        )
    )

    # Views this month
    views_month = await db.scalar(
        select(func.count(ViewingHistory.id)).where(
            ViewingHistory.started_at >= month_ago
        )
    )

    # Unique viewers today
    unique_today = await db.scalar(
        select(func.count(func.distinct(ViewingHistory.user_id))).where(
            ViewingHistory.started_at >= today
        )
    )

    # Most watched channels today
    result = await db.execute(
        select(
            ViewingHistory.channel_id,
            Channel.name,
            func.count(ViewingHistory.id).label('view_count'),
            func.sum(ViewingHistory.duration_seconds).label('total_watch_time'),
            func.count(func.distinct(ViewingHistory.user_id)).label('unique_viewers')
        )
        .join(Channel, ViewingHistory.channel_id == Channel.id)
        .where(
            ViewingHistory.started_at >= today,
            ViewingHistory.channel_id.isnot(None)
        )
        .group_by(ViewingHistory.channel_id, Channel.name)
        .order_by(desc('view_count'))
        .limit(5)
    )

    rows = result.all()
    most_watched = [
        PopularChannel(
            channel_id=row.channel_id,
            channel_name=row.name,
            view_count=row.view_count,
            total_watch_time_seconds=int(row.total_watch_time or 0),
            unique_viewers=row.unique_viewers
        )
        for row in rows
    ]

    return SystemStats(
        total_views_today=views_today or 0,
        total_views_week=views_week or 0,
        total_views_month=views_month or 0,
        unique_viewers_today=unique_today or 0,
        most_watched_today=most_watched
    )
