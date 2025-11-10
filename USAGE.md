# Usage Guide

## Getting Started

### Adding IPTV Providers

The app supports two types of IPTV providers:

#### 1. Xstream Codes API

Used by most modern IPTV providers. Example setup:

```
Name: Strong8K
Type: Xstream
Host: http://hybrid25589.cdn-akm.me
Username: 41bc4e70a3
Password: 3d72b61321
Backup Hosts (optional):
  - http://ksa.protection-cdn.vip
  - http://cf.business-cdn.me
EPG URL: https://epg.iptv.cat/epg.xml
```

#### 2. M3U Playlist

Used by simpler providers. Example setup:

```
Name: TorrentDay
Type: M3U
M3U URL: https://torrentday.com/iptv/711931/xaDkWrkgDP/Default
Backup URLs (optional):
  - https://backup-url-here.com/playlist.m3u
EPG URL: https://epg.iptv.cat/epg.xml
```

### Channel Management

#### Understanding Channel Merging

The app automatically merges duplicate channels across providers:

**Example:**
- Provider 1: "CNN HD"
- Provider 2: "CNN"
- Provider 3: "CNN 1080p"

These are merged into one channel "CNN" with 3 streams, prioritized by quality.

#### Regional Channels

The app recognizes regional variations:

- "Sportsnet West" and "Sportsnet East" remain separate
- "TSN Ontario" and "TSN Atlantic" remain separate
- Regional keywords: West, East, North, South, Ontario, Quebec, etc.

#### Channel Variants

The app recognizes channel variants:

- "ESPN" and "ESPN+" remain separate
- "HBO" and "HBO 2" remain separate
- Variant keywords: +, Plus, HD, 4K, 1, 2, 3, News, Sports, Movies

#### Filtering Channels

Use the web interface to filter:
1. **By Category**: Sports, News, Movies, etc.
2. **By Search**: Type channel name
3. **By Region**: Select specific region
4. **By Quality**: Filter 4K, HD, SD channels

### Stream Quality & Failover

#### Quality Priority

Streams are prioritized automatically:
1. **4K/2160p** (highest)
2. **1440p/QHD**
3. **1080p/FHD**
4. **720p/HD**
5. **480p/SD**
6. **Lower resolutions**

Within each quality level, streams are prioritized by:
- Bitrate (higher is better)
- Provider priority
- Response time (faster is better)

#### Automatic Failover

When a stream fails:
1. App marks stream as unhealthy
2. Next best stream becomes primary
3. Failed stream is rechecked during next health check
4. After 3 consecutive failures, stream is marked inactive

### VOD Management

#### Syncing VOD Content

VOD is only supported for **Xstream providers**:

1. Add Xstream provider
2. Enable provider
3. Click **Sync**
4. Navigate to **VOD** tab
5. View synced movies and series

#### Generating .strm Files

.strm files allow Emby to play IPTV content:

1. Sync VOD content first
2. Click **Generate STRM Files** in VOD tab
3. Files are created in `output/strm_files/`
4. Add this folder to Emby as a media library

**Emby Setup:**
1. Open Emby
2. Go to **Library** > **Add Media Library**
3. For Movies:
   - Content Type: Movies
   - Folder: `<path-to-output>/strm_files/Movies`
4. For TV Shows:
   - Content Type: TV Shows
   - Folder: `<path-to-output>/strm_files/TV Shows`

### Playlist Generation

The app generates merged M3U playlists:

#### Merged Playlist (Best Quality)

Contains one stream per channel (highest quality):
- Location: `output/playlists/merged_playlist_all.m3u`
- Use this for: Most IPTV players

#### Multi-Quality Playlist

Contains all stream qualities for each channel:
- Location: `output/playlists/multi_quality_all.m3u`
- Use this for: Players with manual quality selection

#### Category Playlists

Separate playlists per category:
- `merged_playlist_Sports.m3u`
- `merged_playlist_News.m3u`
- `merged_playlist_Movies.m3u`

#### Using Playlists in Emby

