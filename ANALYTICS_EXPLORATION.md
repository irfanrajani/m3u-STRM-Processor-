# M3U-STRM-Processor Analytics & Monitoring Exploration

## Executive Summary

The M3U-STRM-Processor has a **solid but limited analytics infrastructure** with viewing history tracking at the core, combined with basic stream health monitoring and quality analysis. However, there are significant gaps in provider performance metrics, advanced analytics capabilities, and business intelligence features.

---

## 1. CURRENT ANALYTICS CAPABILITIES

### 1.1 Viewing History Tracking

**What's Captured:**
- User viewing sessions (start time, end time)
- Content viewed (channel, VOD movie, or series)
- Duration of viewing (in seconds)
- Completion status (completed vs in-progress)
- Stream URL used
- Per-user history with pagination support

**Storage Location:**
- Database table: `viewing_history`
- Indexed on: `user_id`, `started_at`, `channel_id`

**Key Metrics Available:**
```sql
-- Total views by user
SELECT COUNT(*) FROM viewing_history WHERE user_id = ?

-- Total watch time
SELECT SUM(duration_seconds) FROM viewing_history WHERE user_id = ?

-- Channels watched
SELECT COUNT(DISTINCT channel_id) FROM viewing_history WHERE user_id = ?

-- Completion rate
SELECT 
  COUNT(*) as total_views,
  SUM(CASE WHEN completed = true THEN 1 ELSE 0 END) as completed_views
FROM viewing_history
```

### 1.2 User Behavior Analytics

**Tracked Behaviors:**
1. **Viewing Preferences**
   - Most watched channels (by view count and duration)
   - Content type preferences (channels vs movies vs series)
   - Average watch time per session

2. **User Activity Patterns**
   - Last login timestamp (captured in `users` table)
   - Historical viewing data (30/90/365 day queries available)
   - Viewing trend analysis (with configurable time ranges)

3. **Currently Missing:**
   - Peak viewing times (hour of day, day of week)
   - Session frequency patterns
   - Content switching behavior
   - Abandonment rates
   - Re-watch patterns

### 1.3 Channel Popularity Tracking

**API Endpoint:** `GET /api/analytics/popular?days=7&limit=10`

**Metrics Available:**
```python
PopularChannel(
    channel_id: int,
    channel_name: str,
    view_count: int,              # Total views
    total_watch_time_seconds: int, # Aggregate watch time
    unique_viewers: int            # Distinct users who watched
)
```

**Database Query Used:**
```sql
SELECT 
    vh.channel_id,
    c.name,
    COUNT(vh.id) as view_count,
    SUM(vh.duration_seconds) as total_watch_time,
    COUNT(DISTINCT vh.user_id) as unique_viewers
FROM viewing_history vh
JOIN channels c ON vh.channel_id = c.id
WHERE vh.started_at >= DATE_SUB(NOW(), INTERVAL ? DAY)
GROUP BY vh.channel_id, c.name
ORDER BY view_count DESC
LIMIT ?
```

**Limitations:**
- No temporal breakdown (hourly/daily/weekly trends)
- No genre-based popularity
- No regional/category filtering
- No concurrent viewership metrics

### 1.4 Provider Performance Metrics

**Stored in `providers` table:**
- `total_channels` - Number of channels from provider
- `active_channels` - Currently working channels
- `total_vod_movies` - Available movies
- `total_vod_series` - Available series
- `last_sync` - Last synchronization time
- `last_health_check` - Last health check execution

**Currently Exposed via API:**
```python
ProviderResponse(
    id: int,
    name: str,
    enabled: bool,
    priority: int,
    total_channels: int,
    active_channels: int,
    total_vod_movies: int,
    total_vod_series: int
)
```

**Missing Provider Metrics:**
- Sync duration/speed
- Data freshness (age of content)
- Error rates during sync
- Channel source changes
- Provider availability trends

### 1.5 Stream Quality Metrics

**Captured per Stream (ChannelStream table):**
```
resolution          # 1080p, 720p, 4K, etc.
bitrate             # in kbps
codec               # h264, h265, etc.
fps                 # frames per second
quality_score       # Calculated 0-1000 score
```

