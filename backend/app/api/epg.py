"""EPG API endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class EPGRefreshRequest(BaseModel):
    epg_url: str


@router.post("/refresh")
async def refresh_epg(request: EPGRefreshRequest):
    """Trigger EPG refresh."""
    return {"status": "accepted", "message": "EPG refresh task queued"}


@router.get("/stats")
async def get_epg_stats():
    """Get EPG statistics."""
    return {
        "total_channels": 0,
        "total_programs": 0,
        "last_update": None
    }
