# M3U-STRM-Processor Analytics - Practical Implementation Guide

## Quick Implementation Examples

### Example 1: Provider Performance Logging

**New Model (add to `backend/app/models/analytics.py`):**

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class ProviderPerformanceLog(Base):
    """Track provider sync performance and metrics."""
    
    __tablename__ = "provider_performance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    
    # Sync metrics
    sync_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sync_duration_seconds = Column(Float, nullable=True)
    
    # Content changes
    channels_added = Column(Integer, default=0)
    channels_removed = Column(Integer, default=0)
    channels_updated = Column(Integer, default=0)
    
    # Error tracking
    errors_count = Column(Integer, default=0)
    error_details = Column(JSON, nullable=True)
    
    # Data freshness
    data_freshness_hours = Column(Float, nullable=True)
    
    # Relationships
    provider = relationship("Provider")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Sync Task Enhancement (update `backend/app/tasks/sync_tasks.py`):**

```python
import time
from app.models.analytics import ProviderPerformanceLog

@celery_app.task(name="app.tasks.sync_tasks.sync_provider")
async def sync_provider(provider_id: int):
    """Sync provider and log performance metrics."""
    sync_start = time.time()
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as db:
            # Get provider
            provider = await db.execute(
                select(Provider).where(Provider.id == provider_id)
            )
            provider = provider.scalar_one()
            
            # Track before sync
            channels_before = await db.scalar(
                select(func.count(Channel.id))
                .where(Channel.provider_id == provider_id)
            )
            
            # Perform sync
            errors = []
            try:
                if provider.provider_type == "m3u":
                    await sync_m3u_provider(db, provider)
                else:
                    await sync_xstream_provider(db, provider)
            except Exception as e:
                errors.append(str(e))
                logger.error(f"Sync error for provider {provider_id}: {e}")
            
            # Track after sync
            channels_after = await db.scalar(
                select(func.count(Channel.id))
                .where(Channel.provider_id == provider_id)
            )
            
            # Calculate freshness
            freshness_hours = 0
            if provider.last_sync:
                freshness_hours = (datetime.utcnow() - provider.last_sync).total_seconds() / 3600
            
            # Log performance
            perf_log = ProviderPerformanceLog(
                provider_id=provider_id,
                sync_timestamp=datetime.utcnow(),
                sync_duration_seconds=time.time() - sync_start,
                channels_added=max(0, channels_after - channels_before),
                channels_removed=max(0, channels_before - channels_after),
                channels_updated=0,  # Track separately if needed
                errors_count=len(errors),
                error_details=errors if errors else None,
                data_freshness_hours=freshness_hours
            )
            
            db.add(perf_log)
            await db.commit()
            
            logger.info(f"Sync completed for provider {provider_id} in {time.time() - sync_start:.2f}s")
            
    except Exception as e:
        logger.error(f"Provider sync failed: {e}")
        await db.rollback()
```

**API Endpoint:**

```python
# Add to backend/app/api/analytics.py

@router.get("/admin/providers/performance")
async def get_provider_performance(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get provider performance metrics."""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            ProviderPerformanceLog.provider_id,
            Provider.name,
            func.avg(ProviderPerformanceLog.sync_duration_seconds).label('avg_sync_duration'),
            func.count(ProviderPerformanceLog.id).label('sync_count'),
            func.sum(ProviderPerformanceLog.errors_count).label('total_errors'),
            func.avg(ProviderPerformanceLog.data_freshness_hours).label('avg_freshness')
        )
        .join(Provider, ProviderPerformanceLog.provider_id == Provider.id)
        .where(ProviderPerformanceLog.created_at >= since_date)
        .group_by(ProviderPerformanceLog.provider_id, Provider.name)
    )
    
    return [
        {
            "provider_id": row.provider_id,
            "provider_name": row.name,
            "avg_sync_duration": round(row.avg_sync_duration or 0, 2),
            "sync_count": row.sync_count,
            "total_errors": row.total_errors or 0,
            "avg_freshness_hours": round(row.avg_freshness or 0, 2)
        }
        for row in result.all()
    ]
```

---

### Example 2: Stream Quality History Tracking

**New Model:**

