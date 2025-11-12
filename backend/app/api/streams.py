"""Streaming stats and control endpoints."""
from fastapi import APIRouter, HTTPException
from app.services.stream_connection_manager import stream_manager

router = APIRouter(prefix="/api/streams", tags=["Streams"])


@router.get("/stats")
async def get_stream_stats():
    """Return aggregate streaming statistics."""
    return stream_manager.get_stats()


@router.get("/active")
async def get_active_streams():
    """List active streams with details."""
    stats = stream_manager.get_stats()
    return {
        "count": stats["active_streams"],
        "total_clients": stats["total_clients"],
        "streams": stats["streams"],
    }


@router.post("/cleanup")
async def force_cleanup():
    """Force immediate cleanup of all idle streams."""
    await stream_manager.cleanup_idle_streams(max_idle_seconds=0)
    return {"status": "success"}
