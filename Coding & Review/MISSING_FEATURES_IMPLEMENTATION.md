# Missing Features - Complete Implementation Plan

**Created**: 2025-01-13
**Priority**: CRITICAL
**Timeline**: 2-3 days

---

## Executive Summary

Three critical features need completion:

1. **EPG Export (XMLTV Generation)** - 🔴 CRITICAL
   - Currently returns empty placeholder
   - EPG data exists in database but not exported
   - Required for Emby/Plex/TiviMate EPG display
   - **Effort**: 4-6 hours

2. **Notification Settings Persistence** - 🟡 HIGH
   - Frontend UI exists but settings don't save
   - Need backend endpoints for Telegram/Pushover/Webhook config
   - **Effort**: 2-3 hours

3. **Bandwidth Settings Persistence** - 🟡 HIGH
   - Frontend UI exists but settings don't save
   - Need backend endpoints for global bandwidth limits
   - **Effort**: 1-2 hours

**Total Estimated Effort**: 7-11 hours (1-2 days)

---

## 1. EPG Export (XMLTV Generation)

### Problem Statement

**Current State**:
```python
# backend/app/api/xtream.py:xmltv.php endpoint
@router.get("/xmltv.php")
async def get_epg(...):
    # Returns empty XMLTV structure
    xmltv = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv generator-info-name="IPTV Stream Manager">
</tv>"""
    return {"content": xmltv, "content_type": "application/xml"}
```

**Required**: Generate full XMLTV from `epg_programs` table with channel mapping.

### How Other Apps Handle EPG

#### Threadfin (Go)
```go
// Threadfin EPG Export Strategy:
1. Maps internal channel IDs to EPG channel IDs
2. Generates XMLTV on-the-fly (no caching)
3. Includes:
   - Channel definitions (<channel> elements)
   - Programme listings (<programme> elements)
   - Images (channel logos, program posters)
4. Filters by date range (today + 7 days typical)
5. Caches generated XML for 1 hour
```

#### Dispatcharr (Python/Django)
```python
# Dispatcharr EPG Strategy:
1. Stores EPG in PostgreSQL (similar to us)
2. Celery task fetches from XMLTV URL daily
3. Auto-matches channels by:
   - tvg-id (primary)
   - Fuzzy name matching (fallback)
4. Export endpoint:
   - Queries EPG by date range
   - Builds XML using lxml library
   - Streams response (doesn't build entire XML in memory)
5. Supports filtering:
   - By channel group
   - By date range
   - By user favorites
```

### Implementation Plan

#### Step 1: Create XMLTV Generator Service

**File**: `backend/app/services/xmltv_generator.py` (NEW)

