"""Health check API endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/check")
async def trigger_health_check():
    """Trigger health check for all streams."""
    return {"status": "accepted", "message": "Health check task queued"}


@router.get("/status")
async def get_health_status():
    """Get health check status."""
    return {
        "last_check": None,
        "total_streams": 0,
        "active_streams": 0,
        "failed_streams": 0
    }
