"""Bandwidth throttling using token bucket algorithm."""
import asyncio
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BandwidthBucket:
    """Token bucket for rate limiting bandwidth."""

    capacity: int  # bytes per second
    tokens: float  # current available tokens
    last_refill: float  # timestamp of last refill

    def refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        new_tokens = elapsed * self.capacity
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    async def consume(self, bytes_count: int):
        """
        Consume tokens. If not enough, wait until refilled.

        Args:
            bytes_count: Number of bytes to consume
        """
        self.refill()

        while self.tokens < bytes_count:
            # Calculate wait time needed
            deficit = bytes_count - self.tokens
            wait_time = deficit / self.capacity

            # Wait for tokens to refill
            logger.debug(f"Throttling: waiting {wait_time:.3f}s for {deficit} bytes")
            await asyncio.sleep(wait_time)
            self.refill()

        # Consume tokens
        self.tokens -= bytes_count


class BandwidthLimiter:
    """Manage bandwidth limiting for streams."""

    def __init__(self, global_limit_mbps: Optional[float] = None):
        """
        Initialize bandwidth limiter.

        Args:
            global_limit_mbps: Global bandwidth limit in Mbps (None = unlimited)
        """
        self.global_limit_bytes = int(global_limit_mbps * 1_000_000 / 8) if global_limit_mbps else None
        self.global_bucket: Optional[BandwidthBucket] = None
        self.stream_buckets: Dict[str, BandwidthBucket] = {}
        self.stream_limits: Dict[str, int] = {}  # stream_id -> bytes/sec

        if self.global_limit_bytes:
            self.global_bucket = BandwidthBucket(
                capacity=self.global_limit_bytes,
                tokens=self.global_limit_bytes,
                last_refill=time.time()
            )
            logger.info(f"Global bandwidth limit: {global_limit_mbps} Mbps ({self.global_limit_bytes} bytes/sec)")

    def set_stream_limit(self, stream_id: str, limit_mbps: float):
        """
        Set bandwidth limit for a specific stream.

        Args:
            stream_id: Stream identifier
            limit_mbps: Bandwidth limit in Mbps
        """
        limit_bytes = int(limit_mbps * 1_000_000 / 8)
        self.stream_limits[stream_id] = limit_bytes

        self.stream_buckets[stream_id] = BandwidthBucket(
            capacity=limit_bytes,
            tokens=limit_bytes,
            last_refill=time.time()
        )
        logger.info(f"Stream {stream_id} bandwidth limit: {limit_mbps} Mbps ({limit_bytes} bytes/sec)")

    def remove_stream_limit(self, stream_id: str):
        """Remove bandwidth limit for a stream."""
        self.stream_limits.pop(stream_id, None)
        self.stream_buckets.pop(stream_id, None)
        logger.info(f"Removed bandwidth limit for stream {stream_id}")

    async def consume(self, stream_id: str, bytes_count: int):
        """
        Consume bandwidth tokens.

        Args:
            stream_id: Stream identifier
            bytes_count: Number of bytes to consume
        """
        # Apply stream-specific limit if configured
        if stream_id in self.stream_buckets:
            await self.stream_buckets[stream_id].consume(bytes_count)

        # Apply global limit if configured
        if self.global_bucket:
            await self.global_bucket.consume(bytes_count)

    async def throttled_read(self, stream_id: str, reader_func, chunk_size: int = 8192):
        """
        Read from a stream with bandwidth throttling.

        Args:
            stream_id: Stream identifier
            reader_func: Async function that reads and returns bytes
            chunk_size: Size of chunks to read

        Yields:
            Bytes chunks with throttling applied
        """
        while True:
            chunk = await reader_func(chunk_size)
            if not chunk:
                break

            # Consume bandwidth before yielding chunk
            await self.consume(stream_id, len(chunk))
            yield chunk

    def get_stats(self) -> Dict:
        """
        Get current bandwidth limiter statistics.

        Returns:
            Dictionary with stats
        """
        stats = {
            "global_limit_mbps": (self.global_limit_bytes * 8 / 1_000_000) if self.global_limit_bytes else None,
            "global_tokens_available": self.global_bucket.tokens if self.global_bucket else None,
            "stream_limits": {},
            "total_streams": len(self.stream_buckets)
        }

        for stream_id, bucket in self.stream_buckets.items():
            bucket.refill()
            stats["stream_limits"][stream_id] = {
                "limit_mbps": bucket.capacity * 8 / 1_000_000,
                "tokens_available": bucket.tokens,
                "utilization_pct": round((1 - bucket.tokens / bucket.capacity) * 100, 1)
            }

        return stats

    def set_global_limit(self, limit_mbps: Optional[float]):
        """
        Update global bandwidth limit.

        Args:
            limit_mbps: Bandwidth limit in Mbps (None = unlimited)
        """
        if limit_mbps is None:
            self.global_bucket = None
            self.global_limit_bytes = None
            logger.info("Global bandwidth limit removed")
        else:
            self.global_limit_bytes = int(limit_mbps * 1_000_000 / 8)
            self.global_bucket = BandwidthBucket(
                capacity=self.global_limit_bytes,
                tokens=self.global_limit_bytes,
                last_refill=time.time()
            )
            logger.info(f"Global bandwidth limit updated: {limit_mbps} Mbps")