**Quality Analysis Methods:**
1. **Name-based Detection** (Fastest)
   - Regex extraction from stream/channel name
   - Priority hierarchy: 8K > 4K > 2160p > 1440p > 1080p > 720p > 480p > 360p

2. **URL-based Detection**
   - Extracts resolution from stream URL
   - Fallback if name detection fails

3. **FFprobe Analysis** (Slowest, Most Accurate)
   - Extracts actual codec, bitrate, resolution from stream
   - Timeout: 15 seconds
   - Command: `ffprobe -select_streams v:0 -show_entries stream= -of json`

**Quality Score Calculation:**
```python
RESOLUTION_PRIORITY = {
    "8K": 1000,
    "4K": 900,
    "1080p": 700,
    "720p": 600,
    "480p": 400,
}

QUALITY_BITRATES = {
    "4K": 15000,      # kbps
    "1080p": 5000,
    "720p": 2500,
    "480p": 1000,
}

score = resolution_priority
if bitrate >= expected_bitrate:
    score += 50  # Bonus for meeting bitrate
else:
    score *= (bitrate / expected_bitrate)  # Penalty for low bitrate
```

**Not Tracked:**
- Bitrate variations over time
- Codec efficiency comparisons
- Performance degradation trends
- Quality per provider comparison

### 1.6 Stream Health Metrics

**Stored in `channel_streams` table:**
```
is_active                 # Boolean - actively working
last_check                # Last health check timestamp
consecutive_failures      # Failure streak counter
response_time            # Last response time in ms
last_success             # Last successful check
last_failure             # Last failed check
failure_reason           # Error message
```

**Health Check Details:**
- **Timeout:** 10 seconds (configurable)
- **Concurrency:** 50 parallel checks
- **Methods:** HEAD request (preferred) → GET fallback
- **Accepted Status Codes:** 200, 206, 302, 301
- **Deactivation Threshold:** 3 consecutive failures

**Health Score Calculation:**
```python
def calculate_health_score(consecutive_failures, response_time, uptime_percentage):
    score = 100
    
    # Failure penalties (exponential)
    if consecutive_failures > 0:
        score -= min(50, consecutive_failures * 10)
    
    # Response time penalties
    if response_time > 5000ms:
        score -= 30
    elif response_time > 3000ms:
        score -= 20
    elif response_time > 1000ms:
        score -= 10
    
    # Historical uptime factor
    if uptime_percentage:
        score *= (uptime_percentage / 100)
    
    return max(0, min(100, score))
```

**Not Tracked:**
- Historical uptime trends
- Provider-level failure correlations
- Geographic failure patterns
- Peak failure times
- Recovery time metrics

### 1.7 System Health Metrics

**Available via `/api/system/health` and `/api/system/stats`:**

**Health Status:**
- Application status: "healthy"
- Database connection: "connected"
- Redis connection: "connected"
- App version

**System Stats:**
- Total providers
- Active providers
- Total channels
- Total VOD items (movies + series)
- Breakdown of movies vs series

**Not Tracked:**
- Database query performance
- API response times
- Memory/CPU usage
- Disk space
- Connection pool metrics
- Cache hit rates

---

## 2. DATA COLLECTION STRATEGY

### 2.1 Events Being Tracked

**High-Level Event Log:**

| Event Type | Location | Capture Method | Frequency |
|-----------|----------|-----------------|-----------|
| Viewing Start | analytics.py | API call | Per user session |
| Viewing Update | analytics.py | API call | On completion |
| Viewing End | analytics.py | API call (patch) | On stop/completion |
| Health Check | health_tasks.py | Scheduled task | Configurable (typically hourly) |
| Provider Sync | sync_tasks.py | Scheduled task | Configurable interval |
| User Login | user.py | Via auth | On authentication |

### 2.2 Data Granularity & Retention

**Current Retention Policy:**
- No explicit retention limits
- All historical data kept indefinitely
- Database queries support 1-365 day windows
- Time-based filtering at query time (not data age)

