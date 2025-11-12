# M3U-STRM-Processor: Complete Implementation Plan
## "Mega Super App" Development Roadmap

**Version**: 1.0
**Created**: 2025-01-12
**Timeline**: 7 weeks (35 working days)
**Goal**: Transform current app into industry-leading IPTV management solution

---

## Executive Summary

### Current Status: 80% Complete ✅

**Existing Strengths:**
- ✅ Intelligent channel merging (region/variant aware)
- ✅ Advanced quality detection (FFprobe-based)
- ✅ Automated health monitoring (50 concurrent checks)
- ✅ Full Xtream Codes support (with backup hosts)
- ✅ Complete VOD management (STRM files)
- ✅ Multi-user authentication & analytics
- ✅ Production-ready infrastructure (Docker, CI/CD)

### Remaining 20%: Strategic Enhancements

**Phase 1**: Core Optimizations (Weeks 1-2)
- Stream connection sharing (50-90% bandwidth reduction)
- Grace period failover (seamless provider switching)
- HLS advanced buffering (superior M3U8 playback)

**Phase 2**: User Experience (Weeks 3-4)
- Real-time monitoring dashboard
- Multi-channel notification system
- Explicit backup channel assignment UI

**Phase 3**: Advanced Features (Weeks 5-6)
- Bandwidth throttling system
- Xtream Codes API output
- Enhanced channel grouping

**Phase 4**: Polish & Launch (Week 7)
- Load testing & optimization
- Documentation & user guides
- Production deployment

---

## PHASE 1: Core Optimizations (Weeks 1-2)

### Goal: Maximize bandwidth efficiency and stream reliability

---

### 1.1 Stream Connection Sharing (Days 1-4)

**Objective**: Reduce bandwidth usage by 50-90% through backend stream reuse

**Priority**: ⭐⭐⭐⭐⭐ CRITICAL

**Impact**:
- 10 users watching same channel → 1 backend connection (vs 10)
- Lower provider load (reduce ban risk)
- Faster stream startup (reuse established connections)

#### Tasks

##### Task 1.1.1: Create Stream Proxy Infrastructure (Day 1)
**File**: `/backend/app/services/stream_proxy.py` (NEW)

**Requirements**:
```python
class StreamProxy:
    """Single backend stream serving multiple clients"""
    - stream_url: str
    - channel_id: int
    - client_count: int
    - chunks: asyncio.Queue  # Buffer for sharing
    - is_running: bool
    - created_at: datetime
    - last_activity: datetime

    Methods:
    - async start() → Start backend fetch
    - async _fetch_stream() → Background task fetching chunks
    - async read_chunks() → Generator for clients
    - add_client() → Increment counter
    - remove_client() → Decrement counter
    - async close() → Cleanup
```

**Implementation Steps**:
1. Create `StreamProxy` class with queue-based buffering
2. Implement background fetch task using `aiohttp`
3. Add client connection/disconnection tracking
4. Implement automatic cleanup on zero clients
5. Add logging for debugging

**Testing**:
```python
# Test: Single stream, multiple clients
async def test_stream_sharing():
    proxy = StreamProxy("http://test.m3u8", 1)
    await proxy.start()

    # Simulate 3 clients
    client1 = proxy.read_chunks()
    client2 = proxy.read_chunks()
    client3 = proxy.read_chunks()

    # Verify all receive same chunks
    chunk1 = await anext(client1)
    chunk2 = await anext(client2)
    chunk3 = await anext(client3)

    assert chunk1 == chunk2 == chunk3
    assert proxy.client_count == 3
```

**Success Metrics**:
- ✅ Multiple clients receive identical chunks
- ✅ Single backend connection per stream
- ✅ Graceful cleanup on client disconnect

---

##### Task 1.1.2: Create Stream Connection Manager (Day 2)
**File**: `/backend/app/services/stream_connection_manager.py` (NEW)

**Requirements**:
```python
class StreamConnectionManager:
    """Manages all active stream proxies"""
    - active_streams: Dict[str, StreamProxy]
    - lock: asyncio.Lock

    Methods:
    - async get_or_create_stream(url, channel_id) → StreamProxy
    - async release_stream(url, channel_id) → None
    - async cleanup_idle_streams(max_idle_secs) → None
    - get_stats() → dict
```

**Implementation Steps**:
1. Create manager class with thread-safe dictionary
2. Implement cache key generation (`url:channel_id`)
3. Add get_or_create logic with reuse detection
4. Implement release with auto-cleanup
5. Add idle stream cleanup task
6. Create stats endpoint for monitoring

**Testing**:
```python
async def test_connection_manager():
    manager = StreamConnectionManager()

    # Request same stream twice
    proxy1 = await manager.get_or_create_stream("http://test.m3u8", 1)
    proxy2 = await manager.get_or_create_stream("http://test.m3u8", 1)

    # Should return same proxy
    assert proxy1 is proxy2
    assert proxy1.client_count == 2

    # Release both
    await manager.release_stream("http://test.m3u8", 1)
    await manager.release_stream("http://test.m3u8", 1)

    # Should be cleaned up
    assert len(manager.active_streams) == 0
```

**Success Metrics**:
- ✅ Stream reuse working correctly
- ✅ Automatic cleanup functioning
- ✅ Thread-safe operations

---

##### Task 1.1.3: Integrate with HDHomeRun Endpoint (Day 3)
**File**: `/backend/app/api/hdhr.py` (MODIFY)

**Changes Required**:
1. Import `stream_connection_manager`
2. Update `stream_channel()` endpoint
3. Add connection sharing logic
4. Implement proper cleanup on client disconnect
5. Add error handling

