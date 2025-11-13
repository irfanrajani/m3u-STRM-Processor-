"""HDHomeRun emulation API endpoints."""
from fastapi import APIRouter, Depends, Response, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.services.hdhr_emulator import HDHomeRunEmulator
from app.services.xmltv_generator import XMLTVGenerator
import httpx
from app.services.stream_connection_manager import stream_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize emulator
hdhr = HDHomeRunEmulator()


def get_base_url(request: Request) -> str:
    """
    Get base URL for this server - auto-detects from request.

    Args:
        request: FastAPI request object

    Returns:
        Base URL (e.g., http://192.168.1.100:8000)
    """
    # Use configured external URL if provided
    if settings.EXTERNAL_URL:
        return settings.EXTERNAL_URL.rstrip('/')

    # Auto-detect from request
    scheme = request.url.scheme
    host = request.client.host if request.client else "localhost"

    # Try to get the actual host from headers (in case of proxy)
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_host:
        return f"{scheme}://{forwarded_host}"

    # Use host header
    host_header = request.headers.get("host")
    if host_header:
        return f"{scheme}://{host_header}"

    # Fallback
    return f"{scheme}://{host}:{settings.API_PORT}"


@router.get("/discover.json")
async def discover(request: Request):
    """HDHomeRun device discovery endpoint."""
    base_url = get_base_url(request)
    return hdhr.get_discover_data(base_url)


@router.get("/lineup_status.json")
async def lineup_status():
    """HDHomeRun lineup status endpoint."""
    return hdhr.get_lineup_status()


@router.get("/lineup.json")
async def lineup(request: Request, db: AsyncSession = Depends(get_db)):
    """HDHomeRun channel lineup endpoint."""
    base_url = get_base_url(request)
    # Get proxy mode from settings
    proxy_mode = settings.HDHR_PROXY_MODE
    return await hdhr.get_lineup(db, base_url, proxy_mode)


@router.get("/device.xml")
async def device_xml(request: Request):
    """HDHomeRun device XML for SSDP discovery."""
    base_url = get_base_url(request)
    xml_content = hdhr.get_device_xml(base_url)
    return Response(content=xml_content, media_type="application/xml")


@router.get("/epg.xml")
async def epg_xml(db: AsyncSession = Depends(get_db)):
    """
    EPG/XMLTV endpoint for HDHomeRun compatibility.

    Provides electronic program guide data in XMLTV format.
    Compatible with Plex Live TV, Emby Live TV, and Channels DVR.
    """
    try:
        # Generate XMLTV from database
        generator = XMLTVGenerator(db)
        xmltv_content = await generator.generate_xmltv()

        # Return as XML response with HDHR-specific headers
        return Response(
            content=xmltv_content,
            media_type="application/xml",
            headers={
                "Content-Disposition": "inline; filename=epg.xml",
                "Cache-Control": "public, max-age=1800"  # Cache for 30 minutes
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate XMLTV for HDHR: {e}", exc_info=True)
        # Return minimal structure on error
        xmltv = """<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="M3U STRM Processor">
</tv>"""
        return Response(content=xmltv, media_type="application/xml")


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
            # Shared-proxy mode - stream through server with connection sharing
            proxy = await stream_manager.get_or_create_stream(stream_url, channel_id)

            async def stream_generator():
                try:
                    async for chunk in proxy.read_chunks():
                        yield chunk
                finally:
                    # allow cleanup; manager will prune if closed
                    await stream_manager.release_stream(stream_url, channel_id)

            return StreamingResponse(
                stream_generator(),
                media_type="video/mp2t",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )

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
