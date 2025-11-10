"""User favorites API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User, UserFavorite
from app.models.channel import Channel
from app.models.vod import VODMovie, VODSeries

router = APIRouter()


# Schemas
class FavoriteCreate(BaseModel):
    """Schema for adding a favorite."""
    channel_id: Optional[int] = None
    vod_movie_id: Optional[int] = None
    vod_series_id: Optional[int] = None


class ChannelInfo(BaseModel):
    """Channel information."""
    id: int
    name: str
    logo_url: Optional[str]


class MovieInfo(BaseModel):
    """Movie information."""
    id: int
    title: str
    cover_url: Optional[str]
    year: Optional[int]


class SeriesInfo(BaseModel):
    """Series information."""
    id: int
    title: str
    cover_url: Optional[str]
    year: Optional[int]


class FavoriteResponse(BaseModel):
    """Schema for favorite response."""
    id: int
    user_id: int
    channel: Optional[ChannelInfo] = None
    vod_movie: Optional[MovieInfo] = None
    vod_series: Optional[SeriesInfo] = None
    created_at: str

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's favorites."""
    result = await db.execute(
        select(UserFavorite)
        .options(
            selectinload(UserFavorite.channel),
            selectinload(UserFavorite.vod_movie),
            selectinload(UserFavorite.vod_series)
        )
        .where(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.created_at.desc())
    )
    favorites = result.scalars().all()

    return [
        FavoriteResponse(
            id=fav.id,
            user_id=fav.user_id,
            channel=ChannelInfo(
                id=fav.channel.id,
                name=fav.channel.name,
                logo_url=fav.channel.logo_url
            ) if fav.channel else None,
            vod_movie=MovieInfo(
                id=fav.vod_movie.id,
                title=fav.vod_movie.title,
                cover_url=fav.vod_movie.cover_url,
                year=fav.vod_movie.year
            ) if fav.vod_movie else None,
            vod_series=SeriesInfo(
                id=fav.vod_series.id,
                title=fav.vod_series.title,
                cover_url=fav.vod_series.cover_url,
                year=fav.vod_series.year
            ) if fav.vod_series else None,
            created_at=fav.created_at.isoformat()
        )
        for fav in favorites
    ]


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a favorite."""
    # Validate that exactly one ID is provided
    ids_provided = sum([
        favorite_data.channel_id is not None,
        favorite_data.vod_movie_id is not None,
        favorite_data.vod_series_id is not None
    ])

    if ids_provided != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactly one of channel_id, vod_movie_id, or vod_series_id must be provided"
        )

    # Check if favorite already exists
    existing = await db.scalar(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.channel_id == favorite_data.channel_id,
            UserFavorite.vod_movie_id == favorite_data.vod_movie_id,
            UserFavorite.vod_series_id == favorite_data.vod_series_id
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Favorite already exists"
        )

    # Verify the item exists
    if favorite_data.channel_id:
        channel = await db.scalar(
            select(Channel).where(Channel.id == favorite_data.channel_id)
        )
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
    elif favorite_data.vod_movie_id:
        movie = await db.scalar(
            select(VODMovie).where(VODMovie.id == favorite_data.vod_movie_id)
        )
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
    elif favorite_data.vod_series_id:
        series = await db.scalar(
            select(VODSeries).where(VODSeries.id == favorite_data.vod_series_id)
        )
        if not series:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Series not found"
            )

    # Create favorite
    new_favorite = UserFavorite(
        user_id=current_user.id,
        channel_id=favorite_data.channel_id,
        vod_movie_id=favorite_data.vod_movie_id,
        vod_series_id=favorite_data.vod_series_id
    )

    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)

    # Load relationships
    await db.refresh(new_favorite, ["channel", "vod_movie", "vod_series"])

    return FavoriteResponse(
        id=new_favorite.id,
        user_id=new_favorite.user_id,
        channel=ChannelInfo(
            id=new_favorite.channel.id,
            name=new_favorite.channel.name,
            logo_url=new_favorite.channel.logo_url
        ) if new_favorite.channel else None,
        vod_movie=MovieInfo(
            id=new_favorite.vod_movie.id,
            title=new_favorite.vod_movie.title,
            cover_url=new_favorite.vod_movie.cover_url,
            year=new_favorite.vod_movie.year
        ) if new_favorite.vod_movie else None,
        vod_series=SeriesInfo(
            id=new_favorite.vod_series.id,
            title=new_favorite.vod_series.title,
            cover_url=new_favorite.vod_series.cover_url,
            year=new_favorite.vod_series.year
        ) if new_favorite.vod_series else None,
        created_at=new_favorite.created_at.isoformat()
    )


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    favorite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a favorite."""
    # Get favorite
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == current_user.id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    await db.delete(favorite)
    await db.commit()

    return None


@router.delete("/channel/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_by_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a favorite by channel ID."""
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.channel_id == channel_id,
            UserFavorite.user_id == current_user.id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    await db.delete(favorite)
    await db.commit()

    return None
