"""Integration URLs and information endpoints."""
import logging
from fastapi import APIRouter, Depends, Request
from app.core.auth import get_current_user
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_base_url(request: Request) -> str:
    """Get base URL from request."""
    if settings.EXTERNAL_URL:
        return settings.EXTERNAL_URL.rstrip('/')

    # Auto-detect from request
    scheme = request.url.scheme
    host_header = request.headers.get("host")
    if host_header:
        return f"{scheme}://{host_header}"

    return f"{scheme}://localhost:8000"


@router.get("/urls")
async def get_integration_urls(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get all integration URLs for Plex, Emby, IPTV apps, etc.

    Returns URLs with proper authentication placeholders.
    """
    base_url = get_base_url(request)
    username = current_user.username

    return {
        "base_url": base_url,
        "hdhr": {
            "name": "HDHomeRun Emulation",
            "description": "For Plex Live TV, Emby Live TV, Channels DVR",
            "urls": {
                "discovery": f"{base_url}/discover.json",
                "lineup": f"{base_url}/lineup.json",
                "lineup_status": f"{base_url}/lineup_status.json",
                "device_xml": f"{base_url}/device.xml",
                "epg": f"{base_url}/epg.xml"
            },
            "setup_instructions": {
                "plex": [
                    "1. Go to Settings → Live TV & DVR",
                    "2. Click 'Set Up Plex DVR'",
                    "3. Select 'HDHomeRun' as device type",
                    f"4. Enter tuner IP: {request.client.host if request.client else 'YOUR_SERVER_IP'}",
                    f"5. Set EPG URL: {base_url}/epg.xml",
                    "6. Scan for channels"
                ],
                "emby": [
                    "1. Go to Settings → Live TV",
                    "2. Click 'Add' under Tuner Devices",
                    "3. Select 'HDHomeRun'",
                    f"4. Enter IP: {request.client.host if request.client else 'YOUR_SERVER_IP'}",
                    f"5. Set Guide Data Provider: XMLTV → {base_url}/epg.xml",
                    "6. Refresh guide data"
                ]
            }
        },
        "xtream": {
            "name": "Xtream Codes API",
            "description": "For TiviMate, IPTV Smarters Pro, GSE Smart IPTV",
            "urls": {
                "player_api": f"{base_url}/player_api.php?username={username}&password=YOUR_PASSWORD",
                "m3u_playlist": f"{base_url}/get.php?username={username}&password=YOUR_PASSWORD&type=m3u_plus&output=ts",
                "xmltv_epg": f"{base_url}/xmltv.php?username={username}&password=YOUR_PASSWORD"
            },
            "credentials": {
                "username": username,
                "password": "YOUR_PASSWORD",
                "server_url": base_url
            },
            "setup_instructions": {
                "tivimate": [
                    "1. Open TiviMate → Settings → Playlists",
                    "2. Click '+' to add playlist",
                    "3. Select 'Xtream Codes API'",
                    f"4. Server: {base_url}",
                    f"5. Username: {username}",
                    "6. Password: YOUR_PASSWORD",
                    f"7. EPG URL: {base_url}/xmltv.php?username={username}&password=YOUR_PASSWORD"
                ],
                "iptv_smarters": [
                    "1. Open IPTV Smarters Pro",
                    "2. Select 'Add New User' → 'Login with Xtream Codes API'",
                    f"3. Server URL: {base_url}",
                    f"4. Username: {username}",
                    "5. Password: YOUR_PASSWORD",
                    "6. Click 'Add User'"
                ]
            }
        },
        "direct_urls": {
            "name": "Direct Access URLs",
            "description": "For manual testing and custom integrations",
            "urls": {
                "api_docs": f"{base_url}/docs",
                "openapi_json": f"{base_url}/openapi.json",
                "health_check": f"{base_url}/api/health/status",
                "websocket_monitor": f"ws://{request.headers.get('host', 'localhost:8000')}/ws/monitor"
            }
        },
        "notes": [
            "⚠️ Replace 'YOUR_PASSWORD' with your actual password",
            "💡 For external access, ensure port 8000 is forwarded",
            "🔒 Use HTTPS in production for secure connections",
            "📱 Use these URLs in your IPTV apps to connect"
        ]
    }


@router.get("/test/epg")
async def test_epg_export(current_user: User = Depends(get_current_user)):
    """
    Test EPG export functionality.

    Returns EPG statistics and validation info.
    """
    from app.services.xmltv_generator import XMLTVGenerator
    from app.core.database import async_session

    try:
        async with async_session() as db:
            generator = XMLTVGenerator(db)
            stats = await generator.get_epg_stats()

            # Generate small sample
            xmltv_sample = await generator.generate_xmltv()

            # Basic validation
            is_valid = (
                xmltv_sample.startswith('<?xml') and
                '<tv' in xmltv_sample and
                '</tv>' in xmltv_sample
            )

            return {
                "status": "success" if is_valid else "error",
                "valid_xmltv": is_valid,
                "statistics": stats,
                "sample_size_bytes": len(xmltv_sample.encode('utf-8')),
                "has_channels": stats.get("channels_with_epg", 0) > 0,
                "has_programs": stats.get("total_programs", 0) > 0,
                "message": (
                    "EPG export is working correctly" if is_valid and stats.get("total_programs", 0) > 0
                    else "EPG export format is valid but no program data available yet. Add a provider with EPG."
                    if is_valid
                    else "EPG export validation failed"
                )
            }
    except Exception as e:
        logger.error(f"EPG test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "valid_xmltv": False,
            "message": f"EPG test failed: {str(e)}"
        }


@router.get("/download/epg")
async def download_epg(current_user: User = Depends(get_current_user)):
    """
    Download EPG as XMLTV file.

    Returns the full XMLTV document for download.
    """
    from fastapi.responses import Response
    from app.services.xmltv_generator import XMLTVGenerator
    from app.core.database import async_session

    try:
        async with async_session() as db:
            generator = XMLTVGenerator(db)
            xmltv_content = await generator.generate_xmltv()

            return Response(
                content=xmltv_content,
                media_type="application/xml",
                headers={
                    "Content-Disposition": "attachment; filename=epg.xml",
                    "Content-Type": "application/xml; charset=utf-8"
                }
            )
    except Exception as e:
        logger.error(f"EPG download failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate EPG: {str(e)}"
        )


@router.get("/info")
async def get_integration_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive integration information.

    Returns system info, URLs, and setup status.
    """
    from app.services.xmltv_generator import XMLTVGenerator
    from app.core.database import async_session

    base_url = get_base_url(request)

    # Get EPG stats
    try:
        async with async_session() as db:
            generator = XMLTVGenerator(db)
            epg_stats = await generator.get_epg_stats()
    except Exception as e:
        logger.warning(f"Failed to get EPG stats: {e}")
        epg_stats = {}

    return {
        "system": {
            "base_url": base_url,
            "version": settings.APP_VERSION,
            "app_name": settings.APP_NAME
        },
        "epg": {
            "available": epg_stats.get("total_programs", 0) > 0,
            "channels": epg_stats.get("channels_with_epg", 0),
            "programs": epg_stats.get("total_programs", 0),
            "date_range_days": epg_stats.get("date_range_days", 0)
        },
        "endpoints": {
            "hdhr_discovery": f"{base_url}/discover.json",
            "hdhr_epg": f"{base_url}/epg.xml",
            "xtream_api": f"{base_url}/player_api.php",
            "m3u_playlist": f"{base_url}/get.php",
            "xmltv_epg": f"{base_url}/xmltv.php"
        },
        "quick_links": {
            "api_docs": f"{base_url}/docs",
            "integration_guide": f"{base_url}/#/integration",
            "settings": f"{base_url}/#/settings"
        }
    }
