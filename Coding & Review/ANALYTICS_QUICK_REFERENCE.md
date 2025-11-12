# M3U-STRM-Processor Analytics - Quick Reference

## Current Status
- **Viewing History:** ✅ Fully implemented
- **Channel Popularity:** ✅ Implemented (7/30/90 day views)
- **Health Metrics:** ✅ Stream health, response time, failures tracked
- **Quality Metrics:** ✅ Basic quality scoring available
- **User Engagement:** ❌ Missing detailed metrics
- **Provider Performance:** ❌ Limited to basic stats
- **Real-Time Analytics:** ❌ Not available
- **Export Capabilities:** ❌ Not available

## Key Database Tables

| Table | Purpose | Key Metrics |
|-------|---------|-------------|
| `viewing_history` | User viewing sessions | user_id, channel_id, duration, completed |
| `channel_streams` | Individual streams | is_active, quality_score, response_time, consecutive_failures |
| `channels` | Merged channel info | stream_count, category, epg_id |
| `providers` | IPTV providers | total_channels, active_channels, last_sync |
| `users` | User accounts | id, username, role, last_login |

## Essential API Endpoints

```
User Analytics:
  GET  /api/analytics/history                    - Get viewing history
  POST /api/analytics/history                    - Start viewing session
  PATCH /api/analytics/history/{id}              - Update session (mark complete)
  GET  /api/analytics/stats?days=30              - Get user statistics
  GET  /api/analytics/popular?days=7&limit=10    - Get popular channels

Admin Analytics:
  GET  /api/analytics/admin/stats                - System-wide stats

Health Checks:
  GET  /api/health/status                        - Get health status
  POST /api/health/check                         - Trigger health check

System:
  GET  /api/system/stats                         - Provider/channel/VOD counts
  GET  /api/system/health                        - System health status
```

## Critical SQL Queries

### User's Top Channels
```sql
SELECT c.id, c.name, COUNT(*) as views, SUM(vh.duration_seconds)/3600 as hours
FROM viewing_history vh
JOIN channels c ON vh.channel_id = c.id
WHERE vh.user_id = ? AND vh.started_at >= NOW() - INTERVAL 30 DAY
GROUP BY c.id
ORDER BY views DESC LIMIT 10;
```

### System Health Score
```sql
SELECT 
  COUNT(*) as total_streams,
  SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_streams,
  ROUND(100.0 * SUM(CASE WHEN is_active THEN 1 ELSE 0 END) / COUNT(*), 2) as health_pct
FROM channel_streams;
```

### Provider Performance
```sql
SELECT 
  p.name, 
  COUNT(DISTINCT cs.id) as streams,
  SUM(CASE WHEN cs.is_active THEN 1 ELSE 0 END) as active,
  ROUND(AVG(cs.response_time), 0) as avg_response_ms
FROM providers p
LEFT JOIN channel_streams cs ON p.id = cs.provider_id
GROUP BY p.id;
```

## Implementation Priorities

### High Priority (Significant Impact)
1. **Provider Performance Logging**
   - Track sync duration, errors, content changes
   - Estimate: 4-6 hours

2. **Stream Quality History**
   - Sample quality metrics hourly
   - Track quality degradation
   - Estimate: 6-8 hours

3. **User Engagement Scoring**
   - Calculate engagement metrics
   - Identify at-risk users
   - Estimate: 4-5 hours

### Medium Priority
4. **Real-Time Analytics Dashboard**
   - WebSocket for live metrics
   - Estimate: 6-8 hours

5. **Export Capabilities**
   - CSV/JSON/Excel export
   - Estimate: 3-4 hours

6. **Anomaly Detection**
   - Alert on failures/quality issues
   - Estimate: 8-10 hours

## Database Schema Additions

### Provider Performance Logs
```sql
CREATE TABLE provider_performance_logs (
  id INT PRIMARY KEY,
  provider_id INT,
  sync_duration_seconds FLOAT,
  channels_added INT,
  channels_removed INT,
  errors_count INT,
  error_details JSON,
  data_freshness_hours FLOAT,
  created_at TIMESTAMP
);
```

### Quality Logs
```sql
CREATE TABLE quality_logs (
  id INT PRIMARY KEY,
  stream_id INT,
  resolution VARCHAR(20),
  bitrate INT,
  quality_score INT,
  codec VARCHAR(50),
  fps FLOAT,
  analysis_method VARCHAR(50),
  sampled_at TIMESTAMP,
  created_at TIMESTAMP
);
```

## Performance Optimization Checklist

- [ ] Add indexes on viewing_history(user_id, started_at)
- [ ] Add indexes on channel_streams(is_active, quality_score)
- [ ] Implement query result caching (5-min TTL)
- [ ] Add connection pooling limits
- [ ] Archive viewing_history > 2 years
- [ ] Partition tables by month (if > 10M rows)
- [ ] Add query timeouts (30 sec default)

## Privacy & Compliance

**Current Gaps:**
- Stream URLs stored in history (not masked)
- No audit logging for data access
- No GDPR "right to be forgotten"
- No data retention policies
- No compliance export endpoints

**Recommendations:**
- Hash stream URLs after 1 day
- Implement audit logging
- Add GDPR export/delete endpoints
- Set retention policy: 2 years for viewing history
- Mask sensitive URLs in logs

## Testing Queries

```python
# Python test - get user's top channels
import requests
response = requests.get(
    'http://localhost:8000/api/analytics/popular?days=30&limit=5',
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())

# Get system stats (admin)
response = requests.get(
    'http://localhost:8000/api/analytics/admin/stats',
    headers={'Authorization': f'Bearer {admin_token}'}
)
print(response.json())
```

## Common Issues & Solutions

**Issue: Viewing history not recorded**
- Check: Client sending POST to `/api/analytics/history`
- Check: User authentication working
- Check: Database connection

**Issue: Health checks failing**
- Check: Provider streams have valid URLs
- Check: Network connectivity to streams
- Check: Health check timeout not too short

**Issue: Slow analytics queries**
- Solution: Add indexes on user_id, started_at
- Solution: Implement query result caching
- Solution: Archive old viewing_history data

## Files to Review

1. `/backend/app/api/analytics.py` - Main analytics endpoints
2. `/backend/app/services/health_checker.py` - Stream health checks
3. `/backend/app/services/quality_analyzer.py` - Quality analysis
4. `/backend/app/models/user.py` - ViewingHistory model
5. `/frontend/src/pages/Analytics.jsx` - Frontend dashboard

## Next Steps

1. Review `ANALYTICS_EXPLORATION.md` for complete analysis
2. Review `ANALYTICS_IMPLEMENTATION_GUIDE.md` for code examples
3. Prioritize implementations based on business needs
4. Start with Quick Wins (Phase 1) for immediate impact
5. Plan for Medium/Long-term analytics features
