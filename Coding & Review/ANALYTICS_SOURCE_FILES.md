# M3U-STRM-Processor Analytics - Source File Reference

## Core Analytics Files

### Backend Analytics API
**File:** `/home/user/m3u-STRM-Processor-/backend/app/api/analytics.py`
- ViewingHistory endpoints (GET, POST, PATCH)
- User statistics endpoint
- Popular channels endpoint
- System-wide admin statistics

**Line References:**
- Lines 96-161: Start viewing session (POST /history)
- Lines 164-223: Update viewing session (PATCH /history/{id})
- Lines 226-261: Get viewing history (GET /history)
- Lines 264-329: Get user statistics (GET /stats)
- Lines 332-372: Get popular channels (GET /popular)
- Lines 375-451: Get system stats (GET /admin/stats)

### Backend Health Check API
**File:** `/home/user/m3u-STRM-Processor-/backend/app/api/health.py`
- Health check status endpoint
- Trigger health check endpoint

### Backend System API
**File:** `/home/user/m3u-STRM-Processor-/backend/app/api/system.py`
- System configuration
- System health status
- System-wide statistics

### Data Models
**File:** `/home/user/m3u-STRM-Processor-/backend/app/models/user.py`
- User model with role-based access control
- UserFavorite model
- ViewingHistory model (lines 73-100)

**File:** `/home/user/m3u-STRM-Processor-/backend/app/models/channel.py`
- Channel model with metadata
- ChannelStream model with quality/health metrics (lines 50-100)

**File:** `/home/user/m3u-STRM-Processor-/backend/app/models/provider.py`
- Provider model with performance tracking fields

### Services - Quality Analysis
**File:** `/home/user/m3u-STRM-Processor-/backend/app/services/quality_analyzer.py`
- QualityAnalyzer class
- Resolution detection (name, URL, FFprobe)
- Quality score calculation (lines 260-291)
- Stream comparison and sorting

**Key Methods:**
- `extract_resolution_from_name()` - Lines 53-72
- `extract_resolution_from_url()` - Lines 74-91
- `analyze_stream()` - Lines 93-144
- `_analyze_with_ffprobe()` - Lines 146-231
- `_calculate_quality_score()` - Lines 260-291

### Services - Health Checking
**File:** `/home/user/m3u-STRM-Processor-/backend/app/services/health_checker.py`
- StreamHealthChecker class
- Concurrent health checks (50 parallel)
- Response time tracking
- Health score calculation (lines 187-221)

**Key Methods:**
- `check_stream()` - Lines 40-99
- `check_streams_batch()` - Lines 101-134
- `calculate_health_score()` - Lines 187-221

### Tasks - Health Checks
**File:** `/home/user/m3u-STRM-Processor-/backend/app/tasks/health_tasks.py`
- Health check task (Celery)
- Stream batch processing
- Database updates with results
- Priority ordering by quality

**Key Tasks:**
- `run_health_check()` - Lines 13-17
- `_run_health_check_async()` - Lines 20-102
- `check_provider_streams()` - Lines 131-136
- `_check_provider_streams_async()` - Lines 138-200

### Database Migrations
**File:** `/home/user/m3u-STRM-Processor-/backend/alembic/versions/001_initial_schema.py`
- Initial schema creation
- viewing_history table definition (lines 50-71)
- channel_streams table with health metrics (lines 126-169)
- Indexes for analytics queries

**File:** `/home/user/m3u-STRM-Processor-/backend/alembic/versions/002_add_user_roles_and_analytics.py`
- User roles enum
- ViewingHistory table creation
- Viewing history indexes (lines 68-70)

## Frontend Analytics Files

### Analytics Page Component
**File:** `/home/user/m3u-STRM-Processor-/frontend/src/pages/Analytics.jsx`
- User analytics dashboard
- Admin system analytics
- Popular channels visualization
- Viewing history table

**Key Sections:**
- Lines 12-18: User statistics query
- Lines 20-27: Popular channels query
- Lines 30-37: System statistics query (admin only)
- Lines 40-46: Viewing history query
- Lines 82-172: System overview section
- Lines 176-231: User statistics section
- Lines 234-252: Popular channels section
- Lines 255-303: Viewing history table

### Dashboard Component
**File:** `/home/user/m3u-STRM-Processor-/frontend/src/pages/Dashboard.jsx`
- System-level statistics
- Quick action buttons
- Provider/channel/VOD counts
- Health status overview