**Before**:
```python
@router.get("/auto/v{channel_id}")
async def stream_channel(channel_id: int):
    stream = await get_best_stream(channel_id)

    # Direct proxy - creates new connection per client
    return StreamingResponse(
        proxy_stream(stream.stream_url),
        media_type="video/mp2t"
    )
```

**After**:
```python
from app.services.stream_connection_manager import stream_manager

@router.get("/auto/v{channel_id}")
async def stream_channel(channel_id: int):
    stream = await get_best_stream(channel_id)

    # Get or create shared proxy
    proxy = await stream_manager.get_or_create_stream(
        stream.stream_url,
        channel_id
    )

    async def stream_generator():
        try:
            async for chunk in proxy.read_chunks():
                yield chunk
        finally:
            # Cleanup on disconnect
            await stream_manager.release_stream(
                stream.stream_url,
                channel_id
            )

    return StreamingResponse(
        stream_generator(),
        media_type="video/mp2t",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

**Testing**:
```bash
# Test with multiple clients
curl http://localhost:8000/auto/v1 &
curl http://localhost:8000/auto/v1 &
curl http://localhost:8000/auto/v1 &

# Check stats endpoint
curl http://localhost:8000/api/streams/stats
# Expected: {"active_streams": 1, "total_clients": 3}
```

**Success Metrics**:
- ✅ Multiple clients → single backend connection
- ✅ Proper cleanup on client disconnect
- ✅ No memory leaks

---

##### Task 1.1.4: Add Celery Cleanup Task (Day 3)
**File**: `/backend/app/tasks/stream_tasks.py` (NEW)

**Implementation**:
```python
from app.services.stream_connection_manager import stream_manager
from celery import Celery

@celery.task
async def cleanup_idle_streams():
    """Run every 5 minutes to cleanup idle streams"""
    await stream_manager.cleanup_idle_streams(max_idle_seconds=300)

    stats = stream_manager.get_stats()
    logger.info(f"Stream cleanup: {stats['active_streams']} active, {stats['total_clients']} clients")

# Schedule in celery_app.py
beat_schedule = {
    "cleanup-idle-streams": {
        "task": "app.tasks.stream_tasks.cleanup_idle_streams",
        "schedule": 300.0,  # Every 5 minutes
    },
}
```

**Success Metrics**:
- ✅ Idle streams cleaned up automatically
- ✅ No orphaned connections

---

##### Task 1.1.5: Add Stats API Endpoint (Day 4)
**File**: `/backend/app/api/streams.py` (NEW)

**Implementation**:
```python
from fastapi import APIRouter
from app.services.stream_connection_manager import stream_manager

router = APIRouter(prefix="/api/streams", tags=["Streams"])

@router.get("/stats")
async def get_stream_stats():
    """Get real-time streaming statistics"""
    return stream_manager.get_stats()

@router.get("/active")
async def get_active_streams():
    """List all active streams with details"""
    stats = stream_manager.get_stats()
    return {
        "count": stats["active_streams"],
        "total_clients": stats["total_clients"],
        "streams": stats["streams"]
    }

@router.post("/cleanup")
async def force_cleanup():
    """Force cleanup of idle streams (admin only)"""
    await stream_manager.cleanup_idle_streams(max_idle_seconds=0)
    return {"status": "success"}
```

**Success Metrics**:
- ✅ Real-time stats accessible
- ✅ Admin controls working

---

##### Task 1.1.6: Integration Testing (Day 4)
**File**: `/backend/tests/test_stream_sharing.py` (NEW)

**Test Scenarios**:
```python
async def test_bandwidth_reduction():
    """Verify bandwidth savings with multiple clients"""
    # Start monitoring backend connections
    initial_connections = count_backend_connections()

    # Spawn 10 clients watching same channel
    clients = [
        start_stream_client(channel_id=1)
        for _ in range(10)
    ]

    await asyncio.sleep(5)  # Let streams stabilize

    final_connections = count_backend_connections()

    # Should only have 1 backend connection
    assert final_connections - initial_connections == 1

    # All clients should be receiving data
    for client in clients:
        assert client.is_receiving_data()

async def test_failover_during_sharing():
    """Verify failover works with shared streams"""
    # Start 5 clients on channel 1
    clients = [start_stream_client(1) for _ in range(5)]

    # Simulate primary stream failure
    await kill_stream_source(channel_id=1, stream_order=1)

    # Should automatically failover to backup
    await asyncio.sleep(2)

    # All clients should still be receiving data
    for client in clients:
        assert client.is_receiving_data()
        assert client.no_interruption()
```

**Load Testing**:
```bash
# Simulate 100 concurrent clients on 10 channels
./load_test.sh --clients 100 --channels 10 --duration 60s

# Expected results:
# - Backend connections: ~10 (not 100)
# - Bandwidth usage: ~10x stream bitrate (not 100x)
# - All clients receive data successfully
```

**Success Metrics**:
- ✅ Bandwidth reduced by 90% (100 clients → 10 connections)
- ✅ Zero interruptions during failover
- ✅ Memory usage stable

---

### 1.2 Grace Period Failover (Days 5-6)

**Objective**: Prevent unnecessary failovers during brief provider hiccups

**Priority**: ⭐⭐⭐⭐ HIGH

**Impact**:
- Smoother viewing experience (no interruptions)
- Reduced provider load (fewer reconnections)
- Better stream stability

#### Tasks

##### Task 1.2.1: Update Health Checker (Day 5)
**File**: `/backend/app/services/health_checker.py` (MODIFY)

**Add New Method**:
```python
@dataclass
class HealthCheckResult:
    is_alive: bool
    response_time: Optional[float]
    status_code: Optional[int]
    error: Optional[str]
    grace_recovery: bool = False  # NEW

