import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class StreamProxy:
    """A single upstream stream connection shared by multiple clients."""

    stream_url: str
    channel_id: int
    buffer_size: int = 64  # number of chunks to retain in ring buffer
    idle_timeout: int = 300  # seconds without clients before auto-close

    _queue: asyncio.Queue = field(init=False, repr=False)
    _clients: int = field(default=0, init=False)
    _fetch_task: Optional[asyncio.Task] = field(default=None, init=False, repr=False)
    _closed: bool = field(default=False, init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)

    def __post_init__(self):
        self._queue = asyncio.Queue(self.buffer_size)

    @property
    def client_count(self) -> int:
        return self._clients

    @property
    def is_running(self) -> bool:
        return self._fetch_task is not None and not self._fetch_task.done()

    async def start(self):
        if self._fetch_task is None:
            self._fetch_task = asyncio.create_task(self._fetch_stream())
            logger.info(f"[StreamProxy] Started upstream fetch channel_id=%s url=%s", self.channel_id, self.stream_url)

    def add_client(self):
        self._clients += 1
        self.last_activity = datetime.now(timezone.utc)
        logger.debug("[StreamProxy] add_client channel_id=%s clients=%d", self.channel_id, self._clients)

    def remove_client(self):
        if self._clients > 0:
            self._clients -= 1
        self.last_activity = datetime.now(timezone.utc)
        logger.debug("[StreamProxy] remove_client channel_id=%s clients=%d", self.channel_id, self._clients)

    async def read_chunks(self) -> AsyncGenerator[bytes, None]:
        self.add_client()
        try:
            while not self._closed:
                try:
                    chunk = await self._queue.get()
                    if chunk is None:  # sentinel for close
                        break
                    yield chunk
                except asyncio.CancelledError:
                    break
        finally:
            self.remove_client()

    async def _fetch_stream(self):
        try:
            timeout = httpx.Timeout(10.0, read=30.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("GET", self.stream_url) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes(chunk_size=8192):
                        if self._closed:
                            break
                        # Drop oldest if queue full
                        if self._queue.full():
                            try:
                                _ = self._queue.get_nowait()
                            except asyncio.QueueEmpty:
                                pass
                        await self._queue.put(chunk)
                        self.last_activity = datetime.now(timezone.utc)
                        if self._clients == 0 and (datetime.now(timezone.utc) - self.last_activity).total_seconds() > self.idle_timeout:
                            logger.info("[StreamProxy] Idle timeout channel_id=%s closing", self.channel_id)
                            break
        except Exception as e:
            logger.warning("[StreamProxy] Upstream error channel_id=%s err=%s", self.channel_id, e)
        finally:
            self._closed = True
            # Flush subscribers
            try:
                await self._queue.put(None)
            except Exception:
                pass
            logger.info("[StreamProxy] Stopped channel_id=%s", self.channel_id)

    async def close(self):
        if not self._closed:
            self._closed = True
            if self._fetch_task:
                self._fetch_task.cancel()
            await self._queue.put(None)