```python
class QualityLog(Base):
    """Historical quality metrics per stream."""
    
    __tablename__ = "quality_logs"
    
    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("channel_streams.id"), nullable=False)
    
    # Quality snapshot
    resolution = Column(String(20), nullable=True)
    bitrate = Column(Integer, nullable=True)
    quality_score = Column(Integer, default=0)
    codec = Column(String(50), nullable=True)
    fps = Column(Float, nullable=True)
    
    # Metadata
    analysis_method = Column(String(50))  # 'name', 'url', 'ffprobe'
    
    # Timestamps
    sampled_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stream = relationship("ChannelStream")
```

**Quality Sampling Task:**

```python
# backend/app/tasks/quality_tasks.py

import asyncio
from app.tasks.celery_app import celery_app
from app.models.analytics import QualityLog

@celery_app.task(name="app.tasks.quality_tasks.sample_stream_quality")
def sample_stream_quality():
    """Sample quality for all active streams (hourly)."""
    asyncio.run(_sample_stream_quality_async())


async def _sample_stream_quality_async():
    """Async implementation."""
    session_factory = get_session_factory()
    analyzer = QualityAnalyzer(enable_bitrate_analysis=False)  # Use quick mode
    
    async with session_factory() as db:
        try:
            # Get active streams
            result = await db.execute(
                select(ChannelStream).where(ChannelStream.is_active == True)
            )
            streams = result.scalars().all()
            
            logger.info(f"Sampling quality for {len(streams)} streams")
            
            for stream in streams[:100]:  # Sample 100 per batch
                try:
                    metrics = await analyzer.analyze_stream(
                        stream.stream_url,
                        stream_name=stream.channel.name if stream.channel else None,
                        quick_mode=True
                    )
                    
                    # Log quality snapshot
                    quality_log = QualityLog(
                        stream_id=stream.id,
                        resolution=metrics.get('resolution'),
                        bitrate=metrics.get('bitrate'),
                        quality_score=metrics.get('quality_score'),
                        codec=metrics.get('codec'),
                        fps=metrics.get('fps'),
                        analysis_method=metrics.get('analysis_method'),
                        sampled_at=datetime.utcnow()
                    )
                    
                    db.add(quality_log)
                    
                except Exception as e:
                    logger.debug(f"Quality sampling failed for stream {stream.id}: {e}")
            
            await db.commit()
            logger.info("Quality sampling completed")
            
        except Exception as e:
            logger.error(f"Quality sampling failed: {e}")
            await db.rollback()
```

**Quality Analysis Endpoint:**

```python
@router.get("/admin/streams/quality-history/{stream_id}")
async def get_stream_quality_history(
    stream_id: int,
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get quality history for a specific stream."""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(QualityLog)
        .where(
            QualityLog.stream_id == stream_id,
            QualityLog.created_at >= since_date
        )
        .order_by(QualityLog.sampled_at.desc())
    )
    
    logs = result.scalars().all()
    
    return [
        {
            "timestamp": log.sampled_at.isoformat(),
            "resolution": log.resolution,
            "bitrate": log.bitrate,
            "quality_score": log.quality_score,
            "codec": log.codec,
            "fps": log.fps
        }
        for log in logs
    ]
```

---

### Example 3: User Engagement Metrics

**Engagement Model and Calculation:**

