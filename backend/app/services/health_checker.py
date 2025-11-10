"""Stream health checker - test stream availability and performance."""
import asyncio
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class HealthCheckResult:
    """Health check result."""

    def __init__(self, is_alive: bool, response_time: Optional[float] = None,
                 status_code: Optional[int] = None, error: Optional[str] = None):
        self.is_alive = is_alive
        self.response_time = response_time  # in milliseconds
        self.status_code = status_code
        self.error = error
        self.timestamp = datetime.utcnow()


class StreamHealthChecker:
    """Check stream health and availability."""

    def __init__(self, timeout: int = 10, max_concurrent: int = 50):
        """
        Initialize health checker.

        Args:
            timeout: Timeout for health checks in seconds
            max_concurrent: Maximum concurrent health checks
        """
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def check_stream(self, stream_url: str, method: str = "head") -> HealthCheckResult:
        """
        Check if a stream is alive.

        Args:
            stream_url: Stream URL to check
            method: HTTP method to use ("head" or "get")

        Returns:
            HealthCheckResult
        """
        async with self.semaphore:
            start_time = time.time()

            try:
                from app.core.config import settings
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=settings.VERIFY_SSL  # Configurable - IPTV streams often have SSL issues
                ) as client:
                    # Try HEAD request first (faster)
                    if method == "head":
                        response = await client.head(stream_url)
                    else:
                        # For GET, only read first few bytes
                        response = await client.get(stream_url, timeout=self.timeout)

                    response_time = (time.time() - start_time) * 1000  # Convert to ms

                    # Check if response is successful
                    if response.status_code in [200, 206, 302, 301]:
                        return HealthCheckResult(
                            is_alive=True,
                            response_time=response_time,
                            status_code=response.status_code
                        )
                    else:
                        return HealthCheckResult(
                            is_alive=False,
                            response_time=response_time,
                            status_code=response.status_code,
                            error=f"HTTP {response.status_code}"
                        )

            except httpx.TimeoutException:
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    is_alive=False,
                    response_time=response_time,
                    error="Timeout"
                )

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return HealthCheckResult(
                    is_alive=False,
                    response_time=response_time,
                    error=str(e)
                )

    async def check_streams_batch(self, streams: List[Dict]) -> List[Dict]:
        """
        Check multiple streams concurrently.

        Args:
            streams: List of streams (must have 'id' and 'stream_url' keys)

        Returns:
            List of results with health check data
        """
        tasks = []

        for stream in streams:
            stream_id = stream.get("id")
            stream_url = stream.get("stream_url")

            if not stream_url:
                continue

            task = self._check_and_record(stream_id, stream_url)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed with exception: {str(result)}")
                continue
            if result:
                valid_results.append(result)

        return valid_results

    async def _check_and_record(self, stream_id: int, stream_url: str) -> Optional[Dict]:
        """
        Check stream and return result dictionary.

        Args:
            stream_id: Stream ID
            stream_url: Stream URL

        Returns:
            Dictionary with health check result
        """
        try:
            # Try HEAD first, fallback to GET if it fails
            result = await self.check_stream(stream_url, method="head")

            # If HEAD failed with client error, try GET
            if not result.is_alive and result.status_code in [405, 501]:
                result = await self.check_stream(stream_url, method="get")

            return {
                "stream_id": stream_id,
                "is_alive": result.is_alive,
                "response_time": result.response_time,
                "status_code": result.status_code,
                "error": result.error,
                "checked_at": result.timestamp
            }

        except Exception as e:
            logger.error(f"Error checking stream {stream_id}: {str(e)}")
            return None

    async def quick_check(self, stream_url: str, timeout: int = 5) -> bool:
        """
        Quick check if stream is accessible (used for testing).

        Args:
            stream_url: Stream URL
            timeout: Timeout in seconds

        Returns:
            True if stream is accessible
        """
        try:
            from app.core.config import settings
            async with httpx.AsyncClient(timeout=timeout, verify=settings.VERIFY_SSL) as client:
                response = await client.head(stream_url, follow_redirects=True)
                return response.status_code in [200, 206, 302, 301]
        except Exception as e:
            logger.debug(f"Quick check failed for {stream_url}: {str(e)}")
            return False

    def calculate_health_score(self, consecutive_failures: int,
                              last_response_time: Optional[float],
                              uptime_percentage: Optional[float] = None) -> int:
        """
        Calculate overall health score for a stream.

        Args:
            consecutive_failures: Number of consecutive failures
            last_response_time: Last response time in ms
            uptime_percentage: Historical uptime percentage (0-100)

        Returns:
            Health score (0-100, higher is better)
        """
        score = 100

        # Penalty for consecutive failures (exponential)
        if consecutive_failures > 0:
            score -= min(50, consecutive_failures * 10)

        # Penalty for slow response time
        if last_response_time:
            if last_response_time > 5000:  # > 5 seconds
                score -= 30
            elif last_response_time > 3000:  # > 3 seconds
                score -= 20
            elif last_response_time > 1000:  # > 1 second
                score -= 10

        # Factor in historical uptime
        if uptime_percentage is not None:
            uptime_factor = uptime_percentage / 100
            score = int(score * uptime_factor)

        return max(0, min(100, score))

    async def check_provider_connectivity(self, provider_url: str) -> bool:
        """
        Check if provider is accessible.

        Args:
            provider_url: Provider base URL

        Returns:
            True if provider is accessible
        """
        return await self.quick_check(provider_url, timeout=10)