**Recommended Strategy:**
```sql
-- Data retention by table
viewing_history      -> Keep 2 years (with monthly rollups after 1 year)
channel_streams      -> Keep indefinitely (operational data)
health_check_log     -> Keep 6 months (high volume)
provider_sync_log    -> Keep 1 year (moderate volume)
```

### 2.3 Performance Impact of Tracking

**Viewing History Collection:**
- **Per Event Overhead:** ~50-100ms (single INSERT + transaction)
- **Storage:** ~500 bytes per entry
- **Query Performance:** Indexed queries on (user_id, started_at)
- **At Scale:** 1000 concurrent users → ~50 INSERTs/sec (acceptable)

**Health Checks:**
- **Batch Size:** 50 concurrent requests per 10 seconds
- **CPU Impact:** Low (async I/O bound)
- **Network Impact:** Moderate (HEAD/GET requests to streams)
- **Database Impact:** Moderate (50 UPDATE statements per batch)

**Recommendations:**
```python
# Implement connection pooling (already in place)
# Add query timeouts for analytics queries
# Consider partitioning viewing_history by month for large datasets
# Implement data archival after 2 years

# Celery task configuration
@periodic_task(run_every=crontab(hour=2, minute=0))
def archive_old_viewing_history():
    """Archive viewing history older than 2 years"""
    cutoff_date = datetime.now() - timedelta(days=730)
    # Move to analytics_archive table or compressed storage
```

### 2.4 Privacy Considerations

**Current Privacy Features:**
- User-scoped data isolation (users can only see own history)
- Password hashing (bcrypt)
- No sensitive data in URLs (stream URLs logged but masked in logs)
- Admin-only access to system-wide stats

**Privacy Gaps:**
```
⚠️ Stream URLs stored in viewing_history
⚠️ No data anonymization for long-term storage
⚠️ No audit logs for data access
⚠️ No GDPR "right to be forgotten" implementation
⚠️ No IP address tracking (good for privacy)
```

**Recommended Privacy Enhancements:**
```python
# 1. Add data masking for stream URLs
viewing_history.stream_url -> Hash(stream_url) with rotation

# 2. Implement data retention policies
class DataRetentionPolicy:
    VIEWING_HISTORY_RETENTION_DAYS = 730  # 2 years
    HEALTH_CHECK_RETENTION_DAYS = 180     # 6 months
    
# 3. Add audit logging
class AuditLog(Base):
    user_id: int
    action: str  # "viewed_analytics", "exported_data"
    resource: str
    timestamp: datetime
    details: JSON

# 4. GDPR compliance endpoint
@router.delete("/data/export")
async def request_data_export(user: User):
    """Export all user data for GDPR compliance"""
    
@router.delete("/data/purge")
async def purge_user_data(user: User):
    """Delete all user data on request"""
```

---

## 3. REPORTING AND VISUALIZATION

### 3.1 Available Dashboards

**Dashboard 1: Analytics Page** (`frontend/src/pages/Analytics.jsx`)

**User View:**
- Total views (configurable: 7/30/90 days)
- Watch time (hours:minutes format)
- Channels watched count
- Most popular channels (top 10 by view count)
- Recent viewing history (last 20 entries)

**Admin View (Additional):**
- Views today/week/month (system-wide)
- Active users today
- Most watched channels today
- System overview metrics

**Dashboard 2: Dashboard Page** (`frontend/src/pages/Dashboard.jsx`)

- Active providers count
- Active streams count
- VOD movies count
- VOD series count
- Quick action buttons (Sync, Health Check, Generate STRM)

**Dashboard 3: System Info Page** (`frontend/src/pages/SystemInfo.jsx`)

- HDHomeRun configuration
- Database statistics
- System details (app version, platform)
- Output paths

### 3.2 Data Aggregation Methods

**Current Aggregation Patterns:**

