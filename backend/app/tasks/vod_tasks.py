"""VOD management tasks."""
import logging
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.core.database import get_session_factory
from app.core.config import settings
from app.models.provider import Provider
from app.models.vod import VODMovie, VODSeries, VODEpisode
from app.services.provider_manager import ProviderManager
from app.services.vod_manager import VODManager

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.vod_tasks.sync_vod_content")
def sync_vod_content(provider_id: int):
    """Sync VOD content from a provider."""
    import asyncio
    asyncio.run(_sync_vod_content_async(provider_id))


async def _sync_vod_content_async(provider_id: int):
    """Async implementation of VOD sync."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            # Get provider
            result = await db.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()

            if not provider or not provider.enabled:
                logger.warning(f"Provider {provider_id} not found or disabled")
                return

            if provider.provider_type != 'xstream':
                logger.info(f"VOD sync only supports Xstream providers. Skipping {provider.name}")
                return

            logger.info(f"Starting VOD sync for provider: {provider.name}")

            # Create Xstream client
            xstream = ProviderManager.create_xstream_provider(
                provider.xstream_host,
                provider.xstream_username,
                provider.xstream_password,
                provider.xstream_backup_hosts
            )

            # Sync movies
            await _sync_movies(db, provider, xstream)

            # Sync series
            await _sync_series(db, provider, xstream)

            await db.commit()
            logger.info(f"VOD sync completed for provider: {provider.name}")

        except Exception as e:
            logger.error(f"VOD sync failed for provider {provider_id}: {str(e)}")
            await db.rollback()


async def _sync_movies(db, provider, xstream):
    """Sync VOD movies."""
    try:
        # Get VOD streams
        vod_streams = await xstream.get_vod_streams()
        logger.info(f"Fetched {len(vod_streams)} VOD streams")

        movie_count = 0

        for vod_data in vod_streams:
            try:
                stream_id = vod_data.get('stream_id')
                if not stream_id:
                    continue

                title = vod_data.get('name', '')
                # Extract year from title if present
                year = None
                if '(' in title and ')' in title:
                    try:
                        year_str = title[title.rfind('(') + 1:title.rfind(')')]
                        if year_str.isdigit() and len(year_str) == 4:
                            year = int(year_str)
                    except Exception as e:
                        logger.debug(f"Failed to parse year from title '{title}': {e}")

                normalized_title = title.lower().strip()

                # Check if movie already exists
                existing_movie = await db.execute(
                    select(VODMovie).where(
                        VODMovie.provider_id == provider.id,
                        VODMovie.normalized_title == normalized_title
                    )
                )
                existing_movie = existing_movie.scalar_one_or_none()

                if existing_movie:
                    continue

                # Create new movie
                stream_url = xstream.get_vod_stream_url(stream_id, 'mp4')

                new_movie = VODMovie(
                    provider_id=provider.id,
                    title=title,
                    normalized_title=normalized_title,
                    year=year,
                    stream_url=stream_url,
                    stream_id=str(stream_id),
                    cover_url=vod_data.get('stream_icon'),
                    genre=vod_data.get('category_name', 'Unknown'),
                    is_active=True
                )

                db.add(new_movie)
                movie_count += 1

            except Exception as e:
                logger.error(f"Error processing movie {vod_data.get('name')}: {str(e)}")
                continue

        provider.total_vod_movies = movie_count
        logger.info(f"Synced {movie_count} movies")

    except Exception as e:
        logger.error(f"Error syncing movies: {str(e)}")


async def _sync_series(db, provider, xstream):
    """Sync VOD series."""
    try:
        # Get series
        series_list = await xstream.get_series()
        logger.info(f"Fetched {len(series_list)} series")

        series_count = 0
        episode_count = 0

        for series_data in series_list:
            try:
                series_id = series_data.get('series_id')
                if not series_id:
                    continue

                title = series_data.get('name', '')
                normalized_title = title.lower().strip()

                # Check if series already exists
                existing_series = await db.execute(
                    select(VODSeries).where(
                        VODSeries.provider_id == provider.id,
                        VODSeries.normalized_title == normalized_title
                    )
                )
                existing_series = existing_series.scalar_one_or_none()

                if existing_series:
                    continue

                # Get series info with episodes
                series_info = await xstream.get_series_info(series_id)
                if not series_info:
                    continue

                # Create new series
                new_series = VODSeries(
                    provider_id=provider.id,
                    title=title,
                    normalized_title=normalized_title,
                    series_id=str(series_id),
                    genre=series_data.get('category_name', 'Unknown'),
                    cover_url=series_data.get('cover'),
                    is_active=True
                )

                db.add(new_series)
                await db.flush()  # Get series ID

                # Add episodes
                episodes_data = series_info.get('episodes', {})
                season_set = set()

                for season_num, season_episodes in episodes_data.items():
                    try:
                        season_number = int(season_num)
                        season_set.add(season_number)

                        for episode_data in season_episodes:
                            episode_num = int(episode_data.get('episode_num', 0))
                            episode_id = episode_data.get('id')

                            if not episode_id:
                                continue

                            stream_url = xstream.get_series_stream_url(episode_id, 'mp4')

                            new_episode = VODEpisode(
                                series_id=new_series.id,
                                title=episode_data.get('title'),
                                season_number=season_number,
                                episode_number=episode_num,
                                episode_id=str(episode_id),
                                stream_url=stream_url,
                                cover_url=episode_data.get('info', {}).get('movie_image'),
                                is_active=True
                            )

                            db.add(new_episode)
                            episode_count += 1

                    except Exception as e:
                        logger.error(f"Error processing season {season_num}: {str(e)}")
                        continue

                new_series.season_count = len(season_set)
                new_series.episode_count = episode_count
                series_count += 1

            except Exception as e:
                logger.error(f"Error processing series {series_data.get('name')}: {str(e)}")
                continue

        provider.total_vod_series = series_count
        logger.info(f"Synced {series_count} series with {episode_count} episodes")

    except Exception as e:
        logger.error(f"Error syncing series: {str(e)}")


@celery_app.task(name="app.tasks.vod_tasks.generate_strm_files")
def generate_strm_files():
    """Generate .strm files for all VOD content."""
    import asyncio
    asyncio.run(_generate_strm_files_async())


async def _generate_strm_files_async():
    """Async implementation of STRM generation."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        try:
            logger.info("Starting STRM file generation")

            vod_manager = VODManager(settings.STRM_DIR)

            # Generate movie STRM files
            result = await db.execute(
                select(VODMovie).where(VODMovie.is_active.is_(True))
            )
            movies = result.scalars().all()

            logger.info(f"Generating STRM files for {len(movies)} movies")

            for movie in movies:
                try:
                    movie_dict = {
                        "title": movie.title,
                        "year": movie.year,
                        "stream_url": movie.stream_url,
                        "genre": movie.genre
                    }

                    strm_path = vod_manager.generate_movie_strm(movie_dict)
                    if strm_path:
                        movie.strm_file_path = strm_path

                except Exception as e:
                    logger.error(f"Error generating STRM for movie {movie.title}: {str(e)}")

            # Generate series STRM files
            result = await db.execute(
                select(VODSeries).where(VODSeries.is_active.is_(True))
            )
            series_list = result.scalars().all()

            logger.info(f"Generating STRM files for {len(series_list)} series")

            for series in series_list:
                try:
                    # Get episodes
                    episodes_result = await db.execute(
                        select(VODEpisode).where(
                            VODEpisode.series_id == series.id,
                            VODEpisode.is_active.is_(True)
                        )
                    )
                    episodes = episodes_result.scalars().all()

                    series_dict = {
                        "title": series.title,
                        "year": None,
                        "genre": series.genre
                    }

                    for episode in episodes:
                        episode_dict = {
                            "season_number": episode.season_number,
                            "episode_number": episode.episode_number,
                            "title": episode.title,
                            "stream_url": episode.stream_url
                        }

                        strm_path = vod_manager.generate_episode_strm(series_dict, episode_dict)
                        if strm_path:
                            episode.strm_file_path = strm_path

                except Exception as e:
                    logger.error(f"Error generating STRM for series {series.title}: {str(e)}")

            await db.commit()
            stats = vod_manager.get_stats()
            logger.info(f"STRM generation completed. Movies: {stats['total_movies']}, Episodes: {stats['total_episodes']}")

        except Exception as e:
            logger.error(f"STRM generation failed: {str(e)}")
            await db.rollback()