class BandwidthMonitor:
    """Monitor actual bandwidth usage."""

    def __init__(self):
        """Initialize bandwidth monitor."""
        self.stream_stats: Dict[str, Dict] = {}
        self.start_time = time.time()
        self.lock = asyncio.Lock()

    async def record_transfer(self, stream_id: str, bytes_transferred: int):
        """
        Record bandwidth usage for a stream.

        Args:
            stream_id: Stream identifier
            bytes_transferred: Number of bytes transferred
        """
        async with self.lock:
            if stream_id not in self.stream_stats:
                self.stream_stats[stream_id] = {
                    "total_bytes": 0,
                    "start_time": time.time(),
                    "last_update": time.time()
                }

            stats = self.stream_stats[stream_id]
            stats["total_bytes"] += bytes_transferred
            stats["last_update"] = time.time()

    def get_stream_bandwidth(self, stream_id: str) -> Optional[float]:
        """
        Get current bandwidth usage for a stream in Mbps.

        Args:
            stream_id: Stream identifier

        Returns:
            Bandwidth in Mbps or None if not found
        """
        if stream_id not in self.stream_stats:
            return None

        stats = self.stream_stats[stream_id]
        elapsed = time.time() - stats["start_time"]

        if elapsed == 0:
            return 0.0

        bytes_per_sec = stats["total_bytes"] / elapsed
        mbps = bytes_per_sec * 8 / 1_000_000

        return round(mbps, 2)

    def get_total_bandwidth(self) -> float:
        """
        Get total bandwidth usage across all streams in Mbps.

        Returns:
            Total bandwidth in Mbps
        """
        total_bytes = sum(stats["total_bytes"] for stats in self.stream_stats.values())
        elapsed = time.time() - self.start_time

        if elapsed == 0:
            return 0.0

        bytes_per_sec = total_bytes / elapsed
        mbps = bytes_per_sec * 8 / 1_000_000

        return round(mbps, 2)

    async def reset_stream(self, stream_id: str):
        """Reset stats for a stream."""
        async with self.lock:
            self.stream_stats.pop(stream_id, None)

    async def get_stats(self) -> Dict:
        """Get all bandwidth statistics."""
        async with self.lock:
            return {
                "total_bandwidth_mbps": self.get_total_bandwidth(),
                "active_streams": len(self.stream_stats),
                "streams": {
                    stream_id: {
                        "bandwidth_mbps": self.get_stream_bandwidth(stream_id),
                        "total_mb": round(stats["total_bytes"] / 1_000_000, 2),
                        "duration_sec": round(time.time() - stats["start_time"], 1)
                    }
                    for stream_id, stats in self.stream_stats.items()
                }
            }


# Global instances
bandwidth_limiter = BandwidthLimiter()
bandwidth_monitor = BandwidthMonitor()