```python
# 1. Time-based aggregation (in analytics.py)
def get_user_stats(days: int = 30):
    since_date = datetime.utcnow() - timedelta(days=days)
    
    total_views = db.scalar(
        select(func.count(ViewingHistory.id))
        .where(ViewingHistory.user_id == user_id)
        .where(ViewingHistory.started_at >= since_date)
    )
    
    # Similar for: watch_time, channels_watched, movies_watched, series_watched

# 2. Group aggregation (Popular channels)
result = db.execute(
    select(
        ViewingHistory.channel_id,
        Channel.name,
        func.count(ViewingHistory.id).label('view_count'),
        func.sum(ViewingHistory.duration_seconds).label('total_watch_time'),
        func.count(func.distinct(ViewingHistory.user_id)).label('unique_viewers')
    )
    .join(Channel)
    .group_by(ViewingHistory.channel_id, Channel.name)
    .order_by(desc('view_count'))
    .limit(10)
)

# 3. System-wide aggregation (Admin stats)
views_today = db.scalar(
    select(func.count(ViewingHistory.id))
    .where(ViewingHistory.started_at >= today)
)
```

**Missing Aggregation Types:**
- Hourly breakdowns (for peak time analysis)
- Daily trends (for trend detection)
- Cohort analysis (user grouping by sign-up date)
- Retention metrics (return user rates)

### 3.3 Export Capabilities

**Current Status:** ❌ Not implemented

**Recommended Export Endpoints:**

```python
@router.get("/export/viewing-history")
async def export_viewing_history(
    format: str = "csv",  # csv, json, xlsx
    date_from: datetime,
    date_to: datetime,
    current_user: User = Depends(get_current_user)
):
    """Export user's viewing history"""

@router.get("/admin/export/analytics")
async def export_system_analytics(
    format: str = "csv",
    include: List[str] = ["views", "channels", "providers", "health"],
    admin_user: User = Depends(require_admin)
):
    """Export system-wide analytics"""
```

### 3.4 Real-Time vs Historical Data

**Real-Time Capabilities:**
- Health check status: Updates every check cycle (~1 hour)
- Viewing history: Immediate write on stream start
- Most watched (today): 5-minute granularity possible

**Historical Analysis:**
- 365-day window supported
- Time-based grouping in queries
- Manual data aggregation needed for hourly/daily trends

**Recommended Real-Time Improvements:**

```python
# WebSocket for real-time analytics
@app.websocket("/ws/analytics/live")
async def websocket_analytics(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # Every 30 seconds, push current metrics
        metrics = {
            "active_viewers": await get_current_active_viewers(),
            "most_watched_now": await get_trending_channels(),
            "stream_health": await get_health_summary(),
            "timestamp": datetime.utcnow()
        }
        await websocket.send_json(metrics)
        await asyncio.sleep(30)
```

---

## 4. GAPS AND OPPORTUNITIES

### 4.1 Critical Gaps

#### Gap #1: Provider Performance Analytics
**Severity: HIGH**

**Missing Metrics:**
- Provider uptime/downtime history
- Sync error rates and reasons
- Content freshness age
- Provider-specific stream quality distribution
- Provider reliability scoring

**Implementation:**
```sql
-- New table: provider_performance_logs
CREATE TABLE provider_performance_logs (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER,
    sync_timestamp DATETIME,
    sync_duration_seconds INTEGER,
    channels_added INTEGER,
    channels_removed INTEGER,
    channels_updated INTEGER,
    errors_count INTEGER,
    error_details TEXT,
    data_freshness_hours INTEGER,
    created_at DATETIME DEFAULT NOW()
);

-- Queries
SELECT 
    provider_id,
    AVG(sync_duration_seconds) as avg_sync_time,
    COUNT(*) as sync_count,
    SUM(errors_count) as total_errors,
    AVG(CAST(errors_count as FLOAT)) as error_rate
FROM provider_performance_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY provider_id;
```

#### Gap #2: Stream-Level Quality Degradation Tracking
**Severity: HIGH**

**Missing Metrics:**
- Quality score history per stream
- Bitrate variations over time
- Codec efficiency comparisons
- Geographic quality patterns (if applicable)
- Quality vs popularity correlation

