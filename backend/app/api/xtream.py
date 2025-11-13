"""Xtream Codes API emulation for IPTV client compatibility."""
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.channel import Channel, ChannelStream
from app.models.vod import VODMovie, VODSeries, VODEpisode
from app.models.provider import Provider
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/player_api.php")
async def player_api(
    username: str = Query(...),
    password: str = Query(...),
    action: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    stream_id: Optional[int] = Query(None),
    series_id: Optional[int] = Query(None),
    vod_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Xtream Codes API emulation endpoint.

    Supports actions:
    - get_live_categories
    - get_live_streams
    - get_vod_categories
    - get_vod_streams
    - get_series_categories
    - get_series
    - get_series_info
    - get_vod_info
    """
    # Simple auth check (in production, verify against user database)
    if not username or not password:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Default action: return user info
    if not action:
        return await get_user_info(db, username)

    # Route to appropriate handler
    if action == "get_live_categories":
        return await get_live_categories(db)
    elif action == "get_live_streams":
        return await get_live_streams(db, category_id)
    elif action == "get_vod_categories":
        return await get_vod_categories(db)
    elif action == "get_vod_streams":
        return await get_vod_streams(db, category_id)
    elif action == "get_series_categories":
        return await get_series_categories(db)
    elif action == "get_series":
        return await get_series(db, category_id)
    elif action == "get_series_info":
        if not series_id:
            raise HTTPException(status_code=400, detail="series_id required")
        return await get_series_info(db, series_id)
    elif action == "get_vod_info":
        if not vod_id:
            raise HTTPException(status_code=400, detail="vod_id required")
        return await get_vod_info(db, vod_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


async def get_user_info(db: AsyncSession, username: str):
    """Get user info (Xtream format)."""
    # Get statistics
    total_channels = await db.scalar(select(func.count(Channel.id)).where(Channel.enabled.is_(True)))
    total_vod = await db.scalar(select(func.count(VODMovie.id)).where(VODMovie.is_active.is_(True)))
    total_series = await db.scalar(select(func.count(VODSeries.id)).where(VODSeries.is_active.is_(True)))

    return {
        "user_info": {
            "username": username,
            "password": "***",
            "message": "Welcome to IPTV Stream Manager",
            "auth": 1,
            "status": "Active",
            "exp_date": "1999999999",  # Never expires
            "is_trial": "0",
            "active_cons": "1",
            "created_at": int(datetime.utcnow().timestamp()),
            "max_connections": "3",
            "allowed_output_formats": ["m3u8", "ts", "rtmp"]
        },
        "server_info": {
            "url": settings.BASE_URL or "http://localhost:8000",
            "port": "8000",
            "https_port": "443",
            "server_protocol": "http",
            "rtmp_port": "1935",
            "timezone": "UTC",
            "timestamp_now": int(datetime.utcnow().timestamp()),
            "time_now": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        },
        "available": {
            "channels": total_channels or 0,
            "movies": total_vod or 0,
            "series": total_series or 0
        }
    }


async def get_live_categories(db: AsyncSession):
    """Get live TV categories."""
    result = await db.execute(
        select(Channel.category, func.count(Channel.id))
        .where(Channel.enabled.is_(True))
        .group_by(Channel.category)
        .order_by(Channel.category)
    )

    categories = []
    category_id = 1
    for category_name, count in result.all():
        if category_name:
            categories.append({
                "category_id": str(category_id),
                "category_name": category_name,
                "parent_id": 0
            })
            category_id += 1

    return categories


async def get_live_streams(db: AsyncSession, category_id: Optional[str] = None):
    """Get live TV streams in Xtream format."""
    query = select(Channel, ChannelStream).join(
        ChannelStream, Channel.id == ChannelStream.channel_id
    ).where(
        Channel.enabled.is_(True),
        ChannelStream.is_active.is_(True),
        ChannelStream.priority_order == 0  # Get primary stream only
    )

    # TODO: Filter by category if provided
    # (requires mapping category names to IDs)

    result = await db.execute(query)

    streams = []
    for channel, stream in result.all():
        # Build stream URL (use our proxy endpoint)
        stream_url = f"{settings.BASE_URL}/stream/channel/{channel.id}.m3u8"

        streams.append({
            "num": channel.id,
            "name": channel.name,
            "stream_type": "live",
            "stream_id": channel.id,
            "stream_icon": channel.logo_url or "",
            "epg_channel_id": channel.epg_id or "",
            "added": "0",
            "is_adult": "0",
            "category_name": channel.category or "Unknown",
            "category_id": "1",  # TODO: Map to actual category ID
            "series_no": None,
            "live": "1",
            "container_extension": "m3u8",
            "custom_sid": "",
            "direct_source": stream_url
        })

    return streams


async def get_vod_categories(db: AsyncSession):
    """Get VOD categories."""
    result = await db.execute(
        select(VODMovie.genre, func.count(VODMovie.id))
        .where(VODMovie.is_active.is_(True))
        .group_by(VODMovie.genre)
        .order_by(VODMovie.genre)
    )

    categories = []
    category_id = 1
    for genre, count in result.all():
        if genre:
            categories.append({
                "category_id": str(category_id),
                "category_name": genre,
                "parent_id": 0
            })
            category_id += 1

    return categories


async def get_vod_streams(db: AsyncSession, category_id: Optional[str] = None):
    """Get VOD streams in Xtream format."""
    query = select(VODMovie).where(VODMovie.is_active.is_(True))

    # TODO: Filter by category if provided

    result = await db.execute(query.limit(1000))
    movies = result.scalars().all()

    streams = []
    for movie in movies:
        streams.append({
            "num": movie.id,
            "name": movie.title,
            "stream_type": "movie",
            "stream_id": movie.id,
            "stream_icon": movie.cover_url or "",
            "rating": str(movie.rating) if movie.rating else "0",
            "rating_5based": round(movie.rating / 2, 1) if movie.rating else 0,
            "added": "0",
            "category_id": "1",  # TODO: Map genre to category ID
            "category_name": movie.genre or "Unknown",
            "container_extension": "mp4",
            "direct_source": movie.stream_url,
            "title": movie.title,
            "year": str(movie.year) if movie.year else ""
        })

    return streams


async def get_series_categories(db: AsyncSession):
    """Get series categories."""
    result = await db.execute(
        select(VODSeries.genre, func.count(VODSeries.id))
        .where(VODSeries.is_active.is_(True))
        .group_by(VODSeries.genre)
        .order_by(VODSeries.genre)
    )

    categories = []
    category_id = 1
    for genre, count in result.all():
        if genre:
            categories.append({
                "category_id": str(category_id),
                "category_name": genre,
                "parent_id": 0
            })
            category_id += 1

    return categories


async def get_series(db: AsyncSession, category_id: Optional[str] = None):
    """Get series list in Xtream format."""
    query = select(VODSeries).where(VODSeries.is_active.is_(True))

    # TODO: Filter by category if provided

    result = await db.execute(query.limit(1000))
    series_list = result.scalars().all()

    streams = []
    for series in series_list:
        streams.append({
            "num": series.id,
            "name": series.title,
            "series_id": series.id,
            "cover": series.cover_url or "",
            "plot": "",
            "cast": "",
            "director": "",
            "genre": series.genre or "Unknown",
            "releaseDate": str(series.year) if series.year else "",
            "last_modified": "0",
            "rating": "0",
            "rating_5based": 0,
            "backdrop_path": [],
            "youtube_trailer": "",
            "episode_run_time": "45",
            "category_id": "1",  # TODO: Map genre to category ID
            "category_name": series.genre or "Unknown"
        })

    return streams


async def get_series_info(db: AsyncSession, series_id: int):
    """Get detailed series info including episodes."""
    # Get series
    result = await db.execute(
        select(VODSeries).where(VODSeries.id == series_id)
    )
    series = result.scalar_one_or_none()

    if not series:
        raise HTTPException(status_code=404, detail="Series not found")

    # Get episodes grouped by season
    episodes_result = await db.execute(
        select(VODEpisode).where(
            VODEpisode.series_id == series_id,
            VODEpisode.is_active.is_(True)
        ).order_by(VODEpisode.season_number, VODEpisode.episode_number)
    )
    episodes = episodes_result.scalars().all()

    # Group episodes by season
    seasons = {}
    for episode in episodes:
        season_num = str(episode.season_number)
        if season_num not in seasons:
            seasons[season_num] = []

        seasons[season_num].append({
            "id": str(episode.id),
            "episode_num": episode.episode_number,
            "title": episode.title or f"Episode {episode.episode_number}",
            "container_extension": "mp4",
            "info": {
                "air_date": "",
                "crew": "",
                "rating": "0",
                "movie_image": episode.cover_url or "",
                "duration_secs": "0",
                "duration": "00:00:00",
                "video": {},
                "audio": {},
                "bitrate": 0
            },
            "custom_sid": "",
            "added": "0",
            "season": episode.season_number,
            "direct_source": episode.stream_url
        })

    return {
        "seasons": seasons,
        "info": {
            "name": series.title,
            "title": series.title,
            "year": str(series.year) if series.year else "",
            "cover": series.cover_url or "",
            "plot": "",
            "cast": "",
            "director": "",
            "genre": series.genre or "Unknown",
            "releaseDate": str(series.year) if series.year else "",
            "last_modified": "0",
            "rating": "0",
            "rating_5based": 0,
            "backdrop_path": [],
            "youtube_trailer": "",
            "episode_run_time": "45",
            "category_id": "1"
        },
        "episodes": seasons
    }


async def get_vod_info(db: AsyncSession, vod_id: int):
    """Get detailed VOD info."""
    result = await db.execute(
        select(VODMovie).where(VODMovie.id == vod_id)
    )
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {
        "info": {
            "tmdb_id": "0",
            "name": movie.title,
            "title": movie.title,
            "year": str(movie.year) if movie.year else "",
            "o_name": movie.title,
            "cover_big": movie.cover_url or "",
            "movie_image": movie.cover_url or "",
            "releasedate": str(movie.year) if movie.year else "",
            "youtube_trailer": "",
            "director": "",
            "actors": "",
            "cast": "",
            "description": "",
            "plot": "",
            "age": "",
            "mpaa_rating": "",
            "rating": str(movie.rating) if movie.rating else "0",
            "rating_5based": round(movie.rating / 2, 1) if movie.rating else 0,
            "country": "",
            "genre": movie.genre or "Unknown",
            "backdrop_path": [],
            "duration_secs": "0",
            "duration": "00:00:00",
            "bitrate": 0,
            "video": {},
            "audio": {}
        },
        "movie_data": {
            "stream_id": movie.id,
            "name": movie.title,
            "title": movie.title,
            "added": "0",
            "category_id": "1",
            "category_name": movie.genre or "Unknown",
            "container_extension": "mp4",
            "custom_sid": "",
            "direct_source": movie.stream_url
        }
    }


@router.get("/get.php")
async def get_m3u_playlist(
    username: str = Query(...),
    password: str = Query(...),
    type: str = Query("m3u_plus"),
    output: str = Query("ts"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate M3U playlist in Xtream format.

    Compatible with IPTV clients that request playlists.
    """
    # Simple auth check
    if not username or not password:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get all enabled channels with their primary streams
    result = await db.execute(
        select(Channel, ChannelStream).join(
            ChannelStream, Channel.id == ChannelStream.channel_id
        ).where(
            Channel.enabled.is_(True),
            ChannelStream.is_active.is_(True),
            ChannelStream.priority_order == 0
        ).order_by(Channel.category, Channel.name)
    )

    # Build M3U playlist
    lines = ["#EXTM3U"]

    for channel, stream in result.all():
        # Build stream URL
        stream_url = f"{settings.BASE_URL}/stream/channel/{channel.id}.{output}"

        # Build EXTINF line
        extinf = f'#EXTINF:-1 tvg-id="{channel.epg_id or ""}" tvg-name="{channel.name}" tvg-logo="{channel.logo_url or ""}" group-title="{channel.category or "Unknown"}",{channel.name}'

        lines.append(extinf)
        lines.append(stream_url)

    playlist = "\n".join(lines)

    return {"content": playlist, "content_type": "application/x-mpegURL"}


@router.get("/xmltv.php")
async def get_epg(
    username: str = Query(...),
    password: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Return EPG in XMLTV format.

    TODO: Implement full EPG export from database.
    """
    # Simple auth check
    if not username or not password:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Return minimal XMLTV structure
    xmltv = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv generator-info-name="IPTV Stream Manager">
</tv>"""

    return {"content": xmltv, "content_type": "application/xml"}
