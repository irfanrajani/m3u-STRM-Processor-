"""EPG parser and auto-matcher - Parse XMLTV EPG and match with channels."""
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
import httpx
from datetime import datetime
from app.services.channel_matcher import ChannelMatcher

logger = logging.getLogger(__name__)


class EPGParser:
    """Parse XMLTV EPG files and auto-match channels."""

    def __init__(self):
        """Initialize EPG parser."""
        self.channel_matcher = ChannelMatcher()
        self.epg_channels: Dict[str, Dict] = {}  # tvg-id -> channel data

    async def fetch_epg(self, epg_url: str) -> Optional[str]:
        """
        Fetch EPG XML from URL.

        Args:
            epg_url: URL to EPG XML file

        Returns:
            XML content or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(epg_url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch EPG from {epg_url}: {str(e)}")
            return None

    def parse_xmltv(self, xml_content: str) -> Dict[str, Dict]:
        """
        Parse XMLTV format EPG.

        Args:
            xml_content: XML content string

        Returns:
            Dictionary mapping tvg-id to channel data
        """
        channels = {}

        try:
            root = ET.fromstring(xml_content)

            # Parse channel elements
            for channel_elem in root.findall('channel'):
                tvg_id = channel_elem.get('id')
                if not tvg_id:
                    continue

                # Get display name (EPG uses this as canonical name)
                display_name_elem = channel_elem.find('display-name')
                display_name = display_name_elem.text if display_name_elem is not None else ''

                # Get icon if available
                icon_elem = channel_elem.find('icon')
                icon_url = icon_elem.get('src') if icon_elem is not None else None

                # Store channel data
                channels[tvg_id] = {
                    'tvg_id': tvg_id,
                    'epg_name': display_name,
                    'icon_url': icon_url,
                    'channel_elem': channel_elem  # Store for future use
                }

            self.epg_channels = channels
            logger.info(f"Parsed {len(channels)} channels from EPG")

            return channels

        except ET.ParseError as e:
            logger.error(f"XML parse error: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error parsing XMLTV: {str(e)}")
            return {}

    def match_channel_with_epg(self, channel_name: str, tvg_id: Optional[str] = None,
                               tvg_name: Optional[str] = None) -> Optional[Dict]:
        """
        Match a channel with EPG data.

        Matching priority:
        1. Exact tvg-id match
        2. Fuzzy match on tvg-name
        3. Fuzzy match on channel name

        Args:
            channel_name: Channel name from M3U
            tvg_id: tvg-id from M3U (if available)
            tvg_name: tvg-name from M3U (if available)

        Returns:
            Matched EPG channel data or None
        """
        if not self.epg_channels:
            return None

        # Priority 1: Exact tvg-id match
        if tvg_id and tvg_id in self.epg_channels:
            logger.debug(f"Matched channel '{channel_name}' by tvg-id: {tvg_id}")
            return self.epg_channels[tvg_id]

        # Priority 2: Fuzzy match on tvg-name
        if tvg_name:
            for epg_channel in self.epg_channels.values():
                epg_name = epg_channel.get('epg_name', '')
                similarity = self.channel_matcher.calculate_similarity(tvg_name, epg_name)
                if similarity >= self.channel_matcher.fuzzy_threshold:
                    logger.debug(f"Matched channel '{channel_name}' by tvg-name (similarity: {similarity}): {epg_name}")
                    return epg_channel

        # Priority 3: Fuzzy match on channel name
        best_match = None
        best_score = 0

        for epg_channel in self.epg_channels.values():
            epg_name = epg_channel.get('epg_name', '')
            similarity = self.channel_matcher.calculate_similarity(channel_name, epg_name)

            if similarity > best_score and similarity >= self.channel_matcher.fuzzy_threshold:
                best_score = similarity
                best_match = epg_channel

        if best_match:
            logger.debug(f"Matched channel '{channel_name}' by name (similarity: {best_score}): {best_match.get('epg_name')}")

        return best_match

    def get_canonical_name(self, channel_name: str, tvg_id: Optional[str] = None,
                           tvg_name: Optional[str] = None) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Get canonical channel name from EPG if available.

        Args:
            channel_name: Original channel name
            tvg_id: tvg-id if available
            tvg_name: tvg-name if available

        Returns:
            Tuple of (canonical_name, matched_tvg_id, icon_url)
        """
        epg_match = self.match_channel_with_epg(channel_name, tvg_id, tvg_name)

        if epg_match:
            return (
                epg_match.get('epg_name', channel_name),
                epg_match.get('tvg_id'),
                epg_match.get('icon_url')
            )

        # No match - return original
        return (channel_name, tvg_id, None)

    async def auto_match_channels(self, channels: List[Dict]) -> List[Dict]:
        """
        Auto-match a list of channels with EPG data.

        Updates each channel dict with:
        - canonical_name: Name from EPG
        - matched_tvg_id: Matched tvg-id
        - epg_icon: Icon URL from EPG

        Args:
            channels: List of channel dictionaries

        Returns:
            Updated list of channels with EPG matches
        """
        if not self.epg_channels:
            logger.warning("No EPG data loaded for auto-matching")
            return channels

        matched_count = 0

        for channel in channels:
            channel_name = channel.get('name', '')
            tvg_id = channel.get('tvg_id') or channel.get('tvg-id')
            tvg_name = channel.get('tvg_name') or channel.get('tvg-name')

            canonical_name, matched_tvg_id, icon_url = self.get_canonical_name(
                channel_name, tvg_id, tvg_name
            )

            # Update channel with EPG data
            if canonical_name != channel_name:
                channel['canonical_name'] = canonical_name
                channel['original_name'] = channel_name
                matched_count += 1

            if matched_tvg_id:
                channel['matched_tvg_id'] = matched_tvg_id

            if icon_url and not channel.get('logo_url'):
                channel['epg_icon'] = icon_url

        logger.info(f"Auto-matched {matched_count}/{len(channels)} channels with EPG data")
        return channels

    def get_epg_stats(self) -> Dict:
        """
        Get statistics about loaded EPG data.

        Returns:
            Dictionary with EPG stats
        """
        return {
            'total_epg_channels': len(self.epg_channels),
            'epg_loaded': len(self.epg_channels) > 0
        }