**Implementation:**
```python
# New celery task
@celery_app.task(name="app.tasks.quality_tasks.sample_stream_quality")
async def sample_stream_quality():
    """Periodically sample stream quality (hourly)"""
    streams = await db.execute(
        select(ChannelStream).where(ChannelStream.is_active == True)
    )
    
    for stream in streams:
        analyzer = QualityAnalyzer()
        quality_metrics = await analyzer.analyze_stream(
            stream.stream_url,
            quick_mode=True  # Use cached data when possible
        )
        
        # Log quality snapshot
        quality_log = QualityLog(
            stream_id=stream.id,
            timestamp=datetime.utcnow(),
            resolution=quality_metrics.get('resolution'),
            bitrate=quality_metrics.get('bitrate'),
            quality_score=quality_metrics.get('quality_score'),
            analysis_method=quality_metrics.get('analysis_method')
        )
        await db.add(quality_log)
```

#### Gap #3: User Engagement Analytics
**Severity: MEDIUM**

**Missing Metrics:**
- Session frequency (views per user per week)
- Content discovery patterns (search → watch)
- Churn prediction (inactive users)
- Engagement score (viewing frequency + duration)
- Feature usage analytics

**Implementation:**
```python
class UserEngagementMetrics(BaseModel):
    user_id: int
    total_sessions: int
    avg_session_duration: int
    viewing_frequency: str  # "daily", "weekly", "monthly"
    last_active: datetime
    engagement_score: float  # 0-100
    content_diversity: float  # how many different channels/movies

@router.get("/admin/engagement/user/{user_id}")
async def get_user_engagement(user_id: int):
    """Get detailed engagement metrics for a user"""
```

#### Gap #4: Anomaly Detection & Alerting
**Severity: MEDIUM**

**Missing Capabilities:**
- Stream failure spike detection
- Provider health degradation alerts
- Unusual viewing pattern detection
- Quality regression warnings

**Implementation:**
```python
class AnomalyDetector:
    def detect_stream_failure_spike(self, provider_id: int):
        """Alert if failure rate exceeds threshold"""
        recent_errors = await db.scalar(
            select(func.count(HealthCheckLog.id))
            .where(HealthCheckLog.is_alive == False)
            .where(HealthCheckLog.checked_at >= datetime.now() - timedelta(hours=1))
            .where(ChannelStream.provider_id == provider_id)
        )
        
        if recent_errors > threshold:
            await send_alert(f"Provider {provider_id} failure spike: {recent_errors} failures")
```

### 4.2 Underutilized Data

**1. Logo/Image Hash Data**
- Stored in: `channels.logo_hash`
- Current Use: None visible
- **Opportunity:** Image-based duplicate detection, channel rebranding tracking

**2. Provider Metadata JSON**
- Stored in: `channel_streams.provider_metadata`
- Current Use: Metadata storage only
- **Opportunity:** Extract insights (e.g., region, source quality hints)

**3. Custom Tags**
- Stored in: `channels.tags` (JSON)
- Current Use: Storage only
- **Opportunity:** User-defined analytics grouping

**4. EPG Data**
- Stored in: `epg_programs` table
- Current Use: Program guide only
- **Opportunity:** 
  - Program popularity tracking
  - Viewing vs program correlation
  - Ad insertion metrics

### 4.3 Advanced Analytics Opportunities

#### Opportunity #1: Predictive Analytics
```python
# Predict next popular channel based on viewing patterns
@router.get("/analytics/predict/next-popular")
async def predict_next_popular_channels(
    days_ahead: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Predict which channels will trend in next N days"""
    # Use viewing pattern history to predict
```

#### Opportunity #2: Recommendation Engine
```python
# Recommend channels based on viewing similarity
@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user)
):
    """Recommend channels based on similar users' viewing patterns"""
    # Collaborative filtering based on viewing history
```

#### Opportunity #3: Cohort Analysis
```python
@router.get("/admin/analytics/cohorts")
async def get_cohort_analysis(
    cohort_by: str = "signup_date",  # signup_date, region, provider
    admin_user: User = Depends(require_admin)
):
    """Analyze user cohorts and their behaviors"""
```

#### Opportunity #4: Real-Time Dashboard
```python
# Live metrics dashboard
@router.websocket("/ws/live-analytics")
async def websocket_live_analytics(websocket: WebSocket):
    """Push real-time metrics to frontend"""
    # Currently viewing count
    # Stream health status changes
    # New popular trends
```