class StreamHealthChecker:
    async def check_stream_with_grace(
        self,
        stream_url: str,
        grace_period_ms: int = 300,
        grace_timeout_secs: int = 2,
        method: str = "head"
    ) -> HealthCheckResult:
        """Check with grace period for transient failures"""

        # Initial check
        result = await self.check_stream(stream_url, method)

        if result.is_alive:
            return result

        # Stream appears down - wait grace period
        logger.info(f"Stream {stream_url} failed, waiting {grace_period_ms}ms grace period")
        await asyncio.sleep(grace_period_ms / 1000)

        # Retry within timeout window
        try:
            retry_result = await asyncio.wait_for(
                self.check_stream(stream_url, method),
                timeout=grace_timeout_secs
            )

            if retry_result.is_alive:
                logger.info(f"Stream {stream_url} RECOVERED during grace period")
                return HealthCheckResult(
                    is_alive=True,
                    response_time=retry_result.response_time,
                    status_code=retry_result.status_code,
                    error=None,
                    grace_recovery=True
                )
            else:
                logger.warning(f"Stream {stream_url} CONFIRMED DOWN after grace period")
                return retry_result

        except asyncio.TimeoutError:
            return HealthCheckResult(
                is_alive=False,
                response_time=None,
                status_code=None,
                error="Grace period timeout"
            )
```

**Testing**:
```python
async def test_grace_period_recovery():
    """Test stream recovers during grace period"""
    checker = StreamHealthChecker()

    # Mock stream that fails once, then recovers
    with mock_stream_response(
        first_response=500,  # Fail
        second_response=200  # Recover
    ):
        result = await checker.check_stream_with_grace(
            "http://test.m3u8",
            grace_period_ms=100
        )

        assert result.is_alive == True
        assert result.grace_recovery == True

async def test_grace_period_confirmed_failure():
    """Test stream stays down after grace period"""
    checker = StreamHealthChecker()

    # Mock stream that stays down
    with mock_stream_response(
        first_response=500,
        second_response=500
    ):
        result = await checker.check_stream_with_grace(
            "http://test.m3u8",
            grace_period_ms=100
        )

        assert result.is_alive == False
        assert result.grace_recovery == False
```

**Success Metrics**:
- ✅ Grace period logic works correctly
- ✅ False positives reduced

---

##### Task 1.2.2: Add Settings Configuration (Day 5)
**File**: `/backend/app/models/settings.py` (MODIFY)

**Add New Settings**:
```python
DEFAULT_SETTINGS = {
    # ... existing settings ...

    # Grace Period Configuration
    "enable_grace_period": True,
    "grace_period_ms": 300,  # Wait 300ms before declaring failure
    "grace_timeout_secs": 2,  # Max 2 seconds for recovery attempt
    "grace_period_applies_to": "all",  # "all", "live_only", "vod_only"
}
```

**UI**: Add to Settings page
```typescript
// /frontend/src/pages/Settings.tsx
<SettingsSection title="Failover Configuration">
    <Toggle
        label="Enable Grace Period"
        value={settings.enable_grace_period}
        onChange={handleChange}
    />
    <NumberInput
        label="Grace Period (milliseconds)"
        value={settings.grace_period_ms}
        min={100}
        max={2000}
        step={100}
        disabled={!settings.enable_grace_period}
    />
    <NumberInput
        label="Grace Timeout (seconds)"
        value={settings.grace_timeout_secs}
        min={1}
        max={10}
        disabled={!settings.enable_grace_period}
    />
</SettingsSection>
```

---

##### Task 1.2.3: Update Health Check Tasks (Day 6)
**File**: `/backend/app/tasks/health_tasks.py` (MODIFY)

**Update Task**:
```python
@celery.task
async def check_provider_health(provider_id: int):
    """Check all streams for provider with grace period"""

    settings = await get_settings()
    grace_enabled = settings.get("enable_grace_period", True)

    streams = await get_provider_streams(provider_id)
    checker = StreamHealthChecker()

    grace_recoveries = 0
    confirmed_failures = 0

    for stream in streams:
        if grace_enabled:
            result = await checker.check_stream_with_grace(
                stream.stream_url,
                grace_period_ms=settings.get("grace_period_ms", 300),
                grace_timeout_secs=settings.get("grace_timeout_secs", 2)
            )
        else:
            result = await checker.check_stream(stream.stream_url)

        # Update database
        if result.is_alive:
            stream.consecutive_failures = 0
            stream.last_success = datetime.utcnow()

            if result.grace_recovery:
                grace_recoveries += 1
                logger.info(f"Stream {stream.id} recovered via grace period")
        else:
            stream.consecutive_failures += 1
            stream.last_failure = datetime.utcnow()
            stream.failure_reason = result.error

            if stream.consecutive_failures >= 3:
                stream.is_active = False
                confirmed_failures += 1

        stream.last_check = datetime.utcnow()
        stream.response_time = result.response_time

        await db.commit()

    # Log summary
    logger.info(
        f"Provider {provider_id} health check complete: "
        f"{grace_recoveries} grace recoveries, "
        f"{confirmed_failures} confirmed failures"
    )
