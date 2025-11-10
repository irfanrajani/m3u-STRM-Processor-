"""HDHomeRun emulator - Makes Emby/Plex think we're a real TV tuner."""
import logging
from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.channel import Channel, ChannelStream
from app.core.config import settings

logger = logging.getLogger(__name__)


class HDHomeRunEmulator:
    """Emulate SiliconDust HDHomeRun device for Emby/Plex compatibility."""

    def __init__(self, device_id: str = "IPTV-MGR", tuner_count: int = 4):
        """
        Initialize HDHomeRun emulator.

        Args:
            device_id: Unique device ID
            tuner_count: Number of virtual tuners (concurrent streams)
        """
        self.device_id = device_id
        self.tuner_count = tuner_count
        self.friendly_name = "IPTV Stream Manager"
        self.manufacturer = "IPTV-SM"
        self.model = "HDTC-2US"
        self.firmware_name = "hdhomerun3_atsc"
        self.firmware_version = "20190621"

    def get_discover_data(self, base_url: str) -> Dict:
        """
        Generate /discover.json response.

        Args:
            base_url: Base URL for this server

        Returns:
            Discovery data dictionary
        """
        return {
            "FriendlyName": self.friendly_name,
            "Manufacturer": self.manufacturer,
            "ModelNumber": self.model,
            "FirmwareName": self.firmware_name,
            "FirmwareVersion": self.firmware_version,
            "DeviceID": self.device_id,
            "DeviceAuth": "iptv",
            "BaseURL": base_url,
            "LineupURL": f"{base_url}/lineup.json",
            "TunerCount": self.tuner_count
        }

    def get_lineup_status(self) -> Dict:
        """
        Generate /lineup_status.json response.

        Returns:
            Lineup status dictionary
        """
        return {
            "ScanInProgress": 0,
            "ScanPossible": 1,
            "Source": "Cable",
            "SourceList": ["Cable", "Antenna"]
        }

    async def get_lineup(self, db: AsyncSession, base_url: str,
                        proxy_mode: str = "direct") -> List[Dict]:
        """
        Generate /lineup.json response with channel lineup.

        Args:
            db: Database session
            base_url: Base URL for stream endpoints
            proxy_mode: 'direct' or 'proxy'

        Returns:
            List of channel dictionaries
        """
        try:
            # Get all enabled channels with active streams
            result = await db.execute(
                select(Channel)
                .where(Channel.enabled == True, Channel.stream_count > 0)
                .order_by(Channel.category, Channel.name)
            )
            channels = result.scalars().all()

            lineup = []
            channel_number = 1

            for channel in channels:
                # Get best stream
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

                # Determine stream URL based on mode
                if proxy_mode == "proxy":
                    stream_url = f"{base_url}/auto/v{channel.id}"
                else:
                    # Direct mode - redirect to original stream
                    stream_url = best_stream.stream_url

                lineup_entry = {
                    "GuideNumber": str(channel_number),
                    "GuideName": channel.name,
                    "URL": stream_url
                }

                # Add optional fields if available
                if channel.logo_url:
                    lineup_entry["HD"] = 1 if "hd" in channel.name.lower() or "1080" in str(best_stream.resolution or "").lower() else 0

                lineup.append(lineup_entry)
                channel_number += 1

            logger.info(f"Generated HDHomeRun lineup with {len(lineup)} channels")
            return lineup

        except Exception as e:
            logger.error(f"Error generating lineup: {str(e)}")
            return []

    async def get_stream_url(self, db: AsyncSession, channel_id: int,
                            proxy_mode: str = "direct") -> Optional[str]:
        """
        Get stream URL for a channel.

        Args:
            db: Database session
            channel_id: Channel ID
            proxy_mode: 'direct' or 'proxy'

        Returns:
            Stream URL or None
        """
        try:
            # Get channel
            result = await db.execute(
                select(Channel).where(Channel.id == channel_id)
            )
            channel = result.scalar_one_or_none()

            if not channel:
                return None

            # Get best active stream
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
                return None

            return best_stream.stream_url

        except Exception as e:
            logger.error(f"Error getting stream URL for channel {channel_id}: {str(e)}")
            return None

    def get_device_xml(self, base_url: str) -> str:
        """
        Generate device.xml for SSDP discovery.

        Args:
            base_url: Base URL for this server

        Returns:
            XML string
        """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <device>
        <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
        <friendlyName>{self.friendly_name}</friendlyName>
        <manufacturer>{self.manufacturer}</manufacturer>
        <modelName>{self.model}</modelName>
        <modelNumber>{self.firmware_version}</modelNumber>
        <serialNumber>{self.device_id}</serialNumber>
        <UDN>uuid:iptv-sm-{self.device_id}</UDN>
    </device>
</root>"""
