"""WebSocket API for real-time monitoring."""
import asyncio
import logging
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        async with self.lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Dictionary to send as JSON
        """
        if not self.active_connections:
            return

        disconnected = set()
        message_str = json.dumps(message)

        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {str(e)}")
                disconnected.add(connection)

        # Remove disconnected clients
        if disconnected:
            async with self.lock:
                self.active_connections -= disconnected

    async def send_personal(self, websocket: WebSocket, message: Dict):
        """
        Send a message to a specific client.

        Args:
            websocket: Target WebSocket connection
            message: Dictionary to send as JSON
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            await self.disconnect(websocket)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring.

    Clients can receive:
    - Health check updates
    - Sync progress updates
    - Stream failover events
    - System alerts
    """
    await manager.connect(websocket)

    try:
        # Send initial connection message
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "WebSocket connected successfully",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong for keep-alive
                if message.get("type") == "ping":
                    await manager.send_personal(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    continue

                # Handle subscription requests
                if message.get("type") == "subscribe":
                    topic = message.get("topic")
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "topic": topic,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {str(e)}")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await manager.disconnect(websocket)


async def broadcast_health_check_update(stream_id: int, is_alive: bool,
                                       channel_name: str, provider_name: str):
    """
    Broadcast health check update to all connected clients.

    Args:
        stream_id: Stream ID
        is_alive: Whether stream is alive
        channel_name: Channel name
        provider_name: Provider name
    """
    await manager.broadcast({
        "type": "health_check_update",
        "data": {
            "stream_id": stream_id,
            "is_alive": is_alive,
            "channel_name": channel_name,
            "provider_name": provider_name
        },
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_sync_progress(provider_id: int, provider_name: str,
                                  progress: int, total: int, status: str):
    """
    Broadcast sync progress to all connected clients.

    Args:
        provider_id: Provider ID
        provider_name: Provider name
        progress: Current progress count
        total: Total items to sync
        status: Status message
    """
    await manager.broadcast({
        "type": "sync_progress",
        "data": {
            "provider_id": provider_id,
            "provider_name": provider_name,
            "progress": progress,
            "total": total,
            "percentage": round((progress / total * 100) if total > 0 else 0, 1),
            "status": status
        },
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_stream_failover(channel_id: int, channel_name: str,
                                   old_stream_url: str, new_stream_url: str,
                                   reason: str):
    """
    Broadcast stream failover event to all connected clients.

    Args:
        channel_id: Channel ID
        channel_name: Channel name
        old_stream_url: Previous stream URL
        new_stream_url: New stream URL
        reason: Reason for failover
    """
    await manager.broadcast({
        "type": "stream_failover",
        "data": {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "old_stream_url": old_stream_url,
            "new_stream_url": new_stream_url,
            "reason": reason
        },
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_alert(level: str, title: str, message: str):
    """
    Broadcast system alert to all connected clients.

    Args:
        level: Alert level (info, warning, error, critical)
        title: Alert title
        message: Alert message
    """
    await manager.broadcast({
        "type": "alert",
        "data": {
            "level": level,
            "title": title,
            "message": message
        },
        "timestamp": datetime.utcnow().isoformat()
    })


async def broadcast_vod_generation_progress(movies_processed: int, movies_total: int,
                                            episodes_processed: int, episodes_total: int):
    """
    Broadcast VOD STRM generation progress.

    Args:
        movies_processed: Number of movies processed
        movies_total: Total movies
        episodes_processed: Number of episodes processed
        episodes_total: Total episodes
    """
    await manager.broadcast({
        "type": "vod_generation_progress",
        "data": {
            "movies_processed": movies_processed,
            "movies_total": movies_total,
            "episodes_processed": episodes_processed,
            "episodes_total": episodes_total,
            "total_processed": movies_processed + episodes_processed,
            "total_items": movies_total + episodes_total,
            "percentage": round(
                ((movies_processed + episodes_processed) / (movies_total + episodes_total) * 100)
                if (movies_total + episodes_total) > 0 else 0,
                1
            )
        },
        "timestamp": datetime.utcnow().isoformat()
    })