```

**Success Metrics**:
- ✅ Grace recoveries logged correctly
- ✅ False failures eliminated

---

##### Task 1.2.4: Add Analytics Tracking (Day 6)
**File**: `/backend/app/models/analytics.py` (NEW)

**Track Grace Period Metrics**:
```python
class StreamHealthEvent(Base):
    __tablename__ = "stream_health_events"

    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("channel_streams.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # "check", "grace_recovery", "confirmed_failure"
    response_time = Column(Float)
    error = Column(String, nullable=True)
    grace_period_used = Column(Boolean, default=False)

# Analytics query
async def get_grace_period_effectiveness():
    """Calculate how often grace period prevents false failures"""

    total_checks = await db.scalar(
        select(func.count(StreamHealthEvent.id))
        .where(StreamHealthEvent.event_type == "check")
    )

    grace_recoveries = await db.scalar(
        select(func.count(StreamHealthEvent.id))
        .where(StreamHealthEvent.event_type == "grace_recovery")
    )

    return {
        "total_checks": total_checks,
        "grace_recoveries": grace_recoveries,
        "false_positive_reduction": f"{(grace_recoveries / total_checks * 100):.1f}%"
    }
```

---

### 1.3 HLS Advanced Buffering (Days 7-10)

**Objective**: Provide superior M3U8 stream playback with intelligent buffering

**Priority**: ⭐⭐⭐⭐ HIGH

**Impact**:
- Smoother HLS playback (pre-buffered segments)
- Automatic quality selection (best variant)
- Reduced latency (cached segments)

#### Tasks

##### Task 1.3.1: Install Dependencies (Day 7)
**File**: `/backend/requirements.txt` (MODIFY)

```txt
# Add HLS support
m3u8==3.5.0  # M3U8 playlist parsing
```

```bash
pip install m3u8
```

---

##### Task 1.3.2: Create HLS Proxy Service (Days 7-8)
**File**: `/backend/app/services/hls_proxy.py` (NEW)

**Implementation**:
```python
import m3u8
import aiohttp
from typing import AsyncGenerator, Optional
from collections import OrderedDict

class HLSStreamProxy:
    """Advanced HLS proxy with buffering and quality selection"""

    def __init__(
        self,
        playlist_url: str,
        buffer_size_mb: int = 10,
        quality_preference: str = "best"  # "best", "auto", "worst"
    ):
        self.playlist_url = playlist_url
        self.buffer_size = buffer_size_mb * 1024 * 1024
        self.quality_preference = quality_preference
        self.segment_cache = OrderedDict()  # LRU cache
        self.max_cached_segments = 50

    async def get_stream(self) -> AsyncGenerator[bytes, None]:
        """Stream HLS with intelligent buffering"""

        # Parse master playlist
        playlist = m3u8.load(self.playlist_url)

        if playlist.is_variant:
            # Multi-quality playlist - select variant
            variant = self._select_variant(playlist)
            variant_url = self._make_absolute_url(variant.uri, self.playlist_url)
            variant_playlist = m3u8.load(variant_url)
        else:
            # Single quality playlist
            variant_playlist = playlist

        # Stream segments with buffering
        for segment in variant_playlist.segments:
            segment_url = self._make_absolute_url(
                segment.uri,
                variant_url if playlist.is_variant else self.playlist_url
            )

            segment_data = await self._fetch_segment_with_cache(segment_url)

            # Yield in chunks
            chunk_size = 8192
            for i in range(0, len(segment_data), chunk_size):
                yield segment_data[i:i + chunk_size]

    def _select_variant(self, playlist: m3u8.M3U8) -> m3u8.Playlist:
        """Select best quality variant based on preference"""

        if not playlist.playlists:
            raise ValueError("No variants found in playlist")

        if self.quality_preference == "best":
            # Highest bandwidth
            return max(
                playlist.playlists,
                key=lambda p: p.stream_info.bandwidth or 0
            )
        elif self.quality_preference == "worst":
            # Lowest bandwidth
            return min(
                playlist.playlists,
                key=lambda p: p.stream_info.bandwidth or float('inf')
            )
        else:  # "auto"
            # Smart selection based on network conditions
            # For now, select middle quality
            sorted_playlists = sorted(
                playlist.playlists,
                key=lambda p: p.stream_info.bandwidth or 0
            )
            return sorted_playlists[len(sorted_playlists) // 2]

    async def _fetch_segment_with_cache(self, segment_url: str) -> bytes:
        """Fetch segment with LRU cache"""

        # Check cache
        if segment_url in self.segment_cache:
            # Move to end (most recently used)
            self.segment_cache.move_to_end(segment_url)
            return self.segment_cache[segment_url]

        # Fetch from source
        async with aiohttp.ClientSession() as session:
            async with session.get(segment_url, timeout=10) as resp:
                if resp.status != 200:
                    raise Exception(f"Segment fetch failed: {resp.status}")

                data = await resp.read()

        # Add to cache
        self.segment_cache[segment_url] = data

        # Evict oldest if cache full
        while len(self.segment_cache) > self.max_cached_segments:
            self.segment_cache.popitem(last=False)

        return data

    def _make_absolute_url(self, uri: str, base_url: str) -> str:
        """Convert relative URL to absolute"""
        if uri.startswith('http://') or uri.startswith('https://'):
            return uri

        from urllib.parse import urljoin
        return urljoin(base_url, uri)
```

**Testing**:
```python
async def test_hls_variant_selection():
    """Test quality variant selection"""
    proxy = HLSStreamProxy(
        "http://test.m3u8",
        quality_preference="best"
    )

    # Mock multi-quality playlist
    with mock_hls_playlist(variants=[
        {"bandwidth": 1000000, "resolution": "640x360"},
        {"bandwidth": 3000000, "resolution": "1280x720"},
        {"bandwidth": 6000000, "resolution": "1920x1080"},
    ]):
        variant = proxy._select_variant(...)
        assert variant.stream_info.bandwidth == 6000000

async def test_segment_caching():
    """Test segment LRU cache"""
    proxy = HLSStreamProxy("http://test.m3u8")
    proxy.max_cached_segments = 3

    # Fetch 5 segments
    for i in range(5):
        await proxy._fetch_segment_with_cache(f"http://test/seg{i}.ts")

    # Should only have last 3 cached
    assert len(proxy.segment_cache) == 3
    assert "http://test/seg4.ts" in proxy.segment_cache
    assert "http://test/seg0.ts" not in proxy.segment_cache
```

---

##### Task 1.3.3: Detect HLS Streams (Day 8)
**File**: `/backend/app/services/stream_detector.py` (NEW)

**Implementation**:
```python
def is_hls_stream(stream_url: str) -> bool:
    """Detect if stream is HLS format"""

    url_lower = stream_url.lower()

    # Check file extension
    if url_lower.endswith('.m3u8') or url_lower.endswith('.m3u'):
        return True

    # Check for m3u8 in path or query params
    if 'm3u8' in url_lower:
        return True

    # Check for HLS indicators
    hls_indicators = ['hls', 'playlist.m3u8', 'index.m3u8']
    if any(indicator in url_lower for indicator in hls_indicators):
        return True

    return False

async def detect_stream_type(stream_url: str) -> str:
    """Detect stream type: hls, rtmp, http, etc."""

    if is_hls_stream(stream_url):
        return "hls"
    elif stream_url.startswith('rtmp://'):
        return "rtmp"
    elif stream_url.startswith('rtsp://'):
        return "rtsp"
    else:
        return "http"
```

---

##### Task 1.3.4: Integrate HLS Proxy (Day 9)
**File**: `/backend/app/api/hdhr.py` (MODIFY)

**Update Endpoint**:
```python
from app.services.hls_proxy import HLSStreamProxy
from app.services.stream_detector import is_hls_stream

@router.get("/auto/v{channel_id}")
async def stream_channel(channel_id: int):
    """Stream channel with HLS detection"""

    stream = await get_best_stream(channel_id)

    # Detect stream type
    if is_hls_stream(stream.stream_url):
        # Use HLS proxy
        settings = await get_settings()

        hls_proxy = HLSStreamProxy(
            stream.stream_url,
            buffer_size_mb=settings.get("hls_buffer_size_mb", 10),
            quality_preference=settings.get("hls_quality_preference", "best")
        )

        return StreamingResponse(
            hls_proxy.get_stream(),
            media_type="video/mp2t",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Use standard connection sharing proxy
        proxy = await stream_manager.get_or_create_stream(
            stream.stream_url,
            channel_id
        )

        # ... existing code ...
```

---

##### Task 1.3.5: Add HLS Settings (Day 9)
**File**: `/backend/app/models/settings.py` (MODIFY)

```python
DEFAULT_SETTINGS = {
    # ... existing ...

    # HLS Configuration
    "hls_buffer_size_mb": 10,  # RAM buffer per stream
    "hls_quality_preference": "best",  # "best", "auto", "worst"
    "hls_segment_cache_size": 50,  # Number of segments to cache
    "hls_enable_adaptive": False,  # Future: adaptive bitrate
}
```

**UI**:
```typescript
// /frontend/src/pages/Settings.tsx
<SettingsSection title="HLS Streaming">
    <NumberInput
        label="Buffer Size (MB)"
        value={settings.hls_buffer_size_mb}
        min={5}
        max={50}
    />
    <Select
        label="Quality Preference"
        value={settings.hls_quality_preference}
        options={[
            { value: "best", label: "Best Quality" },
            { value: "auto", label: "Auto (Medium)" },
            { value: "worst", label: "Lowest Quality" },
        ]}
    />
    <NumberInput
        label="Segment Cache Size"
        value={settings.hls_segment_cache_size}
        min={10}
        max={100}
    />
</SettingsSection>
```

---

##### Task 1.3.6: Testing & Validation (Day 10)
**File**: `/backend/tests/test_hls_proxy.py` (NEW)

**Test Scenarios**:
```python
async def test_hls_playback():
    """Test HLS stream playback"""
    proxy = HLSStreamProxy("http://test/playlist.m3u8")

    chunks_received = 0
    async for chunk in proxy.get_stream():
        chunks_received += 1
        if chunks_received >= 100:  # Test first 100 chunks
            break

    assert chunks_received == 100

async def test_hls_quality_selection():
    """Test different quality preferences"""
    for quality in ["best", "auto", "worst"]:
        proxy = HLSStreamProxy(
            "http://test/playlist.m3u8",
            quality_preference=quality
        )
        # Verify correct variant selected
        # ...

async def test_hls_segment_caching():
    """Test cache reduces redundant fetches"""
    proxy = HLSStreamProxy("http://test/playlist.m3u8")

    # Mock segment fetch counter
    with mock_segment_fetcher() as mock:
        # Stream twice
        async for _ in proxy.get_stream():
            pass
        async for _ in proxy.get_stream():
            pass

        # Should fetch each segment only once (cached)
        assert mock.fetch_count < mock.total_segments * 2
```

**Manual Testing**:
```bash
# Test with real HLS stream
curl "http://localhost:8000/auto/v1" > test.ts
ffprobe test.ts  # Verify valid transport stream

# Test with VLC
vlc http://localhost:8000/auto/v1

# Test with Plex
# Add HDHomeRun device: http://localhost:8000
# Play channel
```

**Success Metrics**:
- ✅ Smooth HLS playback
- ✅ Correct quality variant selected
- ✅ Segment caching working
- ✅ No buffering interruptions

---

### Phase 1 Completion Checklist

**Day 10 Review**:
- [ ] Stream connection sharing deployed
- [ ] Bandwidth usage reduced by 50%+ (verified via monitoring)
- [ ] Grace period preventing false failovers (check analytics)
- [ ] HLS streams playing smoothly
- [ ] All unit tests passing
- [ ] Load tests successful (100+ concurrent clients)
- [ ] Documentation updated
- [ ] Code reviewed and merged

**Success Metrics**:
- ✅ Bandwidth usage: **DOWN 50-90%**
- ✅ False failovers: **DOWN 70%+**
- ✅ HLS buffering issues: **ELIMINATED**
- ✅ User complaints: **DOWN significantly**

---

## PHASE 2: User Experience Enhancements (Weeks 3-4)

### Goal: Professional monitoring and user control

---

### 2.1 Real-time Monitoring Dashboard (Days 11-15)

**Objective**: Provide live visibility into system health and performance

**Priority**: ⭐⭐⭐⭐ HIGH

#### Tasks

##### Task 2.1.1: Create WebSocket Stats Endpoint (Day 11)
**File**: `/backend/app/api/websocket.py` (NEW)

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Connection closed
                pass

manager = ConnectionManager()

@router.websocket("/ws/stats")
async def stream_stats_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Gather stats
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "streams": {
                    "active": len(stream_manager.active_streams),
                    "total_clients": sum(
                        s.client_count
                        for s in stream_manager.active_streams.values()
                    ),
                    "bandwidth_mbps": calculate_total_bandwidth(),
                },
                "channels": {
                    "total": await count_channels(),
                    "active": await count_active_channels(),
                    "failed": await count_failed_channels(),
                },
                "providers": {
                    "total": await count_providers(),
                    "healthy": await count_healthy_providers(),
                    "syncing": await count_syncing_providers(),
                },
                "top_channels": await get_top_channels(limit=10),
            }

            await websocket.send_json(stats)
            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

##### Task 2.1.2: Create React Dashboard Components (Days 12-13)
**File**: `/frontend/src/components/Dashboard/RealTimeStats.tsx` (NEW)

```typescript
import { useWebSocket } from 'react-use-websocket';
import { Line } from 'react-chartjs-2';

export const RealTimeStats = () => {
    const { lastJsonMessage, connectionStatus } = useWebSocket(
        'ws://localhost:8000/ws/stats',
        {
            shouldReconnect: () => true,
            reconnectInterval: 3000,
        }
    );

    const stats = lastJsonMessage as StatsMessage;

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Active Streams Card */}
            <StatCard
                title="Active Streams"
                value={stats?.streams?.active || 0}
                icon={<PlayIcon />}
                trend={calculateTrend(stats?.streams?.active)}
                color="blue"
            />

            {/* Total Clients Card */}
            <StatCard
                title="Connected Clients"
                value={stats?.streams?.total_clients || 0}
                icon={<UsersIcon />}
                color="green"
            />

            {/* Bandwidth Card */}
            <StatCard
                title="Bandwidth"
                value={`${stats?.streams?.bandwidth_mbps || 0} Mbps`}
                icon={<CloudIcon />}
                color="purple"
            />

            {/* Failed Channels Card */}
            <StatCard
                title="Failed Channels"
                value={stats?.channels?.failed || 0}
                icon={<AlertIcon />}
                color="red"
                alert={stats?.channels?.failed > 0}
            />

            {/* Bandwidth Chart */}
            <div className="col-span-full">
                <BandwidthChart data={stats} />
            </div>

            {/* Top Channels List */}
            <div className="col-span-full lg:col-span-2">
                <TopChannelsList channels={stats?.top_channels || []} />
            </div>

            {/* Provider Status */}
            <div className="col-span-full lg:col-span-2">
                <ProviderStatusList providers={stats?.providers || []} />
            </div>
        </div>
    );
};
```

---

##### Task 2.1.3: Add Live Activity Feed (Day 14)
**File**: `/frontend/src/components/Dashboard/ActivityFeed.tsx` (NEW)

```typescript
export const ActivityFeed = () => {
    const [activities, setActivities] = useState<Activity[]>([]);

    useWebSocket('ws://localhost:8000/ws/activity', {
        onMessage: (event) => {
            const activity = JSON.parse(event.data);
            setActivities(prev => [activity, ...prev].slice(0, 50));
        }
    });

    return (
        <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold mb-4">Live Activity</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
                {activities.map(activity => (
                    <ActivityItem key={activity.id} activity={activity} />
                ))}
            </div>
        </div>
    );
};

const ActivityItem = ({ activity }) => {
    const icons = {
        'stream_start': <PlayIcon className="text-green-500" />,
        'stream_stop': <StopIcon className="text-gray-500" />,
        'failover': <AlertIcon className="text-yellow-500" />,
        'provider_sync': <RefreshIcon className="text-blue-500" />,
        'health_check': <CheckIcon className="text-green-500" />,
    };

    return (
        <div className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded">
            {icons[activity.type]}
            <div className="flex-1">
                <p className="text-sm">{activity.message}</p>
                <p className="text-xs text-gray-500">
                    {formatTimeAgo(activity.timestamp)}
                </p>
            </div>
        </div>
    );
};
```

---

##### Task 2.1.4: Add System Health Indicators (Day 15)
**File**: `/frontend/src/components/Dashboard/SystemHealth.tsx` (NEW)

```typescript
export const SystemHealth = () => {
    const { data: health } = useQuery('systemHealth', fetchSystemHealth, {
        refetchInterval: 5000  // Every 5 seconds
    });

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Database Health */}
            <HealthIndicator
                name="Database"
                status={health?.database?.status}
                metrics={{
                    'Response Time': `${health?.database?.response_time_ms}ms`,
                    'Connections': `${health?.database?.active_connections}/${health?.database?.max_connections}`,
                }}
            />

            {/* Redis Health */}
            <HealthIndicator
                name="Redis"
                status={health?.redis?.status}
                metrics={{
                    'Response Time': `${health?.redis?.response_time_ms}ms`,
                    'Memory Usage': `${health?.redis?.memory_usage_mb}MB`,
                }}
            />

            {/* Celery Workers */}
            <HealthIndicator
                name="Background Jobs"
                status={health?.celery?.status}
                metrics={{
                    'Active Workers': health?.celery?.active_workers,
                    'Queue Size': health?.celery?.queue_size,
                }}
            />
        </div>
    );
};
```

---

### 2.2 Notification System (Days 16-18)

**Objective**: Proactive alerts for system events

**Priority**: ⭐⭐⭐ MEDIUM

#### Tasks

##### Task 2.2.1: Install Apprise (Day 16)
```bash
pip install apprise==1.6.0
```

##### Task 2.2.2: Create Notification Manager (Day 16)
**File**: `/backend/app/services/notification_manager.py` (NEW)

```python
import apprise
from typing import Optional

