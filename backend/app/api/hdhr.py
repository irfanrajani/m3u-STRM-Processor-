"""HDHomeRun emulation API endpoints."""
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.services.hdhr_emulator import HDHomeRunEmulator
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize emulator
hdhr = HDHomeRunEmulator()


def get_base_url() -> str:
    """Get base URL for this server."""
    # Use configured external URL or construct from settings
    if hasattr(settings, 'EXTERNAL_URL') and settings.EXTERNAL_URL:
        return settings.EXTERNAL_URL.rstrip('/')
    return f"http://localhost:{settings.API_PORT}"


@router.get("/discover.json")
async def discover():
    """HDHomeRun device discovery endpoint."""
    base_url = get_base_url()
    return hdhr.get_discover_data(base_url)


@router.get("/lineup_status.json")
async def lineup_status():
    """HDHomeRun lineup status endpoint."""
    return hdhr.get_lineup_status()


@router.get("/lineup.json")
async def lineup(db: AsyncSession = Depends(get_db)):
    """HDHomeRun channel lineup endpoint."""
    base_url = get_base_url()
    # Get proxy mode from settings
    proxy_mode = getattr(settings, 'HDHR_PROXY_MODE', 'direct')
    return await hdhr.get_lineup(db, base_url, proxy_mode)


@router.get("/device.xml")
async def device_xml():
    """HDHomeRun device XML for SSDP discovery."""
    base_url = get_base_url()
    xml_content = hdhr.get_device_xml(base_url)
    return Response(content=xml_content, media_type="application/xml")


@router.get("/auto/v{channel_id}")
async def stream_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    """
    Stream a channel (proxy mode endpoint).

    In direct mode, this redirects to the original stream URL.
    In proxy mode, this streams through the server.
    """
    try:
        # Get stream URL
        stream_url = await hdhr.get_stream_url(db, channel_id)

        if not stream_url:
            raise HTTPException(status_code=404, detail="Channel not found or no active stream")

        # Get proxy mode from settings
        proxy_mode = getattr(settings, 'HDHR_PROXY_MODE', 'direct')

        if proxy_mode == "direct":
            # Redirect to original stream
            return RedirectResponse(url=stream_url, status_code=302)
        else:
            # Proxy mode - stream through server
            return await _proxy_stream(stream_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming channel {channel_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Stream error")


async def _proxy_stream(stream_url: str):
    """
    Proxy a stream through the server.

    Args:
        stream_url: Original stream URL

    Returns:
        Streaming response
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", stream_url) as response:
                response.raise_for_status()

                # Get content type
                content_type = response.headers.get("content-type", "video/mp2t")

                # Stream the content
                async def stream_generator():
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk

                return StreamingResponse(
                    stream_generator(),
                    media_type=content_type,
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive"
                    }
                )
    except httpx.HTTPError as e:
        logger.error(f"HTTP error proxying stream {stream_url}: {str(e)}")
        raise HTTPException(status_code=502, detail="Upstream stream error")
    except Exception as e:
        logger.error(f"Error proxying stream {stream_url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Proxy error")


@router.get("/lineup.post")
async def lineup_post():
    """Handle lineup POST request (scan channels)."""
    # Return success - we don't actually scan
    return {"success": True, "message": "Scan not required for IPTV"}
