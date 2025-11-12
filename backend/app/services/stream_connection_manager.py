import asyncio
from dataclasses import dataclass
from typing import Dict
from datetime import datetime, timezone

from .stream_proxy import StreamProxy


def _key(stream_url: str, channel_id: int) -> str:
    return f"{channel_id}:{stream_url}"


@dataclass
class StreamConnectionManager:
    active_streams: Dict[str, StreamProxy]
    lock: asyncio.Lock

    def __init__(self):
        self.active_streams = {}
        self.lock = asyncio.Lock()

    async def get_or_create_stream(self, stream_url: str, channel_id: int) -> StreamProxy:
        k = _key(stream_url, channel_id)
        async with self.lock:
            proxy = self.active_streams.get(k)
            if proxy is None or proxy._closed:
                proxy = StreamProxy(stream_url=stream_url, channel_id=channel_id)
                await proxy.start()
                self.active_streams[k] = proxy
            return proxy

    async def release_stream(self, stream_url: str, channel_id: int) -> None:
        k = _key(stream_url, channel_id)
        async with self.lock:
            proxy = self.active_streams.get(k)
            if proxy and proxy.client_count == 0 and proxy._closed:
                self.active_streams.pop(k, None)

    async def cleanup_idle_streams(self, max_idle_seconds: int = 300) -> None:
        now = datetime.now(timezone.utc)
        async with self.lock:
            to_remove = []
            for k, proxy in list(self.active_streams.items()):
                if proxy.client_count == 0 and (now - proxy.last_activity).total_seconds() > max_idle_seconds:
                    await proxy.close()
                    to_remove.append(k)
            for k in to_remove:
                self.active_streams.pop(k, None)

    def get_stats(self) -> dict:
        streams = []
        total_clients = 0
        for k, p in self.active_streams.items():
            streams.append({
                "key": k,
                "channel_id": p.channel_id,
                "url": p.stream_url,
                "clients": p.client_count,
                "running": p.is_running,
                "created_at": p.created_at.isoformat(),
                "last_activity": p.last_activity.isoformat(),
            })
            total_clients += p.client_count
        return {
            "active_streams": len(self.active_streams),
            "total_clients": total_clients,
            "streams": streams,
        }


# Singleton instance
stream_manager = StreamConnectionManager()