```python
class UserEngagement(BaseModel):
    user_id: int
    username: str
    total_sessions: int
    total_hours_watched: float
    avg_session_minutes: float
    active_days: int
    last_active: Optional[datetime]
    engagement_score: float  # 0-100
    content_diversity: float  # 0-1 (how many different channels)
    completion_rate: float  # 0-100


@router.get("/admin/users/engagement")
async def get_user_engagement_metrics(
    days: int = Query(30, ge=1, le=365),
    min_engagement: float = Query(0, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Get engagement metrics for all users."""
    since_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            User.id,
            User.username,
            func.count(ViewingHistory.id).label('total_sessions'),
            func.sum(ViewingHistory.duration_seconds).label('total_seconds'),
            func.avg(ViewingHistory.duration_seconds).label('avg_session_seconds'),
            func.count(func.distinct(func.date(ViewingHistory.started_at))).label('active_days'),
            func.max(ViewingHistory.started_at).label('last_active'),
            func.count(func.distinct(ViewingHistory.channel_id)).label('unique_channels'),
            func.count(CASE WHEN ViewingHistory.completed == True THEN 1).label('completed_sessions')
        )
        .join(ViewingHistory, User.id == ViewingHistory.user_id, isouter=True)
        .where(ViewingHistory.started_at >= since_date)
        .group_by(User.id)
    )
    
    engagements = []
    for row in result.all():
        total_sessions = row.total_sessions or 0
        total_hours = (row.total_seconds or 0) / 3600
        active_days = row.active_days or 0
        
        # Calculate engagement score
        # Weight: sessions (40%), hours (40%), active days (20%)
        max_sessions = 100
        max_hours = 100
        max_days = 30
        
        session_score = min(100, (total_sessions / max_sessions) * 100)
        hour_score = min(100, (total_hours / max_hours) * 100)
        day_score = min(100, (active_days / max_days) * 100)
        
        engagement_score = (
            session_score * 0.4 +
            hour_score * 0.4 +
            day_score * 0.2
        )
        
        # Content diversity (0-1)
        unique_channels = row.unique_channels or 0
        diversity = min(1.0, unique_channels / 50)  # Normalize to 50 channels
        
        # Completion rate
        completion_rate = 0
        if total_sessions > 0:
            completion_rate = ((row.completed_sessions or 0) / total_sessions) * 100
        
        if engagement_score >= min_engagement:
            engagements.append(UserEngagement(
                user_id=row.id,
                username=row.username,
                total_sessions=total_sessions,
                total_hours_watched=round(total_hours, 2),
                avg_session_minutes=round((row.avg_session_seconds or 0) / 60, 2),
                active_days=active_days,
                last_active=row.last_active,
                engagement_score=round(engagement_score, 2),
                content_diversity=round(diversity, 2),
                completion_rate=round(completion_rate, 2)
            ))
    
    return sorted(engagements, key=lambda x: x.engagement_score, reverse=True)
```

---

### Example 4: Real-Time Analytics WebSocket

**Frontend Component:**

