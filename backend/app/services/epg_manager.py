"""EPG (Electronic Program Guide) manager."""
import asyncio
import gzip
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import httpx
import xmltodict

logger = logging.getLogger(__name__)


class EPGManager:
    """Manage EPG data from XMLTV format."""

    def __init__(self, epg_dir: str):
        """
        Initialize EPG manager.

        Args:
            epg_dir: Directory to store EPG files
        """
        self.epg_dir = Path(epg_dir)
        self.epg_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.epg_dir / "epg_cache.xml"
        self.cache_file_gz = self.epg_dir / "epg_cache.xml.gz"
        self.channels = {}
        self.programs = []

    async def fetch_epg(self, epg_url: str) -> bool:
        """
        Fetch EPG data from URL.

        Args:
            epg_url: EPG XML URL

        Returns:
            True if successful
        """
        try:
            logger.info(f"Fetching EPG from {epg_url}")

            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                response = await client.get(epg_url)
                response.raise_for_status()

                content = response.content

                # Check if content is gzipped
                if epg_url.endswith('.gz') or content[:2] == b'\x1f\x8b':
                    # Save gzipped content
                    with open(self.cache_file_gz, 'wb') as f:
                        f.write(content)

                    # Decompress
                    content = gzip.decompress(content)

                # Save uncompressed XML
                with open(self.cache_file, 'wb') as f:
                    f.write(content)

                logger.info("EPG fetched successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to fetch EPG: {str(e)}")
            return False

    async def parse_epg(self) -> bool:
        """
        Parse EPG XML file.

        Returns:
            True if successful
        """
        try:
            if not self.cache_file.exists():
                logger.error("EPG cache file not found")
                return False

            logger.info("Parsing EPG data")

            # Read XML file
            with open(self.cache_file, 'rb') as f:
                content = f.read()

            # Parse XML
            data = xmltodict.parse(content)

            if 'tv' not in data:
                logger.error("Invalid EPG format")
                return False

            tv_data = data['tv']

            # Parse channels
            channels = tv_data.get('channel', [])
            if not isinstance(channels, list):
                channels = [channels]

            self.channels = {}
            for channel in channels:
                channel_id = channel.get('@id')
                if channel_id:
                    self.channels[channel_id] = {
                        'id': channel_id,
                        'display_name': self._get_display_name(channel),
                        'icon': self._get_icon(channel),
                        'url': channel.get('url')
                    }

            # Parse programmes
            programmes = tv_data.get('programme', [])
            if not isinstance(programmes, list):
                programmes = [programmes]

            self.programs = []
            for prog in programmes:
                try:
                    program = self._parse_programme(prog)
                    if program:
                        self.programs.append(program)
                except Exception as e:
                    logger.debug(f"Failed to parse programme: {str(e)}")
                    continue

            logger.info(f"Parsed {len(self.channels)} channels and {len(self.programs)} programmes")
            return True

        except Exception as e:
            logger.error(f"Failed to parse EPG: {str(e)}")
            return False

    def _get_display_name(self, channel: Dict) -> str:
        """Extract display name from channel data."""
        display_name = channel.get('display-name', '')

        if isinstance(display_name, list):
            # Take first non-empty name
            for name in display_name:
                if isinstance(name, dict):
                    name = name.get('#text', '')
                if name:
                    return str(name)
            return ''
        elif isinstance(display_name, dict):
            return str(display_name.get('#text', ''))
        else:
            return str(display_name)

    def _get_icon(self, channel: Dict) -> Optional[str]:
        """Extract icon URL from channel data."""
        icon = channel.get('icon')

        if isinstance(icon, dict):
            return icon.get('@src')
        elif isinstance(icon, list) and len(icon) > 0:
            if isinstance(icon[0], dict):
                return icon[0].get('@src')

        return None

    def _parse_programme(self, prog: Dict) -> Optional[Dict]:
        """Parse a single programme entry."""
        channel_id = prog.get('@channel')
        start = prog.get('@start')
        stop = prog.get('@stop')

        if not channel_id or not start or not stop:
            return None

        # Parse timestamps (format: YYYYMMDDHHmmss +0000)
        start_time = self._parse_timestamp(start)
        end_time = self._parse_timestamp(stop)

        if not start_time or not end_time:
            return None

        # Extract title
        title = prog.get('title', '')
        if isinstance(title, dict):
            title = title.get('#text', '')
        elif isinstance(title, list):
            title = title[0].get('#text', '') if title else ''

        # Extract subtitle
        subtitle = prog.get('sub-title', '')
        if isinstance(subtitle, dict):
            subtitle = subtitle.get('#text', '')
        elif isinstance(subtitle, list):
            subtitle = subtitle[0].get('#text', '') if subtitle else ''

        # Extract description
        desc = prog.get('desc', '')
        if isinstance(desc, dict):
            desc = desc.get('#text', '')
        elif isinstance(desc, list):
            desc = desc[0].get('#text', '') if desc else ''

        # Extract category
        category = prog.get('category', '')
        if isinstance(category, dict):
            category = category.get('#text', '')
        elif isinstance(category, list):
            category = category[0].get('#text', '') if category else ''

        # Extract episode info
        episode = prog.get('episode-num', '')
        if isinstance(episode, dict):
            episode = episode.get('#text', '')
        elif isinstance(episode, list):
            episode = episode[0].get('#text', '') if episode else ''

        # Extract icon
        icon = None
        icon_data = prog.get('icon')
        if isinstance(icon_data, dict):
            icon = icon_data.get('@src')
        elif isinstance(icon_data, list) and len(icon_data) > 0:
            icon = icon_data[0].get('@src')

        return {
            'channel_id': channel_id,
            'start_time': start_time,
            'end_time': end_time,
            'title': str(title),
            'subtitle': str(subtitle) if subtitle else None,
            'description': str(desc) if desc else None,
            'category': str(category) if category else None,
            'episode': str(episode) if episode else None,
            'icon': icon
        }

    def _parse_timestamp(self, timestamp: str) -> Optional[datetime]:
        """Parse XMLTV timestamp."""
        try:
            # Remove timezone for simplicity (format: YYYYMMDDHHmmss +0000)
            timestamp = timestamp.split()[0]
            return datetime.strptime(timestamp, '%Y%m%d%H%M%S')
        except Exception as e:
            logger.debug(f"Failed to parse timestamp {timestamp}: {str(e)}")
            return None

    def get_current_program(self, channel_id: str) -> Optional[Dict]:
        """
        Get currently airing program for a channel.

        Args:
            channel_id: EPG channel ID

        Returns:
            Program dictionary or None
        """
        now = datetime.utcnow()

        for program in self.programs:
            if program['channel_id'] == channel_id:
                if program['start_time'] <= now <= program['end_time']:
                    return program

        return None

    def get_upcoming_programs(self, channel_id: str, hours: int = 24) -> List[Dict]:
        """
        Get upcoming programs for a channel.

        Args:
            channel_id: EPG channel ID
            hours: Number of hours to look ahead

        Returns:
            List of programs
        """
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)

        upcoming = []
        for program in self.programs:
            if program['channel_id'] == channel_id:
                if now <= program['start_time'] <= end_time:
                    upcoming.append(program)

        # Sort by start time
        upcoming.sort(key=lambda x: x['start_time'])
        return upcoming

    def get_channel_by_name(self, name: str) -> Optional[Dict]:
        """
        Find EPG channel by name (fuzzy match).

        Args:
            name: Channel name to search

        Returns:
            Channel dictionary or None
        """
        name_lower = name.lower()

        # Exact match first
        for channel_id, channel in self.channels.items():
            if channel['display_name'].lower() == name_lower:
                return channel

        # Partial match
        for channel_id, channel in self.channels.items():
            if name_lower in channel['display_name'].lower():
                return channel

        return None

    def get_stats(self) -> Dict:
        """
        Get EPG statistics.

        Returns:
            Dictionary with stats
        """
        now = datetime.utcnow()

        # Count current programs
        current_programs = sum(
            1 for p in self.programs
            if p['start_time'] <= now <= p['end_time']
        )

        # Get time range
        if self.programs:
            start_times = [p['start_time'] for p in self.programs]
            end_times = [p['end_time'] for p in self.programs]
            earliest = min(start_times)
            latest = max(end_times)
        else:
            earliest = None
            latest = None

        return {
            'total_channels': len(self.channels),
            'total_programs': len(self.programs),
            'current_programs': current_programs,
            'earliest_program': earliest,
            'latest_program': latest,
            'cache_file': str(self.cache_file),
            'cache_exists': self.cache_file.exists()
        }

    async def refresh_epg(self, epg_url: str) -> bool:
        """
        Refresh EPG data from URL.

        Args:
            epg_url: EPG XML URL

        Returns:
            True if successful
        """
        success = await self.fetch_epg(epg_url)
        if success:
            success = await self.parse_epg()
        return success