class NotificationManager:
    def __init__(self):
        self.apprise = apprise.Apprise()
        self.enabled = False

    async def initialize(self):
        """Load notification endpoints from settings"""
        settings = await get_settings()

        # Telegram
        if settings.get("telegram_enabled"):
            bot_token = settings["telegram_bot_token"]
            chat_id = settings["telegram_chat_id"]
            self.apprise.add(f"tgram://{bot_token}/{chat_id}")

        # Pushover
        if settings.get("pushover_enabled"):
            user_key = settings["pushover_user_key"]
            api_token = settings["pushover_api_token"]
            self.apprise.add(f"pover://{user_key}@{api_token}")

        # Email
        if settings.get("email_enabled"):
            smtp_url = settings["smtp_url"]
            self.apprise.add(smtp_url)

        # Webhook
        if settings.get("webhook_enabled"):
            webhook_url = settings["webhook_url"]
            self.apprise.add(webhook_url)

        self.enabled = len(self.apprise) > 0

    async def send(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        attach: Optional[str] = None
    ):
        """Send notification via all configured channels"""

        if not self.enabled:
            return

        await self.apprise.async_notify(
            title=title,
            body=message,
            notify_type=notification_type,  # info, success, warning, failure
            attach=attach
        )

# Global instance
notification_manager = NotificationManager()
```

---

##### Task 2.2.3: Add Notification Triggers (Day 17)
**File**: `/backend/app/services/notification_triggers.py` (NEW)

```python
async def notify_provider_failure(provider_id: int):
    """Notify when provider fails health check"""
    provider = await get_provider(provider_id)

    await notification_manager.send(
        title=f"🔴 Provider Failure: {provider.name}",
        message=(
            f"Provider {provider.name} has failed health check.\n"
            f"Active channels affected: {provider.active_channels}\n"
            f"Last successful check: {provider.last_health_check}"
        ),
        notification_type="failure"
    )

