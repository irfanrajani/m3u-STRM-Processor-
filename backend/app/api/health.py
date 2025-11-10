"""Health check API endpoints."""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/check")
async def trigger_health_check():
    """Trigger health check for all streams."""
    from app.tasks.health_tasks import health_check_all_streams
    try:
        task = health_check_all_streams.delay()
        return {"status": "accepted", "message": "Health check task queued", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue health check: {str(e)}")


@router.get("/status")
async def get_health_status():
    """Get health check status."""
    return {
        "last_check": None,
        "total_streams": 0,
        "active_streams": 0,
        "failed_streams": 0
    }
