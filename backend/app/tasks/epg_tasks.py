"""EPG management tasks."""
import logging
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.provider import Provider
from app.services.epg_manager import EPGManager

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.epg_tasks.refresh_epg")
def refresh_epg(provider_id: int):
    """Refresh EPG for a specific provider."""
    import asyncio
    asyncio.run(_refresh_epg_async(provider_id))


async def _refresh_epg_async(provider_id: int):
    """Async implementation of EPG refresh."""
    async with AsyncSessionLocal() as db:
        try:
            # Get provider
            result = await db.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()

            if not provider or not provider.enabled or not provider.epg_url:
                logger.warning(f"Provider {provider_id} not found, disabled, or no EPG URL")
                return

            logger.info(f"Refreshing EPG for provider: {provider.name}")

            # Initialize EPG manager
            epg_manager = EPGManager(settings.EPG_DIR)

            # Fetch and parse EPG
            success = await epg_manager.refresh_epg(provider.epg_url)

            if success:
                logger.info(f"EPG refreshed successfully for {provider.name}")
            else:
                logger.error(f"Failed to refresh EPG for {provider.name}")

        except Exception as e:
            logger.error(f"EPG refresh failed for provider {provider_id}: {str(e)}")


@celery_app.task(name="app.tasks.epg_tasks.refresh_all_epg")
def refresh_all_epg():
    """Refresh EPG for all providers with EPG URLs."""
    import asyncio
    asyncio.run(_refresh_all_epg_async())


async def _refresh_all_epg_async():
    """Async implementation of refresh all EPG."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Provider).where(
                    Provider.enabled.is_(True),
                    Provider.epg_url != None
                )
            )
            providers = result.scalars().all()

            logger.info(f"Refreshing EPG for {len(providers)} providers")

            for provider in providers:
                try:
                    await _refresh_epg_async(provider.id)
                except Exception as e:
                    logger.error(f"Failed to refresh EPG for {provider.name}: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to refresh all EPG: {str(e)}")
