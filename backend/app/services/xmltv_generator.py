"""XMLTV EPG Generator Service."""
from datetime import datetime, timedelta
from typing import Optional, List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.channel import Channel
from app.models.epg import EPGProgram


class XMLTVGenerator:
    """Generate XMLTV format EPG from database."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    async def generate_xmltv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        channel_ids: Optional[List[int]] = None
    ) -> str:
        """
        Generate complete XMLTV document.

        Args:
            start_date: Start date for programs (default: now)
            end_date: End date for programs (default: now + 7 days)
            channel_ids: List of channel IDs to include (default: all enabled)

        Returns:
            XMLTV formatted XML string
        """
        # Set default date range
        if start_date is None:
            start_date = datetime.utcnow()
        if end_date is None:
            end_date = start_date + timedelta(days=7)

        # Create root TV element
        tv = Element('tv')
        tv.set('generator-info-name', 'M3U STRM Processor')
        tv.set('generator-info-url', 'https://github.com/irfanrajani/m3u-STRM-Processor-')

        # Query channels
        channel_query = self.db.query(Channel).filter(Channel.is_enabled == True)
        if channel_ids:
            channel_query = channel_query.filter(Channel.id.in_(channel_ids))

        channels = channel_query.all()

        # Add channel elements
        for channel in channels:
            if channel.epg_channel_id:  # Only include channels with EPG mapping
                self._create_channel_element(tv, channel)

        # Query programs
        program_query = self.db.query(EPGProgram).filter(
            and_(
                EPGProgram.start_time >= start_date,
                EPGProgram.end_time <= end_date
            )
        )

        # Filter by channel IDs if provided
        if channel_ids:
            program_query = program_query.join(Channel).filter(Channel.id.in_(channel_ids))

        programs = program_query.order_by(EPGProgram.start_time).all()

        # Add programme elements
        for program in programs:
            self._create_programme_element(tv, program)

        # Convert to pretty XML string
        xml_str = tostring(tv, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ', encoding='UTF-8').decode('utf-8')

    def _create_channel_element(self, parent: Element, channel: Channel) -> None:
        """
        Create XMLTV channel element.

        Format:
        <channel id="espn.us">
          <display-name>ESPN</display-name>
          <display-name>ESPN HD</display-name>
          <icon src="http://example.com/espn.png" />
        </channel>
        """
        channel_elem = SubElement(parent, 'channel')
        channel_elem.set('id', channel.epg_channel_id)

        # Add display names
        display_name = SubElement(channel_elem, 'display-name')
        display_name.text = channel.name

        # Add canonical name if different
        if channel.canonical_name and channel.canonical_name != channel.name:
            display_name2 = SubElement(channel_elem, 'display-name')
            display_name2.text = channel.canonical_name

        # Add icon if available
        if channel.logo_url:
            icon = SubElement(channel_elem, 'icon')
            icon.set('src', channel.logo_url)

    def _create_programme_element(self, parent: Element, program: EPGProgram) -> None:
        """
        Create XMLTV programme element.

        Format:
        <programme start="20250113120000 +0000" stop="20250113130000 +0000" channel="espn.us">
          <title lang="en">SportsCenter</title>
          <sub-title lang="en">Morning Edition</sub-title>
          <desc lang="en">Latest sports news and highlights</desc>
          <category lang="en">Sports</category>
          <episode-num system="xmltv_ns">0.4.</episode-num>
          <icon src="http://example.com/program.jpg" />
          <rating system="MPAA">
            <value>TV-PG</value>
          </rating>
        </programme>
        """
        # Get channel EPG ID
        channel = self.db.query(Channel).filter(Channel.id == program.channel_id).first()
        if not channel or not channel.epg_channel_id:
            return

        programme = SubElement(parent, 'programme')
        programme.set('start', self._format_xmltv_time(program.start_time))
        programme.set('stop', self._format_xmltv_time(program.end_time))
        programme.set('channel', channel.epg_channel_id)

        # Title (required)
        if program.title:
            title = SubElement(programme, 'title')
            title.set('lang', 'en')
            title.text = program.title

        # Subtitle
        if program.subtitle:
            subtitle = SubElement(programme, 'sub-title')
            subtitle.set('lang', 'en')
            subtitle.text = program.subtitle

        # Description
        if program.description:
            desc = SubElement(programme, 'desc')
            desc.set('lang', 'en')
            desc.text = program.description

        # Category
        if program.category:
            category = SubElement(programme, 'category')
            category.set('lang', 'en')
            category.text = program.category

        # Episode numbering (if available)
        if program.season_number or program.episode_number:
            episode_num = SubElement(programme, 'episode-num')
            episode_num.set('system', 'xmltv_ns')
            episode_num.text = self._format_episode_xmltv(
                program.season_number,
                program.episode_number
            )

        # Icon
        if program.icon_url:
            icon = SubElement(programme, 'icon')
            icon.set('src', program.icon_url)

        # Rating
        if program.rating:
            rating = SubElement(programme, 'rating')
            rating.set('system', 'MPAA')
            value = SubElement(rating, 'value')
            value.text = program.rating

    def _format_xmltv_time(self, dt: datetime) -> str:
        """
        Format datetime to XMLTV time format.

        XMLTV format: YYYYMMDDHHmmss +0000
        Example: 20250113120000 +0000
        """
        return dt.strftime('%Y%m%d%H%M%S +0000')

    def _format_episode_xmltv(
        self,
        season: Optional[int],
        episode: Optional[int]
    ) -> str:
        """
        Format episode numbering to XMLTV format.

        XMLTV format: season.episode.part
        - All numbers are 0-indexed
        - Missing values are left empty

        Examples:
            S01E05 -> "0.4." (season 0, episode 4)
            S02E10 -> "1.9." (season 1, episode 9)
            Episode 5 only -> ".4."
        """
        season_str = str(season - 1) if season else ''
        episode_str = str(episode - 1) if episode else ''
        return f"{season_str}.{episode_str}."

    def _parse_episode_to_xmltv(self, episode_str: str) -> Optional[str]:
        """
        Parse episode string (S01E05) to XMLTV format.

        Args:
            episode_str: Episode string like "S01E05" or "1x05"

        Returns:
            XMLTV format string like "0.4." or None
        """
        if not episode_str:
            return None

        # Try S01E05 format
        match = re.match(r'[Ss](\d+)[Ee](\d+)', episode_str)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return self._format_episode_xmltv(season, episode)

        # Try 1x05 format
        match = re.match(r'(\d+)[xX](\d+)', episode_str)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return self._format_episode_xmltv(season, episode)

        return None

    async def generate_xmltv_streaming(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        channel_ids: Optional[List[int]] = None,
        chunk_size: int = 100
    ):
        """
        Generate XMLTV in streaming chunks for memory efficiency.

        Yields XML chunks instead of building entire document in memory.
        Useful for very large EPG datasets.

        Args:
            start_date: Start date for programs
            end_date: End date for programs
            channel_ids: List of channel IDs to include
            chunk_size: Number of programmes per chunk

        Yields:
            XML string chunks
        """
        # Set default date range
        if start_date is None:
            start_date = datetime.utcnow()
        if end_date is None:
            end_date = start_date + timedelta(days=7)

        # Yield XML header
        yield '<?xml version="1.0" encoding="UTF-8"?>\n'
        yield '<tv generator-info-name="M3U STRM Processor" '
        yield 'generator-info-url="https://github.com/irfanrajani/m3u-STRM-Processor-">\n'

        # Query and yield channels
        channel_query = self.db.query(Channel).filter(Channel.is_enabled == True)
        if channel_ids:
            channel_query = channel_query.filter(Channel.id.in_(channel_ids))

        channels = channel_query.all()
        for channel in channels:
            if channel.epg_channel_id:
                tv = Element('tv')
                self._create_channel_element(tv, channel)
                channel_xml = tostring(tv[0], encoding='utf-8').decode('utf-8')
                yield f"  {channel_xml}\n"

        # Query programs in chunks
        program_query = self.db.query(EPGProgram).filter(
            and_(
                EPGProgram.start_time >= start_date,
                EPGProgram.end_time <= end_date
            )
        ).order_by(EPGProgram.start_time)

        if channel_ids:
            program_query = program_query.join(Channel).filter(Channel.id.in_(channel_ids))

        total_programs = program_query.count()

        for offset in range(0, total_programs, chunk_size):
            programs = program_query.limit(chunk_size).offset(offset).all()

            for program in programs:
                tv = Element('tv')
                self._create_programme_element(tv, program)
                if len(tv) > 0:  # Only if programme was created
                    programme_xml = tostring(tv[0], encoding='utf-8').decode('utf-8')
                    yield f"  {programme_xml}\n"

        # Yield closing tag
        yield '</tv>\n'

    async def get_epg_stats(self) -> dict:
        """
        Get EPG statistics.

        Returns:
            Dictionary with EPG stats
        """
        # Count channels with EPG mapping
        channels_with_epg = self.db.query(Channel).filter(
            and_(
                Channel.is_enabled == True,
                Channel.epg_channel_id.isnot(None)
            )
        ).count()

        # Count total programs
        total_programs = self.db.query(EPGProgram).count()

        # Get date range of available programs
        earliest = self.db.query(EPGProgram.start_time).order_by(
            EPGProgram.start_time.asc()
        ).first()
        latest = self.db.query(EPGProgram.end_time).order_by(
            EPGProgram.end_time.desc()
        ).first()

        # Count programs by category
        from sqlalchemy import func
        category_counts = dict(
            self.db.query(
                EPGProgram.category,
                func.count(EPGProgram.id)
            ).filter(
                EPGProgram.category.isnot(None)
            ).group_by(
                EPGProgram.category
            ).all()
        )

        return {
            "channels_with_epg": channels_with_epg,
            "total_programs": total_programs,
            "earliest_program": earliest[0].isoformat() if earliest and earliest[0] else None,
            "latest_program": latest[0].isoformat() if latest and latest[0] else None,
            "programs_by_category": category_counts,
            "date_range_days": (
                (latest[0] - earliest[0]).days
                if earliest and latest and earliest[0] and latest[0]
                else 0
            )
        }
