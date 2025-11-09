"""Provider manager service - handles Xstream API and M3U playlist parsing."""
import httpx
import m3u_ipytv
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class XstreamProvider:
    """Xstream Codes API client."""

    def __init__(self, host: str, username: str, password: str, backup_hosts: Optional[List[str]] = None):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.backup_hosts = backup_hosts or []
        self.timeout = 30

    async def _make_request(self, endpoint: str, hosts: Optional[List[str]] = None) -> Optional[Dict]:
        """Make request to Xstream API with failover to backup hosts."""
        all_hosts = [self.host] + (hosts or self.backup_hosts)

        for host in all_hosts:
            try:
                url = f"{host.rstrip('/')}/player_api.php"
                params = {
                    "username": self.username,
                    "password": self.password,
                    "action": endpoint
                }

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()

            except Exception as e:
                logger.warning(f"Failed to fetch from {host}: {str(e)}")
                continue

        logger.error(f"All hosts failed for endpoint: {endpoint}")
        return None

    async def get_live_categories(self) -> List[Dict]:
        """Get live TV categories."""
        result = await self._make_request("get_live_categories")
        return result if result else []

    async def get_live_streams(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get live TV streams, optionally filtered by category."""
        endpoint = "get_live_streams"
        if category_id:
            endpoint = f"get_live_streams&category_id={category_id}"

        result = await self._make_request(endpoint)
        return result if result else []

    async def get_vod_categories(self) -> List[Dict]:
        """Get VOD categories."""
        result = await self._make_request("get_vod_categories")
        return result if result else []

    async def get_vod_streams(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get VOD streams, optionally filtered by category."""
        endpoint = "get_vod_streams"
        if category_id:
            endpoint = f"get_vod_streams&category_id={category_id}"

        result = await self._make_request(endpoint)
        return result if result else []

    async def get_vod_info(self, vod_id: int) -> Optional[Dict]:
        """Get detailed VOD info."""
        result = await self._make_request(f"get_vod_info&vod_id={vod_id}")
        return result

    async def get_series_categories(self) -> List[Dict]:
        """Get series categories."""
        result = await self._make_request("get_series_categories")
        return result if result else []

    async def get_series(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get series, optionally filtered by category."""
        endpoint = "get_series"
        if category_id:
            endpoint = f"get_series&category_id={category_id}"

        result = await self._make_request(endpoint)
        return result if result else []

    async def get_series_info(self, series_id: int) -> Optional[Dict]:
        """Get detailed series info including episodes."""
        result = await self._make_request(f"get_series_info&series_id={series_id}")
        return result

    def get_live_stream_url(self, stream_id: str, extension: str = "ts") -> str:
        """Get live stream URL."""
        return f"{self.host}/live/{self.username}/{self.password}/{stream_id}.{extension}"

    def get_vod_stream_url(self, stream_id: str, extension: str = "mp4") -> str:
        """Get VOD stream URL."""
        return f"{self.host}/movie/{self.username}/{self.password}/{stream_id}.{extension}"

    def get_series_stream_url(self, stream_id: str, extension: str = "mp4") -> str:
        """Get series episode stream URL."""
        return f"{self.host}/series/{self.username}/{self.password}/{stream_id}.{extension}"


class M3UProvider:
    """M3U/M3U8 playlist parser."""

    def __init__(self, url: str, backup_urls: Optional[List[str]] = None):
        self.url = url
        self.backup_urls = backup_urls or []
        self.timeout = 30

    async def fetch_playlist(self) -> Optional[str]:
        """Fetch M3U playlist with failover to backup URLs."""
        all_urls = [self.url] + self.backup_urls

        for url in all_urls:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text

            except Exception as e:
                logger.warning(f"Failed to fetch M3U from {url}: {str(e)}")
                continue

        logger.error("All M3U URLs failed")
        return None

    async def parse_playlist(self) -> List[Dict]:
        """Parse M3U playlist and extract channel information."""
        content = await self.fetch_playlist()
        if not content:
            return []

        try:
            playlist = m3u_ipytv.parse(content)
            channels = []

            for item in playlist:
                channel = {
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "tvg_id": item.get("tvg-id", ""),
                    "tvg_name": item.get("tvg-name", ""),
                    "tvg_logo": item.get("tvg-logo", ""),
                    "group_title": item.get("group-title", ""),
                    "tvg_country": item.get("tvg-country", ""),
                    "tvg_language": item.get("tvg-language", ""),
                    "metadata": item  # Store all original metadata
                }
                channels.append(channel)

            return channels

        except Exception as e:
            logger.error(f"Failed to parse M3U playlist: {str(e)}")
            return []


class ProviderManager:
    """Unified provider manager for both Xstream and M3U providers."""

    @staticmethod
    def create_xstream_provider(host: str, username: str, password: str,
                                 backup_hosts: Optional[List[str]] = None) -> XstreamProvider:
        """Create Xstream provider instance."""
        return XstreamProvider(host, username, password, backup_hosts)

    @staticmethod
    def create_m3u_provider(url: str, backup_urls: Optional[List[str]] = None) -> M3UProvider:
        """Create M3U provider instance."""
        return M3UProvider(url, backup_urls)

    @staticmethod
    async def test_xstream_connection(host: str, username: str, password: str) -> bool:
        """Test Xstream API connection."""
        try:
            provider = XstreamProvider(host, username, password)
            result = await provider._make_request("get_live_categories")
            return result is not None
        except Exception as e:
            logger.error(f"Xstream connection test failed: {str(e)}")
            return False

    @staticmethod
    async def test_m3u_connection(url: str) -> bool:
        """Test M3U URL connection."""
        try:
            provider = M3UProvider(url)
            content = await provider.fetch_playlist()
            return content is not None and len(content) > 0
        except Exception as e:
            logger.error(f"M3U connection test failed: {str(e)}")
            return False