```jsx
// frontend/src/pages/LiveAnalytics.jsx

import { useEffect, useState } from 'react'
import { Activity, TrendingUp, Zap } from 'lucide-react'

export default function LiveAnalytics() {
  const [metrics, setMetrics] = useState({
    active_viewers: 0,
    most_watched: [],
    stream_health: { alive: 0, dead: 0 },
    timestamp: null
  })
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.host}/ws/analytics/live`)
    
    ws.onopen = () => {
      console.log('Connected to live analytics')
      setConnected(true)
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMetrics(data)
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnected(false)
    }
    
    return () => ws.close()
  }, [])

  return (
    <div className="px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Live Analytics</h1>
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${
          connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <div className={`w-2 h-2 rounded-full animate-pulse ${
            connected ? 'bg-green-600' : 'bg-red-600'
          }`}></div>
          <span className="text-sm font-medium">
            {connected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* Active Viewers */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-blue-600 mr-4" />
            <div>
              <p className="text-gray-500 text-sm">Active Viewers</p>
              <p className="text-3xl font-bold text-gray-900">
                {metrics.active_viewers}
              </p>
            </div>
          </div>
        </div>

        {/* Stream Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Zap className="h-8 w-8 text-green-600 mr-4" />
            <div>
              <p className="text-gray-500 text-sm">Healthy Streams</p>
              <p className="text-3xl font-bold text-gray-900">
                {metrics.stream_health.alive}
              </p>
              <p className="text-xs text-red-600">
                {metrics.stream_health.dead} down
              </p>
            </div>
          </div>
        </div>

        {/* Timestamp */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-purple-600 mr-4" />
            <div>
              <p className="text-gray-500 text-sm">Last Update</p>
              <p className="text-sm font-mono text-gray-900">
                {metrics.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : '-'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Most Watched Now */}
      {metrics.most_watched.length > 0 && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Trending Now</h2>
          <div className="space-y-2">
            {metrics.most_watched.map((channel, i) => (
              <div key={channel.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="font-bold text-gray-400 mr-3">#{i+1}</span>
                <span className="font-medium text-gray-900 flex-1">{channel.name}</span>
                <span className="text-sm text-gray-500">{channel.viewers} watching</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

**Backend WebSocket Handler:**

```python
# backend/app/api/analytics.py

from fastapi import WebSocket

@app.websocket("/ws/analytics/live")
async def websocket_live_analytics(websocket: WebSocket):
    """Live analytics WebSocket endpoint."""
    await websocket.accept()
    
    try:
        while True:
            # Get current metrics
            db = get_session_factory()
            async with db() as session:
                # Active viewers (currently viewing streams)
                active = await session.scalar(
                    select(func.count(ViewingHistory.id))
                    .where(
                        ViewingHistory.started_at <= datetime.utcnow(),
                        (ViewingHistory.ended_at > datetime.utcnow()) |
                        (ViewingHistory.ended_at.is_(None))
                    )
                )
                
                # Most watched now
                most_watched = await session.execute(
                    select(Channel.id, Channel.name, 
                           func.count(ViewingHistory.id).label('viewers'))
                    .join(ViewingHistory)
                    .where(ViewingHistory.started_at <= datetime.utcnow())
                    .where((ViewingHistory.ended_at > datetime.utcnow()) |
                           (ViewingHistory.ended_at.is_(None)))
                    .group_by(Channel.id)
                    .order_by(desc('viewers'))
                    .limit(5)
                )
                
                # Stream health
                alive = await session.scalar(
                    select(func.count(ChannelStream.id))
                    .where(ChannelStream.is_active == True)
                )
                dead = await session.scalar(
                    select(func.count(ChannelStream.id))
                    .where(ChannelStream.is_active == False)
                )
            
            metrics = {
                "active_viewers": active or 0,
                "most_watched": [
                    {"id": row[0], "name": row[1], "viewers": row[2]}
                    for row in most_watched.all()
                ],
                "stream_health": {
                    "alive": alive or 0,
                    "dead": dead or 0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_json(metrics)
            await asyncio.sleep(30)  # Update every 30 seconds
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from live analytics")
```

---

## Performance Optimization Tips

### 1. Query Optimization

```python
# ❌ Bad: N+1 query problem
for user in users:
    history = db.query(ViewingHistory).filter_by(user_id=user.id).all()

# ✅ Good: Eager loading
users = db.query(User).options(
    selectinload(User.viewing_history)
).all()

# ✅ Better: Single aggregation query
results = db.execute(
    select(User.id, func.count(ViewingHistory.id))
    .join(ViewingHistory)
    .group_by(User.id)
)
```

### 2. Database Indexing

```sql
-- Add these indexes to improve analytics query performance
CREATE INDEX idx_viewing_history_user_date ON viewing_history(user_id, started_at DESC);
CREATE INDEX idx_viewing_history_channel_date ON viewing_history(channel_id, started_at DESC);
CREATE INDEX idx_channel_streams_active ON channel_streams(is_active, quality_score DESC);
CREATE INDEX idx_quality_logs_stream_date ON quality_logs(stream_id, sampled_at DESC);
CREATE INDEX idx_provider_perf_provider_date ON provider_performance_logs(provider_id, created_at DESC);
```

### 3. Caching Strategies

```python
from functools import lru_cache
from datetime import timedelta

# Cache popular channels for 5 minutes
cached_popular = {}
cached_popular_time = None

async def get_popular_channels_cached(days: int = 7):
    global cached_popular, cached_popular_time
    
    now = datetime.utcnow()
    
    # Return cache if fresh
    if cached_popular_time and (now - cached_popular_time) < timedelta(minutes=5):
        return cached_popular
    
    # Fetch fresh data
    result = await db.execute(...)
    cached_popular = result.all()
    cached_popular_time = now
    
    return cached_popular
```

---

## Deployment Checklist

- [ ] Add new database migrations for analytics tables
- [ ] Create required indexes for query performance
- [ ] Configure Celery beat for scheduled tasks
- [ ] Update requirements.txt with new dependencies
- [ ] Test analytics endpoints with sample data
- [ ] Implement proper error handling and logging
- [ ] Add monitoring/alerting for analytics jobs
- [ ] Document new API endpoints
- [ ] Update frontend with new visualizations
- [ ] Performance test with production-like data volume