### 4.4 Business Intelligence Potential

**High-Value Insights to Enable:**

1. **Provider ROI Analysis**
   ```sql
   SELECT 
       p.name,
       COUNT(DISTINCT vh.user_id) as unique_users,
       COUNT(vh.id) as total_views,
       SUM(vh.duration_seconds) / 3600 as hours_watched,
       COUNT(DISTINCT cs.id) as active_streams,
       ROUND(COUNT(vh.id) / COUNT(DISTINCT cs.id), 2) as views_per_stream
   FROM providers p
   LEFT JOIN channel_streams cs ON p.id = cs.provider_id
   LEFT JOIN channels c ON cs.channel_id = c.id
   LEFT JOIN viewing_history vh ON c.id = vh.channel_id
   GROUP BY p.id
   ```

2. **User Lifecycle Value**
   ```python
   class UserLTV:
       user_id: int
       signup_date: datetime
       active_days: int
       total_hours_watched: float
       favorite_genre: str
       retention_status: str  # active, churned, at_risk
       ltv_score: float
   ```

3. **Content Performance Ranking**
   ```python
   class ContentPerformance:
       channel_id: int
       rank: int
       engagement_score: float  # weighted views + duration
       consistency: float  # daily viewership stability
       growth_trend: float  # 7-day trend
       seasonal_pattern: str
   ```

4. **Market Segmentation**
   - Segment users by viewing behavior
   - Identify heavy users vs casual browsers
   - Find niche content audiences
   - Detect regional preferences

---

## 5. DATABASE QUERIES FOR ANALYTICS

### 5.1 User-Level Queries

```sql
-- User viewing timeline
SELECT 
    vh.id,
    COALESCE(c.name, vm.title, vs.title) as content_name,
    vh.duration_seconds,
    vh.completed,
    vh.started_at,
    vh.ended_at
FROM viewing_history vh
LEFT JOIN channels c ON vh.channel_id = c.id
LEFT JOIN vod_movies vm ON vh.vod_movie_id = vm.id
LEFT JOIN vod_series vs ON vh.vod_series_id = vs.id
WHERE vh.user_id = ?
ORDER BY vh.started_at DESC
LIMIT 100;

-- User engagement score (configurable)
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT DATE(vh.started_at)) as active_days,
    COUNT(vh.id) as total_sessions,
    SUM(vh.duration_seconds) / 3600 as hours_watched,
    AVG(vh.duration_seconds) / 60 as avg_session_minutes,
    COUNT(CASE WHEN vh.completed = true THEN 1 END) / COUNT(*) as completion_rate
FROM users u
LEFT JOIN viewing_history vh ON u.id = vh.user_id
WHERE vh.started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY u.id
ORDER BY hours_watched DESC;
```

### 5.2 Content-Level Queries

```sql
-- Channel performance with quality metrics
SELECT 
    c.id,
    c.name,
    c.category,
    COUNT(DISTINCT vh.user_id) as unique_viewers,
    COUNT(vh.id) as total_views,
    SUM(vh.duration_seconds) / 3600 as total_hours,
    COUNT(CASE WHEN vh.completed THEN 1 END) * 100 / COUNT(*) as completion_rate,
    COUNT(DISTINCT cs.id) as stream_variants,
    ROUND(AVG(cs.quality_score), 0) as avg_quality_score,
    SUM(CASE WHEN cs.is_active = true THEN 1 ELSE 0 END) as active_streams
FROM channels c
LEFT JOIN viewing_history vh ON c.id = vh.channel_id
LEFT JOIN channel_streams cs ON c.id = cs.channel_id
WHERE vh.started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY c.id
ORDER BY total_views DESC;

-- Genre popularity
SELECT 
    c.category,
    COUNT(DISTINCT vh.user_id) as unique_viewers,
    COUNT(vh.id) as view_count,
    SUM(vh.duration_seconds) / 3600 as hours_watched,
    ROUND(AVG(CASE WHEN vh.completed THEN 1 ELSE 0 END) * 100, 2) as completion_rate
FROM channels c
LEFT JOIN viewing_history vh ON c.id = vh.channel_id
WHERE vh.started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY c.category
ORDER BY view_count DESC;
```