```python
"""XMLTV EPG generator service."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.channel import Channel
from app.models.epg import EPGProgram

logger = logging.getLogger(__name__)


class XMLTVGenerator:
    """Generate XMLTV format EPG from database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_xmltv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        channel_ids: Optional[List[int]] = None
    ) -> str:
        """
        Generate complete XMLTV document.

        Args:
            start_date: Filter programs starting from this date (default: now)
            end_date: Filter programs up to this date (default: now + 7 days)
            channel_ids: Optional list of channel IDs to include

        Returns:
            XMLTV XML string
        """
        # Default date range: now to 7 days ahead
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=7)

        # Create root element
        tv = Element('tv')
        tv.set('generator-info-name', 'IPTV Stream Manager')
        tv.set('generator-info-url', 'https://github.com/irfanrajani/m3u-STRM-Processor-')

        # Get channels
        query = select(Channel).where(Channel.enabled.is_(True))
        if channel_ids:
            query = query.where(Channel.id.in_(channel_ids))

        result = await self.db.execute(query.order_by(Channel.name))
        channels = result.scalars().all()

        # Add channel elements
        channel_epg_map = {}  # Map channel.id -> EPG channel ID
        for channel in channels:
            if channel.epg_id:  # Only include channels with EPG ID
                channel_elem = self._create_channel_element(channel)
                tv.append(channel_elem)
                channel_epg_map[channel.epg_id] = channel

        # Get programs
        prog_query = select(EPGProgram).where(
            EPGProgram.start_time >= start_date,
            EPGProgram.start_time <= end_date
        )

        # Filter by EPG channel IDs
        if channel_epg_map:
            prog_query = prog_query.where(
                EPGProgram.channel_id.in_(list(channel_epg_map.keys()))
            )

        prog_result = await self.db.execute(
            prog_query.order_by(EPGProgram.channel_id, EPGProgram.start_time)
        )
        programs = prog_result.scalars().all()

        logger.info(f"Generating XMLTV with {len(channels)} channels and {len(programs)} programs")

        # Add programme elements
        for program in programs:
            programme_elem = self._create_programme_element(program)
            tv.append(programme_elem)

        # Convert to string with proper encoding
        xml_str = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += b'<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
        xml_str += tostring(tv, encoding='utf-8')

        return xml_str.decode('utf-8')

    def _create_channel_element(self, channel: Channel) -> Element:
        """Create XMLTV channel element."""
        channel_elem = Element('channel')
        channel_elem.set('id', channel.epg_id or str(channel.id))

        # Display name
        display_name = SubElement(channel_elem, 'display-name')
        display_name.text = channel.name

        # Icon (channel logo)
        if channel.logo_url:
            icon = SubElement(channel_elem, 'icon')
            icon.set('src', channel.logo_url)

        return channel_elem

    def _create_programme_element(self, program: EPGProgram) -> Element:
        """Create XMLTV programme element."""
        programme = Element('programme')

        # Channel and time attributes
        programme.set('channel', program.channel_id)
        programme.set('start', self._format_xmltv_time(program.start_time))
        programme.set('stop', self._format_xmltv_time(program.end_time))

        # Title
        title = SubElement(programme, 'title')
        title.set('lang', 'en')
        title.text = program.title

        # Subtitle (episode title)
        if program.subtitle:
            sub_title = SubElement(programme, 'sub-title')
            sub_title.set('lang', 'en')
            sub_title.text = program.subtitle

        # Description
        if program.description:
            desc = SubElement(programme, 'desc')
            desc.set('lang', 'en')
            desc.text = program.description

        # Category
        if program.category:
            category = SubElement(programme, 'category')
            category.set('lang', 'en')
            category.text = program.category

        # Icon (program poster)
        if program.icon:
            icon = SubElement(programme, 'icon')
            icon.set('src', program.icon)

        # Episode numbering (XMLTV format: "S.E.P" where S=season-1, E=episode-1, P=part-1)
        if program.episode:
            # Parse episode format (e.g., "S01E05" -> "0.4.")
            ep_num = SubElement(programme, 'episode-num')
            ep_num.set('system', 'xmltv_ns')
            ep_num.text = self._parse_episode_to_xmltv(program.episode)

        # Rating
        if program.rating:
            rating = SubElement(programme, 'rating')
            value = SubElement(rating, 'value')
            value.text = program.rating

        return programme

    def _format_xmltv_time(self, dt: datetime) -> str:
        """
        Format datetime to XMLTV format: YYYYMMDDHHmmss +0000

        Example: 20250113143000 +0000
        """
        return dt.strftime('%Y%m%d%H%M%S +0000')

    def _parse_episode_to_xmltv(self, episode_str: str) -> str:
        """
        Parse episode string to XMLTV episode-num format.

        Input: "S01E05" or "1x5"
        Output: "0.4." (season 1 = 0, episode 5 = 4)
        """
        import re

        # Try S01E05 format
        match = re.match(r'S(\d+)E(\d+)', episode_str, re.IGNORECASE)
        if match:
            season = int(match.group(1)) - 1  # XMLTV is 0-indexed
            episode = int(match.group(2)) - 1
            return f"{season}.{episode}."

        # Try 1x5 format
        match = re.match(r'(\d+)x(\d+)', episode_str)
        if match:
            season = int(match.group(1)) - 1
            episode = int(match.group(2)) - 1
            return f"{season}.{episode}."

        # Can't parse, return empty
        return ""

    async def generate_xmltv_streaming(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """
        Generate XMLTV in streaming fashion (memory efficient).

        Yields XML chunks instead of building entire document in memory.
        Use for large EPG datasets.
        """
        # Yield header
        yield b'<?xml version="1.0" encoding="UTF-8"?>\n'
        yield b'<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
        yield b'<tv generator-info-name="IPTV Stream Manager">\n'

        # Stream channels
        query = select(Channel).where(
            Channel.enabled.is_(True),
            Channel.epg_id.isnot(None)
        )
        result = await self.db.execute(query.order_by(Channel.name))

        for channel in result.scalars():
            channel_elem = self._create_channel_element(channel)
            yield tostring(channel_elem, encoding='utf-8') + b'\n'

        # Stream programs
        if not start_date:
            start_date = datetime.utcnow()
        if not end_date:
            end_date = start_date + timedelta(days=7)

        prog_query = select(EPGProgram).where(
            EPGProgram.start_time >= start_date,
            EPGProgram.start_time <= end_date
        ).order_by(EPGProgram.channel_id, EPGProgram.start_time)

        prog_result = await self.db.execute(prog_query)

        for program in prog_result.scalars():
            programme_elem = self._create_programme_element(program)
            yield tostring(programme_elem, encoding='utf-8') + b'\n'

        # Close tag
        yield b'</tv>\n'
```