async def notify_stream_recovered(stream_id: int):
    """Notify when failed stream recovers"""
    stream = await get_stream(stream_id)

    await notification_manager.send(
        title=f"✅ Stream Recovered: {stream.channel.name}",
        message=f"Stream for {stream.channel.name} has recovered and is now active.",
        notification_type="success"
    )

async def notify_daily_summary():
    """Send daily health summary"""
    stats = await get_daily_stats()

    message = f"""
📊 Daily Summary

Streams:
- Total active: {stats['active_streams']}
- Failed today: {stats['failed_streams']}
- Grace recoveries: {stats['grace_recoveries']}

Providers:
- Healthy: {stats['healthy_providers']}
- Failed: {stats['failed_providers']}

Top Channels:
{format_top_channels(stats['top_channels'])}
"""

    await notification_manager.send(
        title="📊 Daily Summary",
        message=message,
        notification_type="info"
    )
```

---

##### Task 2.2.4: Add Settings UI (Day 18)
**File**: `/frontend/src/pages/Settings/Notifications.tsx` (NEW)

```typescript
export const NotificationSettings = () => {
    const [settings, setSettings] = useState({});

    return (
        <div className="space-y-6">
            {/* Telegram */}
            <Section title="Telegram">
                <Toggle
                    label="Enable Telegram Notifications"
                    value={settings.telegram_enabled}
                />
                <Input
                    label="Bot Token"
                    value={settings.telegram_bot_token}
                    type="password"
                    disabled={!settings.telegram_enabled}
                />
                <Input
                    label="Chat ID"
                    value={settings.telegram_chat_id}
                    disabled={!settings.telegram_enabled}
                />
                <Button onClick={testTelegram}>Test Telegram</Button>
            </Section>

            {/* Pushover */}
            <Section title="Pushover">
                {/* Similar fields */}
            </Section>

            {/* Email */}
            <Section title="Email">
                <Toggle label="Enable Email Notifications" />
                <Input label="SMTP Server" placeholder="smtp.gmail.com:587" />
                <Input label="From Address" type="email" />
                <Input label="To Address" type="email" />
                <Input label="Username" />
                <Input label="Password" type="password" />
            </Section>

            {/* Notification Triggers */}
            <Section title="Triggers">
                <Checkbox label="Provider failures" checked />
                <Checkbox label="Stream recoveries" checked />
                <Checkbox label="Daily summary" checked />
                <Checkbox label="Sync completions" />
                <Checkbox label="Health check alerts" checked />
            </Section>
        </div>
    );
};
```

---

### 2.3 Backup Channel Assignment UI (Days 19-20)

**Objective**: Let users explicitly configure backup streams

**Priority**: ⭐⭐⭐ MEDIUM

#### Tasks

##### Task 2.3.1: Add Database Field (Day 19)
**Migration**: `/backend/alembic/versions/xxxx_add_backup_order.py`

```python
def upgrade():
    op.add_column(
        'channel_streams',
        sa.Column('backup_order', sa.Integer, nullable=False, server_default='0')
    )
    # 0 = primary, 1-3 = backups