### 5.3 Provider-Level Queries

```sql
-- Provider health and performance
SELECT 
    p.id,
    p.name,
    p.total_channels,
    COUNT(DISTINCT cs.id) as indexed_streams,
    SUM(CASE WHEN cs.is_active = true THEN 1 ELSE 0 END) as active_streams,
    ROUND(SUM(CASE WHEN cs.is_active = true THEN 1 ELSE 0 END) * 100 / COUNT(DISTINCT cs.id), 2) as health_percentage,
    SUM(CASE WHEN cs.consecutive_failures > 0 THEN 1 ELSE 0 END) as failing_streams,
    ROUND(AVG(cs.response_time), 0) as avg_response_time_ms,
    MAX(cs.last_check) as last_check_time
FROM providers p
LEFT JOIN channel_streams cs ON p.id = cs.provider_id
GROUP BY p.id
ORDER BY health_percentage DESC;

-- Provider content freshness
SELECT 
    p.id,
    p.name,
    p.last_sync,
    ROUND(HOUR(TIMEDIFF(NOW(), p.last_sync)) + DAY(TIMEDIFF(NOW(), p.last_sync)) * 24, 1) as hours_since_sync,
    COUNT(DISTINCT c.id) as total_channels,
    COUNT(DISTINCT vm.id) as total_movies,
    COUNT(DISTINCT vs.id) as total_series
FROM providers p
LEFT JOIN channel_streams cs ON p.id = cs.provider_id
LEFT JOIN channels c ON cs.channel_id = c.id
LEFT JOIN vod_movies vm ON p.id = vm.provider_id
LEFT JOIN vod_series vs ON p.id = vs.provider_id
GROUP BY p.id;
```

### 5.4 Stream Quality Queries

```sql
-- Streams by quality tier
SELECT 
    cs.resolution,
    COUNT(*) as stream_count,
    ROUND(AVG(cs.bitrate), 0) as avg_bitrate_kbps,
    ROUND(AVG(cs.quality_score), 0) as avg_quality_score,
    SUM(CASE WHEN cs.is_active = true THEN 1 ELSE 0 END) as active_count,
    COUNT(DISTINCT cs.provider_id) as provider_count
FROM channel_streams cs
WHERE cs.resolution IS NOT NULL
GROUP BY cs.resolution
ORDER BY cs.quality_score DESC;

-- Streams underperforming on quality
SELECT 
    cs.id,
    c.name,
    cs.resolution,
    cs.bitrate,
    cs.quality_score,
    cs.response_time,
    cs.consecutive_failures,
    COUNT(vh.id) as views_in_30d
FROM channel_streams cs
JOIN channels c ON cs.channel_id = c.id
LEFT JOIN viewing_history vh ON c.id = vh.channel_id 
  AND vh.started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
WHERE cs.is_active = true
  AND cs.quality_score < 500  -- Low quality threshold
  AND COUNT(vh.id) > 0  -- Has viewers
GROUP BY cs.id
ORDER BY vh.view_count DESC;
```

### 5.5 Health Check Analysis

```sql
-- Stream reliability metrics
SELECT 
    cs.id,
    c.name,
    SUM(CASE WHEN cs.last_success IS NOT NULL THEN 1 ELSE 0 END) as successful_checks,
    SUM(CASE WHEN cs.last_failure IS NOT NULL THEN 1 ELSE 0 END) as failed_checks,
    ROUND(100 - (cs.consecutive_failures * 100 / (
        SELECT COUNT(*) FROM channel_streams WHERE provider_id = cs.provider_id
    )), 2) as estimated_uptime,
    cs.last_check,
    cs.failure_reason
FROM channel_streams cs
JOIN channels c ON cs.channel_id = c.id
ORDER BY cs.consecutive_failures DESC;

-- Daily health trends
SELECT 
    DATE(hc.checked_at) as check_date,
    COUNT(*) as total_checks,
    SUM(CASE WHEN hc.is_alive = true THEN 1 ELSE 0 END) as alive_count,
    ROUND(100 * SUM(CASE WHEN hc.is_alive = true THEN 1 ELSE 0 END) / COUNT(*), 2) as daily_health_percentage
FROM health_check_log hc
GROUP BY DATE(hc.checked_at)
ORDER BY check_date DESC
LIMIT 30;
```