#### Step 2: Update Xtream Codes API Endpoint

**File**: `backend/app/api/xtream.py` (MODIFY)

```python
# Add import
from app.services.xmltv_generator import XMLTVGenerator
from fastapi.responses import StreamingResponse

# Update endpoint
@router.get("/xmltv.php")
async def get_epg(
    username: str = Query(...),
    password: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Return EPG in XMLTV format.

    Generates XMLTV from database EPG data.
    """
    # Simple auth check
    if not username or not password:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Generate XMLTV
    generator = XMLTVGenerator(db)

    # Use streaming for memory efficiency
    async def generate():
        async for chunk in generator.generate_xmltv_streaming():
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="application/xml",
        headers={
            "Content-Disposition": "attachment; filename=epg.xml"
        }
    )
```

#### Step 3: Add EPG Export Endpoint to HDHR

**File**: `backend/app/api/hdhr.py` (ADD)

```python
@router.get("/epg.xml")
async def get_epg_xml(request: Request, db: AsyncSession = Depends(get_db)):
    """
    EPG export for Emby/Plex.

    Emby/Plex expect EPG at: http://your-ip:8000/epg.xml
    """
    from app.services.xmltv_generator import XMLTVGenerator

    generator = XMLTVGenerator(db)

    # Generate for next 7 days
    async def generate():
        async for chunk in generator.generate_xmltv_streaming():
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="application/xml",
        headers={
            "Content-Disposition": "inline; filename=epg.xml"
        }
    )
```

#### Step 4: Add EPG Stats Endpoint

**File**: `backend/app/api/epg.py` (UPDATE)

```python
@router.get("/stats")
async def get_epg_stats(db: AsyncSession = Depends(get_db)):
    """Get EPG statistics."""
    from sqlalchemy import func

    # Count channels with EPG
    channels_with_epg = await db.scalar(
        select(func.count(Channel.id)).where(
            Channel.enabled.is_(True),
            Channel.epg_id.isnot(None)
        )
    )

    # Count total programs
    total_programs = await db.scalar(
        select(func.count(EPGProgram.id))
    )

    # Get date range
    oldest = await db.scalar(
        select(func.min(EPGProgram.start_time))
    )
    newest = await db.scalar(
        select(func.max(EPGProgram.end_time))
    )

    # Last update
    last_update = await db.scalar(
        select(func.max(EPGProgram.created_at))
    )

    return {
        "channels_with_epg": channels_with_epg or 0,
        "total_programs": total_programs or 0,
        "oldest_program": oldest.isoformat() if oldest else None,
        "newest_program": newest.isoformat() if newest else None,
        "last_update": last_update.isoformat() if last_update else None
    }
```

### Testing EPG Export

```bash
# Test XMLTV generation
curl "http://localhost:8000/xmltv.php?username=test&password=test" > epg.xml

# Validate XMLTV structure
xmllint --dtdvalid xmltv.dtd epg.xml

# Test in Emby/Plex
# Add EPG source: http://your-server:8000/epg.xml

# Test with TiviMate
# Xtream config includes xmltv.php automatically
```

---

## 2. Notification Settings Persistence

### Problem Statement

**Frontend UI exists** (`SettingsEnhanced.jsx`) with:
- Telegram (bot_token, chat_id, min_level)
- Pushover (user_key, api_token, min_level)
- Webhook (url, min_level)

**Backend missing**: API endpoints to save/load notification configuration.

### Implementation Plan

#### Step 1: Add Notification Settings to Database

**Settings to Add** (`backend/app/api/settings.py`):

