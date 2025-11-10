"""VOD API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.core.database import get_db
from app.models.vod import VODMovie, VODSeries, VODEpisode

router = APIRouter()


class MovieResponse(BaseModel):
    id: int
    title: str
    year: Optional[int]
    genre: Optional[str]
    rating: Optional[float]
    cover_url: Optional[str]
    is_active: bool
    strm_file_path: Optional[str]

    class Config:
        from_attributes = True


class SeriesResponse(BaseModel):
    id: int
    title: str
    year: Optional[int]
    genre: Optional[str]
    season_count: int
    episode_count: int
    cover_url: Optional[str]

    class Config:
        from_attributes = True


@router.get("/movies", response_model=List[MovieResponse])
async def list_movies(
    genre: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List VOD movies."""
    query = select(VODMovie).where(VODMovie.is_active.is_(True))

    if genre:
        query = query.where(VODMovie.genre == genre)

    query = query.offset(skip).limit(limit).order_by(VODMovie.title)

    result = await db.execute(query)
    movies = result.scalars().all()

    return movies


@router.get("/series", response_model=List[SeriesResponse])
async def list_series(
    genre: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List VOD series."""
    query = select(VODSeries).where(VODSeries.is_active.is_(True))

    if genre:
        query = query.where(VODSeries.genre == genre)

    query = query.offset(skip).limit(limit).order_by(VODSeries.title)

    result = await db.execute(query)
    series = result.scalars().all()

    return series


@router.post("/generate-strm")
async def generate_strm_files(db: AsyncSession = Depends(get_db)):
    """Trigger STRM file generation."""
    from app.tasks.vod_tasks import generate_strm_files as generate_strm_task
    try:
        task = generate_strm_task.delay()
        return {"status": "accepted", "message": "STRM generation task queued", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue STRM generation: {str(e)}")


@router.get("/stats")
async def get_vod_stats(db: AsyncSession = Depends(get_db)):
    """Get VOD statistics."""
    movie_count = await db.scalar(select(func.count(VODMovie.id)).where(VODMovie.is_active.is_(True)))
    series_count = await db.scalar(select(func.count(VODSeries.id)).where(VODSeries.is_active.is_(True)))
    episode_count = await db.scalar(select(func.count(VODEpisode.id)).where(VODEpisode.is_active.is_(True)))

    return {
        "total_movies": movie_count or 0,
        "total_series": series_count or 0,
        "total_episodes": episode_count or 0
    }
