"""Provider synchronization tasks."""
import logging
from datetime import datetime
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.core.database import get_session_factory
from app.models.provider import Provider
from app.models.channel import Channel, ChannelStream
from app.services.provider_manager import ProviderManager
from app.services.channel_matcher import ChannelMatcher
from app.services.quality_analyzer import QualityAnalyzer

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_tasks.sync_provider")
def sync_provider(provider_id: int):
    """
    Sync a single provider - fetch channels and streams.

    Args:
        provider_id: Provider ID to sync
    """
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (required for Celery + async)
    nest_asyncio.apply()
    
    # Create new event loop for this task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_sync_provider_async(provider_id))
        # Allow pending cleanup tasks to complete
        loop.run_until_complete(asyncio.sleep(0.1))
    finally:
        # Shutdown async generators and close loop
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except:
            pass
        loop.close()


async def _sync_provider_async(provider_id: int):
    """Async implementation of provider sync."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            # Get provider
            result = await db.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()

            if not provider or not provider.enabled:
                logger.warning(f"Provider {provider_id} not found or disabled")
                return

            logger.info(f"Starting sync for provider: {provider.name}")

            # Initialize services
            matcher = ChannelMatcher()
            quality_analyzer = QualityAnalyzer()

            # Fetch streams based on provider type
            if provider.provider_type == 'xstream':
                await _sync_xstream_provider(db, provider, matcher, quality_analyzer)
            elif provider.provider_type == 'm3u':
                await _sync_m3u_provider(db, provider, matcher, quality_analyzer)

            # Update sync timestamp
            provider.last_sync = datetime.utcnow()
            await db.commit()

            logger.info(f"Sync completed for provider: {provider.name}")

        except Exception as e:
            logger.error(f"Error syncing provider {provider_id}: {str(e)}")
            await db.rollback()


async def _sync_xstream_provider(db, provider, matcher, quality_analyzer):
    """Sync Xstream provider."""
    xstream = ProviderManager.create_xstream_provider(
        provider.xstream_host,
        provider.xstream_username,
        provider.xstream_password,
        provider.xstream_backup_hosts
    )

    # Fetch live streams
    streams = await xstream.get_live_streams()
    logger.info(f"Fetched {len(streams)} streams from {provider.name}")

    channel_count = 0
    stream_count = 0

    for stream_data in streams:
        try:
            stream_id = stream_data.get('stream_id')
            if not stream_id:
                continue

            channel_name = stream_data.get('name', '')
            category = stream_data.get('category_name', 'Unknown')
            logo_url = stream_data.get('stream_icon')

            # Extract region and variant
            region = matcher.extract_region(channel_name)
            variant = matcher.extract_variant(channel_name)
            normalized_name = matcher.normalize_name(channel_name)

            # Find or create channel
            channel = await _find_or_create_channel(
                db, channel_name, normalized_name, category, region, variant, logo_url, matcher
            )

            if channel:
                channel_count += 1

                # Create stream URL
                stream_url = xstream.get_live_stream_url(stream_id, 'ts')

                # Analyze quality
                quality_info = await quality_analyzer.analyze_stream(stream_url, channel_name, quick_mode=True)

                # Check if stream already exists
                existing_stream = await db.execute(
                    select(ChannelStream).where(
                        ChannelStream.channel_id == channel.id,
                        ChannelStream.provider_id == provider.id,
                        ChannelStream.stream_url == stream_url
                    )
                )
                existing_stream = existing_stream.scalar_one_or_none()

                if not existing_stream:
                    # Create new stream
                    new_stream = ChannelStream(
                        channel_id=channel.id,
                        provider_id=provider.id,
                        stream_url=stream_url,
                        stream_id=str(stream_id),
                        stream_format='ts',
                        original_name=channel_name,
                        original_category=category,
                        resolution=quality_info.get('resolution'),
                        bitrate=quality_info.get('bitrate'),
                        codec=quality_info.get('codec'),
                        quality_score=quality_info.get('quality_score', 0),
                        is_active=True
                    )
                    db.add(new_stream)
                    stream_count += 1
                else:
                    # Update existing stream quality info
                    existing_stream.resolution = quality_info.get('resolution') or existing_stream.resolution
                    existing_stream.bitrate = quality_info.get('bitrate') or existing_stream.bitrate
                    existing_stream.quality_score = quality_info.get('quality_score', 0)

        except Exception as e:
            logger.error(f"Error processing stream {stream_data.get('name')}: {str(e)}")
            continue

    # Update provider stats
    provider.total_channels = channel_count
    provider.active_channels = channel_count

    await db.commit()
    logger.info(f"Synced {channel_count} channels and {stream_count} new streams")


async def _sync_m3u_provider(db, provider, matcher, quality_analyzer):
    """Sync M3U provider."""
    m3u = ProviderManager.create_m3u_provider(
        provider.m3u_url,
        provider.m3u_backup_urls
    )

    # Parse playlist
    channels_data = await m3u.parse_playlist()
    logger.info(f"Parsed {len(channels_data)} channels from {provider.name}")

    channel_count = 0
    stream_count = 0

    for channel_data in channels_data:
        try:
            channel_name = channel_data.get('name', '')
            if not channel_name:
                continue

            category = channel_data.get('group_title', 'Unknown')
            logo_url = channel_data.get('tvg_logo')
            stream_url = channel_data.get('url')
            tvg_id = channel_data.get('tvg_id')

            if not stream_url:
                continue

            # Extract region and variant
            region = matcher.extract_region(channel_name)
            variant = matcher.extract_variant(channel_name)
            normalized_name = matcher.normalize_name(channel_name)

            # Find or create channel
            channel = await _find_or_create_channel(
                db, channel_name, normalized_name, category, region, variant, logo_url, matcher
            )

            if channel:
                channel_count += 1

                # Analyze quality
                quality_info = await quality_analyzer.analyze_stream(stream_url, channel_name, quick_mode=True)

                # Check if stream already exists
                existing_stream = await db.execute(
                    select(ChannelStream).where(
                        ChannelStream.channel_id == channel.id,
                        ChannelStream.provider_id == provider.id,
                        ChannelStream.stream_url == stream_url
                    )
                )
                existing_stream = existing_stream.scalar_one_or_none()

                if not existing_stream:
                    # Create new stream
                    new_stream = ChannelStream(
                        channel_id=channel.id,
                        provider_id=provider.id,
                        stream_url=stream_url,
                        stream_format='m3u8' if '.m3u8' in stream_url else 'ts',
                        original_name=channel_name,
                        original_category=category,
                        resolution=quality_info.get('resolution'),
                        bitrate=quality_info.get('bitrate'),
                        codec=quality_info.get('codec'),
                        quality_score=quality_info.get('quality_score', 0),
                        is_active=True,
                        metadata=channel_data
                    )
                    db.add(new_stream)
                    stream_count += 1

                # Update channel EPG ID
                if tvg_id and not channel.tvg_id:
                    channel.tvg_id = tvg_id

        except Exception as e:
            logger.error(f"Error processing channel {channel_data.get('name')}: {str(e)}")
            continue

    # Update provider stats
    provider.total_channels = channel_count
    provider.active_channels = channel_count

    await db.commit()
    logger.info(f"Synced {channel_count} channels and {stream_count} new streams")


async def _find_or_create_channel(db, name, normalized_name, category, region, variant, logo_url, matcher):
    """Find existing channel or create new one."""
    # Search for existing channels
    result = await db.execute(
        select(Channel).where(Channel.normalized_name == normalized_name)
    )
    existing_channels = result.scalars().all()

    # Try to find matching channel
    matching_channel = None
    for existing_channel in existing_channels:
        if matcher.is_same_channel(
            name, existing_channel.name,
            region, existing_channel.region,
            variant, existing_channel.variant
        ):
            matching_channel = existing_channel
            break

    if matching_channel:
        # Update channel info if needed
        if not matching_channel.logo_url and logo_url:
            matching_channel.logo_url = logo_url
        matching_channel.stream_count += 1
        return matching_channel
    else:
        # Create new channel
        new_channel = Channel(
            name=name,
            normalized_name=normalized_name,
            category=category,
            region=region,
            variant=variant,
            logo_url=logo_url,
            enabled=True,
            stream_count=0
        )
        db.add(new_channel)
        await db.flush()  # Get ID
        return new_channel


@celery_app.task(name="app.tasks.sync_tasks.sync_all_providers")
def sync_all_providers():
    """Sync all enabled providers."""
    import asyncio
    import nest_asyncio
    
    # Allow nested event loops (required for Celery + async)
    nest_asyncio.apply()
    
    # Create new event loop for this task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_sync_all_providers_async())
    finally:
        loop.close()


async def _sync_all_providers_async():
    """Async implementation of sync all providers."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        result = await db.execute(
            select(Provider).where(Provider.enabled.is_(True))
        )
        providers = result.scalars().all()

        logger.info(f"Starting sync for {len(providers)} providers")

        for provider in providers:
            try:
                await _sync_provider_async(provider.id)
            except Exception as e:
                logger.error(f"Failed to sync provider {provider.name}: {str(e)}")
