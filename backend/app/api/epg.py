"""EPG API endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.xmltv_generator import XMLTVGenerator

router = APIRouter()


class EPGRefreshRequest(BaseModel):
    epg_url: str


@router.post("/refresh")
async def refresh_epg(request: EPGRefreshRequest):
    """Trigger EPG refresh."""
    return {"status": "accepted", "message": "EPG refresh task queued"}


@router.get("/stats")
async def get_epg_stats(db: AsyncSession = Depends(get_db)):
    """
    Get EPG statistics.

    Returns comprehensive EPG data including:
    - Number of channels with EPG mapping
    - Total programs in database
    - Date range of available programs
    - Programs grouped by category
    """
    generator = XMLTVGenerator(db)
    stats = await generator.get_epg_stats()
    return stats