```python
# Add to DEFAULT_SETTINGS dictionary

# Notification - Telegram
"notification_telegram_enabled": {
    "value": False,
    "type": "bool",
    "description": "Enable Telegram notifications"
},
"notification_telegram_bot_token": {
    "value": "",
    "type": "string",
    "description": "Telegram bot API token"
},
"notification_telegram_chat_id": {
    "value": "",
    "type": "string",
    "description": "Telegram chat ID for notifications"
},
"notification_telegram_min_level": {
    "value": "INFO",
    "type": "string",
    "description": "Minimum notification level: INFO, WARNING, ERROR, CRITICAL"
},

# Notification - Pushover
"notification_pushover_enabled": {
    "value": False,
    "type": "bool",
    "description": "Enable Pushover notifications"
},
"notification_pushover_user_key": {
    "value": "",
    "type": "string",
    "description": "Pushover user key"
},
"notification_pushover_api_token": {
    "value": "",
    "type": "string",
    "description": "Pushover API token"
},
"notification_pushover_min_level": {
    "value": "WARNING",
    "type": "string",
    "description": "Minimum notification level for Pushover"
},

# Notification - Webhook
"notification_webhook_enabled": {
    "value": False,
    "type": "bool",
    "description": "Enable webhook notifications"
},
"notification_webhook_url": {
    "value": "",
    "type": "string",
    "description": "Webhook URL for POST notifications"
},
"notification_webhook_min_level": {
    "value": "ERROR",
    "type": "string",
    "description": "Minimum notification level for webhook"
},
```

#### Step 2: Add Notification Configuration Endpoint

**File**: `backend/app/api/settings.py` (ADD)

```python
from app.services.notification_manager import notification_manager, NotificationLevel

@router.post("/notifications/configure")
async def configure_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Configure notification manager from saved settings.

    Called on app startup and after settings update.
    """
    # Get all notification settings
    result = await db.execute(
        select(AppSettings).where(
            AppSettings.key.like('notification_%')
        )
    )
    settings = {s.key: json.loads(s.value) for s in result.scalars().all()}

    # Configure Telegram
    if settings.get('notification_telegram_enabled'):
        notification_manager.configure_telegram(
            bot_token=settings.get('notification_telegram_bot_token', ''),
            chat_id=settings.get('notification_telegram_chat_id', ''),
            enabled=True,
            min_level=NotificationLevel(settings.get('notification_telegram_min_level', 'INFO'))
        )

    # Configure Pushover
    if settings.get('notification_pushover_enabled'):
        notification_manager.configure_pushover(
            user_key=settings.get('notification_pushover_user_key', ''),
            api_token=settings.get('notification_pushover_api_token', ''),
            enabled=True,
            min_level=NotificationLevel(settings.get('notification_pushover_min_level', 'WARNING'))
        )

    # Configure Webhook
    if settings.get('notification_webhook_enabled'):
        notification_manager.configure_webhook(
            webhook_url=settings.get('notification_webhook_url', ''),
            enabled=True,
            min_level=NotificationLevel(settings.get('notification_webhook_min_level', 'ERROR'))
        )

    return {"status": "configured", "channels": len(notification_manager.notifiers)}


@router.post("/notifications/test")
async def test_notification(
    channel: str,  # 'telegram', 'pushover', or 'webhook'
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send test notification to verify configuration.
    """
    from app.services.notification_manager import NotificationChannel, notification_manager

    # Configure from settings first
    await configure_notifications(db, current_user)

    # Send test
    result = await notification_manager.send(
        title="Test Notification",
        message="This is a test notification from IPTV Stream Manager",
        level=NotificationLevel.INFO,
        channels=[NotificationChannel(channel.upper())]
    )

    return {
        "success": result.get(NotificationChannel(channel.upper()), False),
        "message": "Test notification sent"
    }
```

#### Step 3: Initialize Notifications on Startup

**File**: `backend/app/main.py` (MODIFY lifespan)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting IPTV Stream Manager...")
    await init_db()
    logger.info("Database initialized")

    # ... existing user creation code ...

    # Configure notifications from settings
    from app.api.settings import configure_notifications
    from app.core.database import async_session
    async with async_session() as db:
        try:
            await configure_notifications(db, None)  # None = skip auth check
            logger.info("✅ Notifications configured from settings")
        except Exception as e:
            logger.warning(f"Failed to configure notifications: {e}")

    yield
    logger.info("Shutting down...")
    await close_db()
