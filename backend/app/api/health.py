"""Health check API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.channel import ChannelStream

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
async def get_health_status(db: AsyncSession = Depends(get_db)):
    """Get health check status."""
    # Get total streams
    total_streams = await db.scalar(select(func.count(ChannelStream.id)))

    # Get active streams
    active_streams = await db.scalar(
        select(func.count(ChannelStream.id)).where(ChannelStream.is_active.is_(True))
    )

    # Get failed streams (inactive)
    failed_streams = await db.scalar(
        select(func.count(ChannelStream.id)).where(ChannelStream.is_active.is_(False))
    )

    # Get last check time from most recent stream update
    last_check_result = await db.execute(
        select(ChannelStream.last_check)
        .where(ChannelStream.last_check.isnot(None))
        .order_by(ChannelStream.last_check.desc())
        .limit(1)
    )
    last_check_row = last_check_result.first()
    last_check = last_check_row[0] if last_check_row else None

    return {
        "last_check": last_check.isoformat() if last_check else None,
        "total_streams": total_streams or 0,
        "active_streams": active_streams or 0,
        "failed_streams": failed_streams or 0
    }
