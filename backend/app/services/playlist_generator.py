"""Playlist generator - create merged M3U playlists."""
import logging
from pathlib import Path
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.channel import Channel, ChannelStream

logger = logging.getLogger(__name__)


class PlaylistGenerator:
    """Generate M3U playlists from merged channels."""

    def __init__(self, output_dir: str):
        """
        Initialize playlist generator.

        Args:
            output_dir: Directory for playlist output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_merged_playlist(self, db: AsyncSession, category: Optional[str] = None) -> str:
        """
        Generate merged M3U playlist.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            Path to generated playlist
        """
        try:
            # Build query
            query = select(Channel).where(Channel.enabled == True, Channel.stream_count > 0)

            if category:
                query = query.where(Channel.category == category)

            query = query.order_by(Channel.category, Channel.name)

            result = await db.execute(query)
            channels = result.scalars().all()

            logger.info(f"Generating playlist for {len(channels)} channels")

            # Generate M3U content
            m3u_lines = ["#EXTM3U"]

            for channel in channels:
                # Get best stream (first by priority_order)
                stream_result = await db.execute(
                    select(ChannelStream)
                    .where(
                        ChannelStream.channel_id == channel.id,
                        ChannelStream.is_active == True
                    )
                    .order_by(ChannelStream.priority_order)
                    .limit(1)
                )
                best_stream = stream_result.scalar_one_or_none()

                if not best_stream:
                    continue

                # Build EXTINF line
                extinf_parts = [
                    "#EXTINF:-1",
                ]

                # Add attributes
                if channel.tvg_id:
                    extinf_parts.append(f'tvg-id="{channel.tvg_id}"')

                extinf_parts.append(f'tvg-name="{channel.name}"')

                if channel.logo_url:
                    extinf_parts.append(f'tvg-logo="{channel.logo_url}"')

                if channel.category:
                    extinf_parts.append(f'group-title="{channel.category}"')

                # Add resolution if available
                if best_stream.resolution:
                    extinf_parts.append(f'group-title="{channel.category} - {best_stream.resolution}"')

                # Add channel name
                extinf_line = " ".join(extinf_parts) + f",{channel.name}"

                m3u_lines.append(extinf_line)
                m3u_lines.append(best_stream.stream_url)

            # Write to file
            filename = f"merged_playlist_{category if category else 'all'}.m3u"
            output_path = self.output_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(m3u_lines))

            logger.info(f"Generated playlist: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate playlist: {str(e)}")
            raise

    async def generate_multi_quality_playlist(self, db: AsyncSession,
                                             category: Optional[str] = None) -> str:
        """
        Generate M3U playlist with all stream qualities for each channel.

        This allows clients to choose quality or provides failover options.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            Path to generated playlist
        """
        try:
            # Build query
            query = select(Channel).where(Channel.enabled == True, Channel.stream_count > 0)

            if category:
                query = query.where(Channel.category == category)

            query = query.order_by(Channel.category, Channel.name)

            result = await db.execute(query)
            channels = result.scalars().all()

            logger.info(f"Generating multi-quality playlist for {len(channels)} channels")

            # Generate M3U content
            m3u_lines = ["#EXTM3U"]

            for channel in channels:
                # Get all active streams sorted by priority
                streams_result = await db.execute(
                    select(ChannelStream)
                    .where(
                        ChannelStream.channel_id == channel.id,
                        ChannelStream.is_active == True
                    )
                    .order_by(ChannelStream.priority_order)
                )
                streams = streams_result.scalars().all()

                if not streams:
                    continue

                for idx, stream in enumerate(streams):
                    # Build channel name with quality indicator
                    quality_suffix = ""
                    if stream.resolution:
                        quality_suffix = f" [{stream.resolution}]"
                    elif idx > 0:
                        quality_suffix = f" [Stream {idx + 1}]"

                    channel_name = f"{channel.name}{quality_suffix}"

                    # Build EXTINF line
                    extinf_parts = [
                        "#EXTINF:-1",
                    ]

                    if channel.tvg_id:
                        extinf_parts.append(f'tvg-id="{channel.tvg_id}"')

                    extinf_parts.append(f'tvg-name="{channel_name}"')

                    if channel.logo_url:
                        extinf_parts.append(f'tvg-logo="{channel.logo_url}"')

                    if channel.category:
                        category_name = channel.category
                        if stream.resolution:
                            category_name += f" - {stream.resolution}"
                        extinf_parts.append(f'group-title="{category_name}"')

                    extinf_line = " ".join(extinf_parts) + f",{channel_name}"

                    m3u_lines.append(extinf_line)
                    m3u_lines.append(stream.stream_url)

            # Write to file
            filename = f"multi_quality_{category if category else 'all'}.m3u"
            output_path = self.output_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(m3u_lines))

            logger.info(f"Generated multi-quality playlist: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate multi-quality playlist: {str(e)}")
            raise

    async def generate_category_playlists(self, db: AsyncSession) -> List[str]:
        """
        Generate separate M3U playlists for each category.

        Args:
            db: Database session

        Returns:
            List of generated playlist paths
        """
        try:
            # Get all categories
            result = await db.execute(
                select(Channel.category)
                .where(Channel.enabled == True, Channel.stream_count > 0)
                .distinct()
            )
            categories = [row[0] for row in result.all() if row[0]]

            logger.info(f"Generating playlists for {len(categories)} categories")

            playlist_paths = []

            for category in categories:
                path = await self.generate_merged_playlist(db, category)
                playlist_paths.append(path)

            logger.info(f"Generated {len(playlist_paths)} category playlists")
            return playlist_paths

        except Exception as e:
            logger.error(f"Failed to generate category playlists: {str(e)}")
            raise