```

#### Step 4: Update Settings Categories

**File**: `backend/app/api/settings.py` (UPDATE categories)

```python
@router.get("/categories/list")
async def get_settings_categories(...):
    return {
        # ... existing categories ...
        "Notifications - Telegram": [
            "notification_telegram_enabled",
            "notification_telegram_bot_token",
            "notification_telegram_chat_id",
            "notification_telegram_min_level"
        ],
        "Notifications - Pushover": [
            "notification_pushover_enabled",
            "notification_pushover_user_key",
            "notification_pushover_api_token",
            "notification_pushover_min_level"
        ],
        "Notifications - Webhook": [
            "notification_webhook_enabled",
            "notification_webhook_url",
            "notification_webhook_min_level"
        ],
        # ... rest ...
    }
```

#### Step 5: Update Frontend to Use Real Settings

**File**: `frontend/src/pages/SettingsEnhanced.jsx` (MODIFY)

```javascript
// Remove local notificationConfig state
// Instead, load from settings API

const { data: notificationSettings } = useQuery({
  queryKey: ['settings-notifications'],
  queryFn: async () => {
    const response = await axios.get(`${API_URL}/api/settings/`);
    const settings = response.data;

    // Extract notification settings
    return {
      telegram: {
        enabled: settings.notification_telegram_enabled?.value || false,
        bot_token: settings.notification_telegram_bot_token?.value || '',
        chat_id: settings.notification_telegram_chat_id?.value || '',
        min_level: settings.notification_telegram_min_level?.value || 'INFO'
      },
      pushover: {
        enabled: settings.notification_pushover_enabled?.value || false,
        user_key: settings.notification_pushover_user_key?.value || '',
        api_token: settings.notification_pushover_api_token?.value || '',
        min_level: settings.notification_pushover_min_level?.value || 'WARNING'
      },
      webhook: {
        enabled: settings.notification_webhook_enabled?.value || false,
        url: settings.notification_webhook_url?.value || '',
        min_level: settings.notification_webhook_min_level?.value || 'ERROR'
      }
    };
  }
});

// Update handleSave to save all notification settings
const handleSave = async () => {
  const payload = {};

  // Include notification settings
  payload['notification_telegram_enabled'] = notificationConfig.telegram.enabled;
  payload['notification_telegram_bot_token'] = notificationConfig.telegram.bot_token;
  // ... etc for all notification fields

  await axios.post(`${API_URL}/api/settings/bulk-update`, { settings: payload });

  // Trigger reconfiguration
  await axios.post(`${API_URL}/api/settings/notifications/configure`);

  toast.success('Settings saved and notifications configured!');
};

// Add test button handler
const handleTestNotification = async (channel) => {
  try {
    await axios.post(`${API_URL}/api/settings/notifications/test`, { channel });
    toast.success(`Test notification sent to ${channel}!`);
  } catch (err) {
    toast.error(`Failed to send test notification: ${err.message}`);
  }
};
```

---

## 3. Bandwidth Settings Persistence

### Problem Statement

Same as notifications - frontend UI exists, backend persistence missing.

### Implementation Plan

#### Step 1: Add Bandwidth Settings

**File**: `backend/app/api/settings.py` (ADD to DEFAULT_SETTINGS)

```python
# Bandwidth Throttling
"bandwidth_throttling_enabled": {
    "value": False,
    "type": "bool",
    "description": "Enable global bandwidth throttling"
},
"bandwidth_global_limit_mbps": {
    "value": None,
    "type": "float",
    "description": "Global bandwidth limit in Mbps (null = unlimited)"
},
```

#### Step 2: Add Bandwidth Configuration Endpoint

**File**: `backend/app/api/settings.py` (ADD)

```python
from app.services.bandwidth_limiter import bandwidth_limiter

