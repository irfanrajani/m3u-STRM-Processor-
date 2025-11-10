# Testing Guide

## Quick Test (5 Minutes)

This guide will help you test the app with your actual IPTV providers.

### Step 1: Start the Application

```bash
# Clone and start
git clone <repository-url>
cd m3u-STRM-Processor-
docker-compose up -d
```

Wait about 30 seconds for all services to start, then verify:

```bash
docker-compose ps
```

You should see all services as "Up" (healthy).

### Step 2: Access Web Interface

Open your browser:
```
http://localhost:8080
```

You should see the IPTV Stream Manager dashboard.

### Step 3: Add Your First Provider

Based on your providers, here are the exact configurations:

#### TorrentDay (M3U)

1. Click **Providers** in the top menu
2. Click **Add Provider**
3. Fill in:
   - **Name**: TorrentDay
   - **Type**: m3u
   - **M3U URL**: `https://torrentday.com/iptv/711931/xaDkWrkgDP/Default`
   - **EPG URL**: `https://epg.iptv.cat/epg.xml`
   - **Enabled**: ✓ (checked)
   - **Priority**: 1
4. Click **Test Connection** (should show "success")
5. Click **Save**

#### Strong8K (Xstream)

1. Click **Add Provider**
2. Fill in:
   - **Name**: Strong8K
   - **Type**: xstream
   - **Host**: `http://hybrid25589.cdn-akm.me`
   - **Username**: `41bc4e70a3`
   - **Password**: `3d72b61321`
   - **Backup Hosts** (click Add for each):
     - `http://ksa.protection-cdn.vip`
     - `http://cf.business-cdn.me`
   - **EPG URL**: `https://epg.iptv.cat/epg.xml`
   - **Enabled**: ✓
   - **Priority**: 2
3. Click **Test Connection**
4. Click **Save**

#### TrexTV (Xstream)

1. Click **Add Provider**
2. Fill in:
   - **Name**: TrexTV
   - **Type**: xstream
   - **Host**: `http://56702-phrase.ott-tx.com`
   - **Username**: `5fd6df874a`
   - **Password**: `74c7acf67d`
   - **Backup Hosts**:
     - `http://line.trx-ott.com`
     - `http://es3.premium-tx.com`
   - **EPG URL**: `https://epg.iptv.cat/epg.xml`
   - **Enabled**: ✓
   - **Priority**: 3
3. Click **Test Connection**
4. Click **Save**

### Step 4: Trigger Initial Sync

For each provider you added:

1. Click the **Sync** button (circular arrows icon)
2. Watch the terminal logs to see progress:
   ```bash
   docker-compose logs -f backend
   ```

**Expected output:**
```
INFO - Starting sync for provider: TorrentDay
INFO - Fetched 30000+ channels from TorrentDay
INFO - Synced 15000 channels and 15000 new streams
```

This will take **5-15 minutes** depending on the number of channels.

### Step 5: Verify Channels

1. Navigate to **Channels** in the menu
2. You should see merged channels from all providers
3. Click on any channel to see its streams
4. Verify that:
   - Channels from multiple providers are merged
   - Streams are sorted by quality
   - Regional channels (e.g., "Sportsnet West") are separate

### Step 6: Test VOD (Optional)

1. Navigate to **VOD** tab
2. Click **Generate STRM Files**
3. Wait for completion
4. Check output folder:
   ```bash
   ls -la output/strm_files/Movies/
   ls -la output/strm_files/TV\ Shows/
   ```

### Step 7: Test Playlists

1. Check generated playlists:
   ```bash
   ls -la output/playlists/
   ```

2. Test playlist in VLC or IPTV player:
   ```
   http://localhost:8080/output/playlists/merged_playlist_all.m3u
   ```

3. Verify:
   - Channels load
   - Streams play
   - Highest quality stream is used by default

### Step 8: Test Health Check

1. Go back to **Dashboard**
2. Click **Run Health Check**
3. Monitor logs:
   ```bash
   docker-compose logs -f celery_worker
   ```

**Expected:**
```
INFO - Starting health check for all streams
INFO - Checking 90000 active streams
INFO - Batch completed. Alive: 500, Dead: 0
```