---

## 6. API ENDPOINTS SUMMARY

### 6.1 Analytics Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/analytics/history` | GET | User viewing history | User |
| `/api/analytics/history` | POST | Create viewing session | User |
| `/api/analytics/history/{id}` | PATCH | Update viewing session | User |
| `/api/analytics/stats` | GET | User viewing statistics | User |
| `/api/analytics/popular` | GET | Popular channels | User |
| `/api/analytics/admin/stats` | GET | System-wide statistics | Admin |

### 6.2 Health Check Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/health/check` | POST | Trigger health check | None |
| `/api/health/status` | GET | Get health check status | None |

### 6.3 System Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/system/health` | GET | System health status | None |
| `/api/system/stats` | GET | System-wide statistics | None |
| `/api/system/config` | GET | System configuration | None |

---

## 7. RECOMMENDATIONS & IMPLEMENTATION ROADMAP

### Phase 1: Quick Wins (1-2 weeks)

1. **Add Export Functionality**
   - CSV/JSON export for viewing history
   - Admin analytics export
   - Effort: 2-3 hours

2. **Implement Provider Performance Logging**
   - Track sync duration and errors
   - Monitor content freshness
   - Effort: 4-6 hours

3. **Add Real-Time Health Status WebSocket**
   - Live stream health updates
   - Effort: 3-4 hours

### Phase 2: Core Analytics (2-3 weeks)

1. **Create Advanced Analytics Dashboard**
   - Time-series charts (viewing trends)
   - Cohort analysis
   - Provider performance comparison
   - Effort: 8-10 hours

2. **Implement Stream Quality History Tracking**
   - Sample quality metrics hourly
   - Track quality degradation
   - Effort: 6-8 hours

3. **Add User Engagement Scoring**
   - Calculate engagement metrics
   - Identify at-risk users
   - Effort: 4-5 hours

### Phase 3: Advanced Features (3-4 weeks)

1. **Recommendation Engine**
   - Collaborative filtering
   - Content similarity matching
   - Effort: 12-15 hours

2. **Anomaly Detection**
   - Stream failure spike detection
   - Quality regression alerts
   - Effort: 8-10 hours

3. **Business Intelligence Reports**
   - Provider ROI analysis
   - User lifetime value calculation
   - Market segmentation
   - Effort: 10-12 hours

---

## 8. VISUALIZATION RECOMMENDATIONS

### Chart Types by Metric

**Viewing Trends:**
- **Line Chart**: Views over time (daily/weekly aggregation)
- **Area Chart**: Cumulative watch time
- **Bar Chart**: Top channels comparison

**User Behavior:**
- **Heatmap**: Viewing time patterns (hour × day)
- **Funnel Chart**: Stream start → completion flow
- **Scatter Plot**: Session duration vs frequency

**Provider Health:**
- **Gauge Chart**: Provider health percentage
- **Timeline**: Stream uptime/downtime history
- **Stacked Bar**: Active vs failed streams

**Quality Metrics:**
- **Waterfall Chart**: Quality score breakdown
- **Distribution**: Resolution distribution
- **Trend Line**: Quality degradation over time

---

## Summary

The M3U-STRM-Processor has **foundational analytics capabilities** focused on viewing history and stream health, but lacks:
- Provider performance detailed tracking
- Stream quality degradation monitoring
- Advanced user engagement metrics
- Real-time analytics infrastructure
- Export and reporting features
- Anomaly detection and alerting

**Priority Improvements:**
1. Provider performance analytics (HIGH impact)
2. Stream quality history tracking (HIGH impact)
3. Real-time analytics dashboard (MEDIUM impact)
4. User engagement scoring (MEDIUM impact)
5. Anomaly detection/alerting (MEDIUM-HIGH impact)