@router.post("/bandwidth/configure")
async def configure_bandwidth(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Configure bandwidth limiter from settings."""
    result = await db.execute(
        select(AppSettings).where(
            AppSettings.key.in_([
                'bandwidth_throttling_enabled',
                'bandwidth_global_limit_mbps'
            ])
        )
    )
    settings = {s.key: json.loads(s.value) for s in result.scalars().all()}

    if settings.get('bandwidth_throttling_enabled'):
        limit_mbps = settings.get('bandwidth_global_limit_mbps')
        bandwidth_limiter.set_global_limit(limit_mbps)
        return {"status": "enabled", "limit_mbps": limit_mbps}
    else:
        bandwidth_limiter.set_global_limit(None)
        return {"status": "disabled"}


@router.get("/bandwidth/stats")
async def get_bandwidth_stats():
    """Get current bandwidth usage statistics."""
    return bandwidth_limiter.get_stats()
```

#### Step 3: Initialize on Startup

**File**: `backend/app/main.py` (ADD to lifespan)

```python
# Configure bandwidth limiter
try:
    from app.api.settings import configure_bandwidth
    await configure_bandwidth(db, None)
    logger.info("✅ Bandwidth limiter configured")
except Exception as e:
    logger.warning(f"Failed to configure bandwidth: {e}")
```

#### Step 4: Update Frontend

Similar pattern to notifications - load from settings, save via bulk-update.

---

## 4. Testing Checklist

### EPG Export
- [ ] Generate XMLTV with sample data
- [ ] Validate XML structure
- [ ] Test with Emby/Plex EPG import
- [ ] Test with TiviMate (Xtream endpoint)
- [ ] Verify date range filtering works
- [ ] Check memory usage with large EPG datasets

### Notifications
- [ ] Save Telegram config and verify persistence after restart
- [ ] Send test Telegram notification
- [ ] Save Pushover config and test
- [ ] Save Webhook config and test
- [ ] Verify min_level filtering works
- [ ] Test with health check failure (should trigger notification)

### Bandwidth
- [ ] Set global limit and verify enforcement
- [ ] Check bandwidth stats endpoint
- [ ] Test with multiple concurrent streams
- [ ] Verify token bucket algorithm works correctly
- [ ] Test bandwidth monitor accuracy

---

## 5. Integration Points

### Where These Features Connect:

#### EPG Export:
- **Used by**: Emby, Plex, Jellyfin, TiviMate, IPTV Smarters
- **Endpoints**: `/epg.xml`, `/xmltv.php`
- **Data source**: `epg_programs` table
- **Update frequency**: Regenerated on each request (with caching recommended)

#### Notifications:
- **Triggered by**:
  - Health check failures (stream goes down)
  - Provider sync errors
  - VOD generation completion
  - System alerts
- **Integration**: `notification_manager.send()`
- **Config source**: `app_settings` table

#### Bandwidth:
- **Used by**: Stream proxy (`stream_proxy.py`)
- **Integration**: Wrap `read_chunks()` with bandwidth limiter
- **Monitoring**: Real-time stats via `/api/settings/bandwidth/stats`

---

## 6. Implementation Order

**Day 1 (4-6 hours):**
1. Create `XMLTVGenerator` service
2. Update `/xmltv.php` endpoint
3. Add `/epg.xml` endpoint
4. Test with sample EPG data

**Day 2 (3-4 hours):**
5. Add notification settings to DEFAULT_SETTINGS
6. Create `/settings/notifications/configure` endpoint
7. Add startup configuration in `main.py`
8. Update frontend SettingsEnhanced.jsx
9. Test notification persistence

**Day 3 (1-2 hours):**
10. Add bandwidth settings
11. Create `/settings/bandwidth/configure` endpoint
12. Add startup configuration
13. Update frontend
14. Integration testing

---

## 7. Success Criteria

✅ **EPG Export**:
- XMLTV generates valid XML
- Emby/Plex can import and display EPG
- TiviMate shows program guide
- Performance acceptable with 10k+ programs

✅ **Notifications**:
- Settings persist across restarts
- Test notifications deliver successfully
- Health check failures trigger notifications
- Min level filtering works correctly

✅ **Bandwidth**:
- Global limit enforced accurately
- Stats show real usage
- Token bucket prevents bursts
- No impact when disabled

---

## Estimated Timeline

| Feature | Effort | Priority |
|---------|--------|----------|
| EPG Export | 4-6 hours | 🔴 CRITICAL |
| Notifications | 2-3 hours | 🟡 HIGH |
| Bandwidth | 1-2 hours | 🟡 HIGH |
| **Total** | **7-11 hours** | **1-2 days** |

---

## Next Steps

1. Review this implementation plan
2. Create feature branch: `feature/missing-features-completion`
3. Implement in order: EPG → Notifications → Bandwidth
4. Test each feature before moving to next
5. Commit and push when all tests pass
6. Update documentation

---

**Let's proceed with implementation!** 🚀