def downgrade():
    op.drop_column('channel_streams', 'backup_order')
```

---

##### Task 2.3.2: Create Drag-and-Drop UI (Day 20)
**File**: `/frontend/src/components/Channels/StreamPriorityManager.tsx` (NEW)

```typescript
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

export const StreamPriorityManager = ({ channel }) => {
    const [streams, setStreams] = useState(channel.streams);

    const onDragEnd = (result) => {
        if (!result.destination) return;

        const items = Array.from(streams);
        const [reordered] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reordered);

        // Update backup_order
        const updated = items.map((stream, index) => ({
            ...stream,
            backup_order: index
        }));

        setStreams(updated);
        saveStreamOrder(channel.id, updated);
    };

    return (
        <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="streams">
                {(provided) => (
                    <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className="space-y-2"
                    >
                        {streams.map((stream, index) => (
                            <Draggable
                                key={stream.id}
                                draggableId={String(stream.id)}
                                index={index}
                            >
                                {(provided) => (
                                    <div
                                        ref={provided.innerRef}
                                        {...provided.draggableProps}
                                        {...provided.dragHandleProps}
                                        className="flex items-center gap-3 p-3 bg-white rounded shadow"
                                    >
                                        <DragIcon className="text-gray-400" />
                                        <Badge color={index === 0 ? 'green' : 'gray'}>
                                            {index === 0 ? 'Primary' : `Backup ${index}`}
                                        </Badge>
                                        <div className="flex-1">
                                            <p className="font-medium">{stream.provider.name}</p>
                                            <p className="text-sm text-gray-500">
                                                {stream.resolution} • {stream.quality_score} points
                                            </p>
                                        </div>
                                        <HealthBadge stream={stream} />
                                    </div>
                                )}
                            </Draggable>
                        ))}
                        {provided.placeholder}
                    </div>
                )}
            </Droppable>
        </DragDropContext>
    );
};
```

---

### Phase 2 Completion Checklist

**Day 20 Review**:
- [ ] Real-time dashboard operational
- [ ] WebSocket connections stable
- [ ] Notifications configured and tested
- [ ] Backup channel UI functional
- [ ] All features documented

**Success Metrics**:
- ✅ Dashboard updates: **< 1 second latency**
- ✅ Notification delivery: **< 30 seconds**
- ✅ User satisfaction: **Significantly improved**

---

## PHASE 3: Advanced Features (Weeks 5-6)

### 3.1 Bandwidth Throttling (Days 21-23)
### 3.2 Xtream Codes Output (Days 24-28)
### 3.3 Enhanced Channel Grouping (Days 29-30)

*(Detailed tasks similar to above phases)*

---

## PHASE 4: Polish & Launch (Week 7)

### 4.1 Load Testing (Days 31-32)
### 4.2 Documentation (Day 33)
### 4.3 Production Deployment (Days 34-35)

---

## Timeline Summary

| Week | Phase | Focus | Deliverables |
|------|-------|-------|--------------|
| 1-2 | Phase 1 | Core Optimizations | Stream sharing, Grace period, HLS buffering |
| 3-4 | Phase 2 | User Experience | Dashboard, Notifications, Backup UI |
| 5-6 | Phase 3 | Advanced Features | Throttling, Xtream output, Grouping |
| 7 | Phase 4 | Launch | Testing, Docs, Deployment |

---

## Resource Requirements

**Team**: 1-2 developers
**Infrastructure**: Current (Docker, PostgreSQL, Redis)
**Dependencies**: m3u8, apprise, react-beautiful-dnd
**Budget**: $0 (all open source)

---

## Risk Mitigation

**Risk**: Breaking existing functionality
**Mitigation**: Comprehensive testing, feature flags, gradual rollout

**Risk**: Performance degradation
**Mitigation**: Load testing, monitoring, rollback plan

**Risk**: User adoption
**Mitigation**: Documentation, tutorials, migration guides

---

## Success Criteria

1. ✅ Bandwidth usage reduced by 50%+
2. ✅ Zero critical bugs in production
3. ✅ User satisfaction score > 90%
4. ✅ Competitive parity with Channels DVR
5. ✅ 100% feature coverage from comparison doc

---

## Next Steps

1. Review and approve this plan
2. Set up project tracking (GitHub Projects / Jira)
3. Begin Phase 1, Task 1.1.1 (Stream Proxy)
4. Weekly progress reviews
5. Iterate based on feedback

**Ready to begin implementation?** 🚀