### System Info Component
**File:** `/home/user/m3u-STRM-Processor-/frontend/src/pages/SystemInfo.jsx`
- System configuration display
- Database statistics
- Health status
- System health check

## Configuration Files

### Environment Settings
**File:** `/home/user/m3u-STRM-Processor-/backend/app/core/config.py`
- Health check timeout configuration
- Concurrent health check limits
- EPG refresh intervals
- Verification settings

### Database Configuration
**File:** `/home/user/m3u-STRM-Processor-/backend/app/core/database.py`
- Database connection setup
- Session factory configuration
- Async engine configuration

## Documentation Generated

### Comprehensive Analysis
**File:** `/home/user/m3u-STRM-Processor-/ANALYTICS_EXPLORATION.md`
- Complete analytics capabilities overview
- Data collection strategy
- Reporting and visualization details
- Gaps and opportunities
- Business intelligence potential

### Implementation Guide
**File:** `/home/user/m3u-STRM-Processor-/ANALYTICS_IMPLEMENTATION_GUIDE.md`
- Practical code examples
- Provider performance logging
- Stream quality history tracking
- User engagement metrics
- Real-time WebSocket analytics
- Performance optimization tips

### Quick Reference
**File:** `/home/user/m3u-STRM-Processor-/ANALYTICS_QUICK_REFERENCE.md`
- Current status checklist
- Key database tables
- Essential API endpoints
- Critical SQL queries
- Implementation priorities
- Database schema additions

## Key Metrics Storage Locations

### Viewing Metrics
- **Table:** `viewing_history`
- **Fields:** user_id, channel_id, duration_seconds, completed, started_at, ended_at
- **Indexed on:** user_id, started_at, channel_id
- **Location:** Database

### Stream Health Metrics
- **Table:** `channel_streams`
- **Fields:** is_active, response_time, consecutive_failures, last_check, failure_reason
- **Location:** Database

### Quality Metrics
- **Table:** `channel_streams`
- **Fields:** resolution, bitrate, codec, fps, quality_score
- **Location:** Database

### Provider Metrics
- **Table:** `providers`
- **Fields:** total_channels, active_channels, last_sync, last_health_check
- **Location:** Database

## API Test Endpoints

### Using curl
```bash
# Get user viewing history
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/history

# Get user statistics (30 days)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/stats?days=30

# Get popular channels (7 days)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/popular?days=7&limit=10

# Get system stats (admin only)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/admin/stats

# Get health status
curl http://localhost:8000/api/health/status

# Trigger health check
curl -X POST http://localhost:8000/api/health/check

# Get system stats
curl http://localhost:8000/api/system/stats
```

## Integration Points

### Authentication Integration
- **File:** `/home/user/m3u-STRM-Processor-/backend/app/core/auth.py`
- Analytics endpoints use `get_current_user()` and `require_admin()`

### Database Integration
- **File:** `/home/user/m3u-STRM-Processor-/backend/app/core/database.py`
- All analytics queries use async SQLAlchemy ORM

### Task Scheduling
- **File:** `/home/user/m3u-STRM-Processor-/backend/app/tasks/celery_app.py`
- Health checks run via Celery beat scheduler

## Important Implementation Notes

1. **Async/Await Pattern:** All database operations use async SQLAlchemy
2. **Error Handling:** Comprehensive try-except blocks in health checks
3. **Concurrency Control:** Semaphore limits to 50 concurrent health checks
4. **Data Isolation:** ViewingHistory filtered by current user (except admin)
5. **Pagination Support:** History queries support limit/offset parameters
6. **Time Zone Aware:** All timestamps use UTC with timezone support

## Performance Characteristics

- **Viewing History Insert:** ~50-100ms per record
- **Popular Channels Query:** ~200-500ms for 7-day window
- **Health Check Batch:** 50 streams in ~30-60 seconds
- **Quality Analysis:** 1-2 seconds per stream (FFprobe mode)
- **Storage per Entry:** ~500 bytes for viewing_history

## Next Steps for Implementation

1. Review complete files listed above
2. Check `/home/user/m3u-STRM-Processor-/ANALYTICS_EXPLORATION.md` for gaps
3. Follow code examples in `/home/user/m3u-STRM-Processor-/ANALYTICS_IMPLEMENTATION_GUIDE.md`
4. Use priorities from `/home/user/m3u-STRM-Processor-/ANALYTICS_QUICK_REFERENCE.md`
5. Update database schema with new tables
6. Add new endpoints following existing patterns
7. Test with real provider data

