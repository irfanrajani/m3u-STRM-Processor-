"""
HLS Stream Proxy - Advanced M3U8 Handler
Provides RAM buffering, segment caching, and intelligent variant selection
Improves playback quality and reduces stuttering for HLS streams
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict
from datetime import datetime, timedelta
import aiohttp
import m3u8
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class HLSStreamProxy:
    """Advanced HLS/M3U8 stream handler with buffering"""
    
    def __init__(
        self,
        playlist_url: str,
        channel_id: int,
        buffer_size_mb: int = 10,
        max_segments_cached: int = 50
    ):
        self.playlist_url = playlist_url
        self.channel_id = channel_id
        self.buffer_size = buffer_size_mb * 1024 * 1024
        self.max_segments_cached = max_segments_cached
        self.segment_cache: Dict[str, bytes] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.bytes_served = 0
        self.created_at = datetime.utcnow()
        
    async def get_stream(self) -> AsyncGenerator[bytes, None]:
        """
        Proxy HLS stream with intelligent buffering
        Handles both master playlists and variant playlists
        """
        try:
            # Parse the playlist
            async with aiohttp.ClientSession() as session:
                async with session.get(self.playlist_url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Failed to fetch playlist: HTTP {resp.status}")
                    
                    playlist_content = await resp.text()
                    playlist = m3u8.loads(playlist_content, uri=self.playlist_url)
            
            # Check if this is a master playlist (multiple variants)
            if playlist.is_variant:
                # Select best quality variant
                variant = self._select_best_variant(playlist)
                if not variant:
                    raise Exception("No suitable variant found in master playlist")
                
                logger.info(
                    f"Selected variant for channel {self.channel_id}: "
                    f"bandwidth={variant.stream_info.bandwidth}, "
                    f"resolution={variant.stream_info.resolution}"
                )
                
                # Load the variant playlist
                variant_url = urljoin(self.playlist_url, variant.uri)
                async with aiohttp.ClientSession() as session:
                    async with session.get(variant_url) as resp:
                        variant_content = await resp.text()
                        variant_playlist = m3u8.loads(variant_content, uri=variant_url)
            else:
                # This is already a media playlist
                variant_playlist = playlist
            
            # Stream the segments
            async for chunk in self._stream_segments(variant_playlist):
                yield chunk
                
        except Exception as e:
            logger.error(f"HLS proxy error for channel {self.channel_id}: {e}")
            raise
    
    def _select_best_variant(self, playlist: m3u8.M3U8) -> Optional[m3u8.Playlist]:
        """Select the best quality variant based on bandwidth"""
        if not playlist.playlists:
            return None
        
        # Filter out audio-only streams
        video_variants = [
            p for p in playlist.playlists
            if p.stream_info.bandwidth and (
                not hasattr(p.stream_info, 'video') or p.stream_info.video != 'none'
            )
        ]
        
        if not video_variants:
            video_variants = playlist.playlists
        
        # Sort by bandwidth and select highest
        sorted_variants = sorted(
            video_variants,
            key=lambda p: p.stream_info.bandwidth or 0,
            reverse=True
        )
        
        return sorted_variants[0]
    
    async def _stream_segments(
        self,
        playlist: m3u8.M3U8
    ) -> AsyncGenerator[bytes, None]:
        """Stream segments with caching and buffering"""
        
        if not playlist.segments:
            raise Exception("No segments found in playlist")
        
        logger.info(f"Streaming {len(playlist.segments)} segments for channel {self.channel_id}")
        
        for segment in playlist.segments:
            # Build absolute URL for segment
            segment_url = urljoin(playlist.base_uri, segment.uri)
            
            # Fetch segment (with caching)
            segment_data = await self._fetch_segment_with_cache(segment_url)
            
            # Yield in chunks for smooth streaming
            chunk_size = 8192
            for i in range(0, len(segment_data), chunk_size):
                chunk = segment_data[i:i + chunk_size]
                self.bytes_served += len(chunk)
                yield chunk
    
    async def _fetch_segment_with_cache(self, segment_url: str) -> bytes:
        """
        Fetch segment with RAM caching
        Uses LRU eviction when cache is full
        """
        # Check cache first
        if segment_url in self.segment_cache:
            self.cache_hits += 1
            logger.debug(f"Cache hit for segment: {segment_url}")
            return self.segment_cache[segment_url]
        
        # Cache miss - fetch from source
        self.cache_misses += 1
        logger.debug(f"Cache miss for segment: {segment_url}")
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(segment_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to fetch segment: HTTP {resp.status}")
                
                data = await resp.read()
        
        # Add to cache with LRU eviction
        if len(self.segment_cache) >= self.max_segments_cached:
            # Remove oldest entry (first key in dict)
            oldest_key = next(iter(self.segment_cache))
            del self.segment_cache[oldest_key]
            logger.debug(f"Evicted segment from cache: {oldest_key}")
        
        self.segment_cache[segment_url] = data
        return data
    
    def get_stats(self) -> dict:
        """Get proxy statistics"""
        cache_hit_rate = 0
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            cache_hit_rate = round((self.cache_hits / total_requests) * 100, 1)
        
        return {
            'channel_id': self.channel_id,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate_percent': cache_hit_rate,
            'cached_segments': len(self.segment_cache),
            'bytes_served': self.bytes_served,
            'mb_served': round(self.bytes_served / 1024 / 1024, 2),
            'uptime_seconds': (datetime.utcnow() - self.created_at).total_seconds()
        }


async def detect_stream_type(url: str) -> str:
    """
    Detect if URL is HLS, MPEG-TS, or other format
    Returns: 'hls', 'mpegts', or 'unknown'
    """
    url_lower = url.lower()
    
    # Check file extension
    if url_lower.endswith('.m3u8') or url_lower.endswith('.m3u'):
        return 'hls'
    
    if url_lower.endswith('.ts') or url_lower.endswith('.mpg'):
        return 'mpegts'
    
    # Check content-type header
    try:
        timeout = aiohttp.ClientTimeout(total=5, connect=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(url, allow_redirects=True) as resp:
                content_type = resp.headers.get('content-type', '').lower()
                
                if 'mpegurl' in content_type or 'vnd.apple.mpegurl' in content_type:
                    return 'hls'
                
                if 'mp2t' in content_type or 'mpeg' in content_type:
                    return 'mpegts'
    except Exception as e:
        logger.debug(f"Failed to detect stream type for {url}: {e}")
    
    return 'unknown'