1. Open Emby
2. Go to **Live TV** > **Tuner Devices**
3. Select **M3U Tuner**
4. Enter playlist URL: `http://<server-ip>:8080/output/playlists/merged_playlist_all.m3u`
5. Save

### EPG (Electronic Program Guide)

#### Adding EPG Data

1. Navigate to **Settings**
2. Add EPG URL for each provider
3. Common EPG sources:
   - https://epg.iptv.cat/epg.xml
   - https://iptv-org.github.io/epg/guides/
4. EPG refreshes daily at 2 AM (configurable)

#### Manual EPG Refresh

Use the API:
```bash
curl -X POST http://localhost:8080/api/epg/refresh \
  -H "Content-Type: application/json" \
  -d '{"epg_url": "https://epg.iptv.cat/epg.xml"}'
```

### Health Checks

#### Automatic Health Checks

Default schedule: Daily at 3 AM

The health check:
1. Tests each stream URL
2. Measures response time
3. Marks dead streams as inactive
4. Re-prioritizes active streams

#### Manual Health Check

Via web interface:
1. Navigate to **Dashboard**
2. Click **Run Health Check**

Via API:
```bash
curl -X POST http://localhost:8080/api/health/check
```

#### Understanding Health Status

- **Green (Active)**: Stream is working
- **Yellow (Slow)**: Stream works but slow response
- **Red (Inactive)**: Stream failed 3+ times

### Settings Configuration

#### Channel Matching

**Fuzzy Match Threshold (85)**
- Lower = More aggressive merging
- Higher = More conservative merging
- Recommended: 80-90

**Enable Logo Matching**
- Uses image comparison for better matching
- Slightly slower but more accurate

#### Health Check Settings

**Schedule (0 3 * * *)**
- Cron format
- Default: Daily at 3 AM
- Change for your preference

**Timeout (10 seconds)**
- Time to wait for stream response
- Lower = Faster checks, more false negatives
- Higher = Slower checks, fewer false negatives

**Max Concurrent Checks (50)**
- Number of streams checked simultaneously
- Lower = Slower but less resource intensive
- Higher = Faster but more CPU/network usage

#### Quality Analysis

**Enable Bitrate Analysis**
- Uses FFprobe to analyze streams
- More accurate quality detection
- Slower sync process
- Disable for faster syncing

### Advanced Usage

#### API Access

The app provides a REST API:

**Base URL:** `http://localhost:8080/api`

**Common Endpoints:**
- `GET /providers/` - List providers
- `POST /providers/{id}/sync` - Sync provider
- `GET /channels/` - List channels
- `GET /vod/movies` - List movies
- `POST /health/check` - Run health check

**API Documentation:**
Visit `http://localhost:8080/docs` for interactive API docs.

#### Scheduled Tasks

The app runs these automated tasks:

1. **Provider Sync** - Hourly
2. **Health Check** - Daily at 3 AM
3. **EPG Refresh** - Daily at 2 AM

Modify schedules in `backend/app/tasks/celery_app.py`.

#### Database Access

Access PostgreSQL directly:

```bash
docker exec -it iptv_db psql -U iptv iptv_manager

# Example queries
SELECT name, total_channels, active_channels FROM providers;
SELECT name, stream_count FROM channels WHERE enabled = true;
SELECT COUNT(*) FROM channel_streams WHERE is_active = true;
```

## Tips & Best Practices

### Performance Optimization

1. **Disable bitrate analysis** for faster syncing (Settings)
2. **Limit concurrent health checks** on slower systems
3. **Schedule health checks** during off-peak hours
4. **Use category playlists** for faster loading in players

### Quality Management

1. **Test providers** before full sync
2. **Review merged channels** for accuracy
3. **Adjust fuzzy threshold** if too many/few merges
4. **Monitor health checks** regularly

### Troubleshooting

1. **No channels appearing**: Check provider sync logs
2. **Wrong channel merging**: Increase fuzzy threshold
3. **Streams not playing**: Run health check
4. **Slow performance**: Disable bitrate analysis

### Regular Maintenance

Weekly:
- Review inactive streams
- Check provider health
- Monitor disk space

Monthly:
- Backup database
- Review and adjust settings
- Update to latest version
