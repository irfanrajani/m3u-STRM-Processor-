"""Health check tasks."""
import logging
from datetime import datetime
from sqlalchemy import select, update
from app.tasks.celery_app import celery_app
from app.core.database import get_session_factory
from app.models.channel import ChannelStream, Channel
from app.services.health_checker import StreamHealthChecker

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.health_tasks.run_health_check")
def run_health_check():
    """Run health check on all active streams."""
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (required for Celery + async)
    nest_asyncio.apply()
    
    # Create new event loop for this task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run_health_check_async())
    finally:
        loop.close()


async def _run_health_check_async():
    """Async implementation of health check."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            logger.info("Starting health check for all streams")

            # Get all active streams
            result = await db.execute(
                select(ChannelStream).where(ChannelStream.is_active.is_(True))
            )
            streams = result.scalars().all()

            logger.info(f"Checking {len(streams)} active streams")

            # Initialize health checker
            checker = StreamHealthChecker(timeout=10, max_concurrent=50)

            # Prepare stream data for batch check
            stream_data = [
                {"id": stream.id, "stream_url": stream.stream_url}
                for stream in streams
            ]

            # Run health checks in batches
            batch_size = 500
            total_checked = 0
            total_alive = 0
            total_dead = 0

            for i in range(0, len(stream_data), batch_size):
                batch = stream_data[i:i + batch_size]
                logger.info(f"Checking batch {i // batch_size + 1} ({len(batch)} streams)")

                results = await checker.check_streams_batch(batch)

                # Update database with results
                for result in results:
                    stream_id = result['stream_id']
                    is_alive = result['is_alive']
                    response_time = result['response_time']
                    error = result['error']

                    # Find stream
                    stream_result = await db.execute(
                        select(ChannelStream).where(ChannelStream.id == stream_id)
                    )
                    stream = stream_result.scalar_one_or_none()

                    if stream:
                        stream.last_check = datetime.utcnow()
                        stream.response_time = response_time

                        if is_alive:
                            stream.consecutive_failures = 0
                            stream.last_success = datetime.utcnow()
                            total_alive += 1
                        else:
                            stream.consecutive_failures += 1
                            stream.last_failure = datetime.utcnow()
                            stream.failure_reason = error
                            total_dead += 1

                            # Mark as inactive after 3 consecutive failures
                            if stream.consecutive_failures >= 3:
                                stream.is_active = False
                                logger.warning(f"Stream {stream_id} marked as inactive after 3 failures")

                        total_checked += 1

                # Commit batch
                await db.commit()
                logger.info(f"Batch completed. Alive: {total_alive}, Dead: {total_dead}")

            # Update channel stream counts
            await _update_channel_stream_counts(db)

            logger.info(f"Health check completed. Total: {total_checked}, Alive: {total_alive}, Dead: {total_dead}")

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            await db.rollback()


async def _update_channel_stream_counts(db):
    """Update stream counts for all channels using optimized single query."""
    from sqlalchemy import func
    
    # Get all channels with their active stream counts in a single query
    result = await db.execute(
        select(
            ChannelStream.channel_id,
            func.count(ChannelStream.id).label('active_count')
        )
        .where(ChannelStream.is_active.is_(True))
        .group_by(ChannelStream.channel_id)
    )
    
    stream_counts = {row.channel_id: row.active_count for row in result.all()}
    
    # Get all channels
    result = await db.execute(select(Channel))
    channels = result.scalars().all()
    
    for channel in channels:
        channel.stream_count = stream_counts.get(channel.id, 0)
        
        # Re-prioritize streams for this channel
        result = await db.execute(
            select(ChannelStream)
            .where(
                ChannelStream.channel_id == channel.id,
                ChannelStream.is_active.is_(True)
            )
            .order_by(ChannelStream.quality_score.desc())
        )
        active_streams = result.scalars().all()
        
        # Bulk update priority
        for idx, stream in enumerate(active_streams):
            stream.priority_order = idx
    
    await db.commit()


@celery_app.task(name="app.tasks.health_tasks.check_provider_streams")
def check_provider_streams(provider_id: int):
    """Run health check for a specific provider's streams."""
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (required for Celery + async)
    nest_asyncio.apply()
    
    # Create new event loop for this task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_check_provider_streams_async(provider_id))
    finally:
        loop.close()


async def _check_provider_streams_async(provider_id: int):
    """Async implementation of provider-specific health check."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            logger.info(f"Starting health check for provider {provider_id}")

            # Get provider's active streams
            result = await db.execute(
                select(ChannelStream).where(
                    ChannelStream.provider_id == provider_id,
                    ChannelStream.is_active.is_(True)
                )
            )
            streams = result.scalars().all()

            logger.info(f"Checking {len(streams)} streams for provider {provider_id}")

            # Initialize health checker
            checker = StreamHealthChecker(timeout=10, max_concurrent=50)

            # Prepare stream data
            stream_data = [
                {"id": stream.id, "stream_url": stream.stream_url}
                for stream in streams
            ]

            # Run health checks
            results = await checker.check_streams_batch(stream_data)

            # Update database
            for result in results:
                stream_id = result['stream_id']
                is_alive = result['is_alive']
                response_time = result['response_time']
                error = result['error']

                stream_result = await db.execute(
                    select(ChannelStream).where(ChannelStream.id == stream_id)
                )
                stream = stream_result.scalar_one_or_none()

                if stream:
                    stream.last_check = datetime.utcnow()
                    stream.response_time = response_time

                    if is_alive:
                        stream.consecutive_failures = 0
                        stream.last_success = datetime.utcnow()
                    else:
                        stream.consecutive_failures += 1
                        stream.last_failure = datetime.utcnow()
                        stream.failure_reason = error

                        if stream.consecutive_failures >= 3:
                            stream.is_active = False

            await db.commit()
            logger.info(f"Health check completed for provider {provider_id}")

        except Exception as e:
            logger.error(f"Provider health check failed: {str(e)}")
            await db.rollback()
