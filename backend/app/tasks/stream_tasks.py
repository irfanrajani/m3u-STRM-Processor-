"""Celery tasks for stream management (idle cleanup, stats snapshot)."""
from celery import shared_task
from app.services.stream_connection_manager import stream_manager
import logging

logger = logging.getLogger(__name__)

@shared_task(name="app.tasks.stream_tasks.cleanup_idle_streams")
def cleanup_idle_streams(max_idle_seconds: int = 60):
    """Celery task to cleanup idle stream proxies.

    Args:
        max_idle_seconds: Stream idle threshold for removal.
    """
    try:
        # Run async cleanup via event loop policy
        import asyncio
        asyncio.run(stream_manager.cleanup_idle_streams(max_idle_seconds=max_idle_seconds))
        stats = stream_manager.get_stats()
        logger.info("Idle stream cleanup complete active_streams=%d", stats.get("active_streams"))
        return {"active_streams": stats.get("active_streams"), "removed_idle": True}
    except Exception as e:
        logger.error("Error during idle stream cleanup: %s", e)
        return {"error": str(e)}

@shared_task(name="app.tasks.stream_tasks.snapshot_stream_stats")
def snapshot_stream_stats():
    """Return current streaming stats (for monitoring / future persistence)."""
    try:
        stats = stream_manager.get_stats()
        logger.debug("Stream stats snapshot: %s", stats)
        return stats
    except Exception as e:
        logger.error("Error snapshotting stream stats: %s", e)
        return {"error": str(e)}