This will take **15-30 minutes** for 90k+ streams.

## Troubleshooting

### Issue: Services won't start

**Check logs:**
```bash
docker-compose logs db
docker-compose logs redis
docker-compose logs backend
```

**Common fix:**
```bash
docker-compose down
docker-compose up -d
```

### Issue: Provider sync fails

**Check provider credentials:**
- Verify username/password are correct
- Test provider URL in browser
- Check if provider requires VPN

**View detailed logs:**
```bash
docker-compose logs -f celery_worker
```

### Issue: No channels appearing

**Verify sync completed:**
```bash
docker exec -it iptv_db psql -U iptv iptv_manager -c "SELECT COUNT(*) FROM channels;"
```

**If count is 0, re-sync:**
1. Go to Providers
2. Click Sync for each provider
3. Wait for completion

### Issue: Channels not merging correctly

**Adjust fuzzy matching:**
1. Go to **Settings**
2. Change **Fuzzy Match Threshold**:
   - Too many merges? Increase to 90
   - Too few merges? Decrease to 75
3. Save settings
4. Re-sync providers

### Issue: Streams not playing

**Run health check:**
```bash
curl -X POST http://localhost:8080/api/health/check
```

**Check stream status:**
1. Go to **Channels**
2. Click on a channel
3. View stream status (green = active, red = inactive)

## Performance Testing

### Test Load with All Providers

With 3 providers and 30k+ channels each:

**Expected totals:**
- Total streams: ~90,000
- Merged channels: ~25,000-35,000 (many duplicates)
- Sync time: 15-30 minutes per provider
- Health check time: 30-60 minutes
- Memory usage: ~2-4 GB
- CPU usage: Moderate during sync/health check

### Monitor Resources

```bash
# Watch resource usage
docker stats

# Check disk usage
du -sh output/
```

## Advanced Testing

### API Testing

Test the REST API directly:

```bash
# List providers
curl http://localhost:8080/api/providers/

# Get channels
curl http://localhost:8080/api/channels/

# Get VOD stats
curl http://localhost:8080/api/vod/stats

# Trigger sync
curl -X POST http://localhost:8080/api/providers/1/sync
```

### Database Testing

```bash
# Connect to database
docker exec -it iptv_db psql -U iptv iptv_manager

# Check statistics
SELECT
  p.name,
  p.total_channels,
  COUNT(cs.id) as total_streams
FROM providers p
LEFT JOIN channel_streams cs ON cs.provider_id = p.id
GROUP BY p.id, p.name;

# Check active streams
SELECT COUNT(*) FROM channel_streams WHERE is_active = true;

# Check merged channels
SELECT
  c.name,
  c.stream_count,
  string_agg(DISTINCT p.name, ', ') as providers
FROM channels c
JOIN channel_streams cs ON cs.channel_id = c.id
JOIN providers p ON p.id = cs.provider_id
WHERE c.enabled = true
GROUP BY c.id, c.name, c.stream_count
HAVING COUNT(DISTINCT cs.provider_id) > 1
ORDER BY c.stream_count DESC
LIMIT 20;
```

### Logs Testing

```bash
# Watch all logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat

# Check for errors
docker-compose logs | grep ERROR
docker-compose logs | grep WARNING
```

## Success Criteria

Your installation is working correctly if:

- ✅ All Docker containers are running
- ✅ Web interface loads at http://localhost:8080
- ✅ Providers can be added and tested
- ✅ Sync completes without errors
- ✅ Channels appear in the Channels tab
- ✅ Duplicate channels are merged correctly
- ✅ Regional variants remain separate
- ✅ Streams are prioritized by quality
- ✅ Health checks complete successfully
- ✅ Playlists are generated
- ✅ VOD .strm files are created
- ✅ Streams play in IPTV players

## Next Steps

Once testing is complete:

1. **Configure Emby** (see USAGE.md)
2. **Adjust Settings** based on your preferences
3. **Set up automated backups**
4. **Monitor health checks** regularly
5. **Fine-tune channel matching** if needed

## Getting Help

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Review INSTALLATION.md
3. Review USAGE.md
4. Open an issue on GitHub with:
   - Error messages
   - Docker logs
   - Steps to reproduce
