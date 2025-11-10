# IPTV Stream Manager - Deployment Guide

## 🚀 Quick Start (QNAP Deployment)

### Step 1: Pull Latest Code on QNAP

SSH into your QNAP and navigate to your project directory:

```bash
cd /share/CACHEDEV1_DATA/your-project-directory
git pull origin claude/iptv-stream-manager-app-011CUy48Kq3XqiW9T6GuBArx
```

### Step 2: Stop Existing Containers (if running)

```bash
docker compose -f docker-compose.deploy.yml down
```

### Step 3: Build Fresh Images

**Option A: Build on QNAP directly (recommended)**

```bash
# Build backend
docker build --no-cache --platform linux/amd64 -f docker/Dockerfile.backend -t iptv-backend:local .

# Build frontend
docker build --no-cache --platform linux/amd64 -f docker/Dockerfile.frontend -t iptv-frontend:local .
```

**Option B: Build on Mac and transfer**

```bash
# On your Mac
cd ~/path/to/project
git pull

# Build for AMD64
docker build --no-cache --platform linux/amd64 -f docker/Dockerfile.backend -t iptv-backend:local .
docker build --no-cache --platform linux/amd64 -f docker/Dockerfile.frontend -t iptv-frontend:local .

# Save images
docker save iptv-backend:local | gzip > iptv-backend-latest.tar.gz
docker save iptv-frontend:local | gzip > iptv-frontend-latest.tar.gz

# Transfer to QNAP (manually via File Station or scp)
# Then on QNAP:
docker load < iptv-backend-latest.tar.gz
docker load < iptv-frontend-latest.tar.gz
```

### Step 4: Create Required Directories

```bash
mkdir -p output/playlists output/strm_files output/epg logs
chmod -R 777 output logs
```

### Step 5: Start Services

```bash
docker compose -f docker-compose.deploy.yml up -d
```

### Step 6: Check Logs

```bash
# Watch all logs
docker compose -f docker-compose.deploy.yml logs -f

# Watch just backend
docker compose -f docker-compose.deploy.yml logs -f backend

# Check if services are running
docker compose -f docker-compose.deploy.yml ps
```

### Step 7: Run Database Migrations

```bash
docker compose -f docker-compose.deploy.yml exec backend alembic upgrade head
```

---

## 📋 First-Time Setup

### 1. Access the Web UI

Open your browser and go to:
```
http://YOUR_QNAP_IP:3000
```

(Replace `YOUR_QNAP_IP` with your actual QNAP IP address, e.g., `192.168.1.100`)

### 2. Create Admin Account

On first visit, you'll see the login page. Click "Create Account" and register your admin user.

### 3. Add a Provider

1. Navigate to **Providers** page
2. Click **"Add Provider"**
3. Choose provider type:

**For Xstream API:**
- Name: `My IPTV Provider`
- Type: `Xstream`
- Host: `http://provider.com:8080`
- Username: `your_username`
- Password: `your_password`

**For M3U Playlist:**
- Name: `My M3U Provider`
- Type: `M3U`
- M3U URL: `http://provider.com/playlist.m3u`
- EPG URL (optional): `http://provider.com/epg.xml`

4. Click **"Add Provider"**

### 4. Sync Provider

After adding a provider:
1. Click the **refresh icon** next to the provider
2. Wait for sync to complete (check logs if needed)
3. Navigate to **Channels** to see imported channels

---

## 🎬 Configure Emby for Live TV (HDHomeRun Mode)

This is the **recommended** method for Emby Live TV - no transcoding, smooth playback!

### Step 1: Get Your HDHomeRun URL

1. In the web UI, go to **System Info** page
2. Find the **HDHomeRun URL** section
3. Copy the URL (should look like: `http://192.168.1.100:8201`)

### Step 2: Add Tuner in Emby

1. Open Emby Server Dashboard
2. Go to **Live TV** → **Tuner Devices**
3. Click **Add**
4. Select **HDHomeRun**
5. Paste your URL from Step 1
6. Click **Save**

Emby will automatically discover your "HD Home Run" device!

### Step 3: Map Channels

1. In Emby, go to **Live TV** → **Channel Mappings**
2. Emby will show all channels from your lineup
3. Map channels to EPG data (if you have EPG configured)
4. Save

### Step 4: Test

1. Go to Emby → **Live TV** → **Guide**
2. Click on a channel to start playback
3. Check playback info - it should say **"Direct Play"** (not transcoding!)

---

##  📺 Alternative: Use M3U Playlist (VLC, Kodi, etc.)

If you prefer using the M3U playlist directly:

### Get Playlist URL

From **System Info** page, copy the **M3U Playlist** URL:
```
http://192.168.1.100:8080/playlists/merged_playlist_all.m3u
```

### Use in VLC

1. Open VLC
2. Media → Open Network Stream
3. Paste the M3U URL
4. Play!

### Use in Kodi

1. Add-ons → PVR Clients → **PVR IPTV Simple Client**
2. Configure → **General** → M3U Play List URL
3. Paste your M3U URL
4. Save and restart

---

## 🎥 Configure Emby for VOD (Movies/TV Shows)

### Step 1: Generate STRM Files

1. Make sure you've synced a provider with VOD content
2. Go to **Dashboard**
3. Click **"Generate STRM Files"**
4. Wait for generation to complete

STRM files will be created in `/output/strm_files/`:
```
/output/strm_files/Movies/Genre/Movie Title (Year)/Movie Title (Year).strm
/output/strm_files/TV Shows/Genre/Series (Year)/Season 01/Series - S01E01 - Title.strm
```

### Step 2: Add Libraries in Emby

1. Open Emby Server Dashboard
2. Go to **Library** → **Add Library**

**For Movies:**
- Content type: **Movies**
- Folder: `/path/to/output/strm_files/Movies`
- (On QNAP, use the actual path where you mounted the volume)

**For TV Shows:**
- Content type: **TV Shows**
- Folder: `/path/to/output/strm_files/TV Shows`

3. Scan library
4. Emby will detect all .strm files as media!

---

## ⚙️ Configuration

All configuration is auto-detected! No manual .env editing needed.

### Optional Settings (via .env if needed)

If you want to customize:

```bash
# On QNAP, edit .env file
nano .env
```

Available settings:
```bash
# HDHomeRun Emulation
HDHR_PROXY_MODE=direct          # or 'proxy' to stream through server
HDHR_DEVICE_ID=IPTV-MGR         # Device ID shown in Emby
HDHR_TUNER_COUNT=4              # Number of concurrent streams

# If auto-detection doesn't work, set manually:
# EXTERNAL_URL=http://192.168.1.100:8201

# Channel Matching
DEFAULT_FUZZY_MATCH_THRESHOLD=85  # 70-100, higher = stricter

# Quality Analysis
ENABLE_BITRATE_ANALYSIS=true    # Analyze stream quality (slower)
FFPROBE_TIMEOUT=15              # Seconds to wait for analysis
```

After changing .env:
```bash
docker compose -f docker-compose.deploy.yml restart backend
```

---

## 🔍 Troubleshooting

### Backend won't start

**Check logs:**
```bash
docker compose -f docker-compose.deploy.yml logs backend
```

**Common issues:**
- Database not ready: Wait 30 seconds and try again
- Port conflict: Change port in docker-compose.deploy.yml

### Emby can't find HDHomeRun device

1. Check System Info page - make sure URL is correct
2. Try accessing the discovery URL directly in browser:
   ```
   http://YOUR_IP:8201/discover.json
   ```
   Should return JSON with device info

3. Make sure Emby server can reach your QNAP IP

### Channels not showing after sync

1. Check provider sync completed:
   ```bash
   docker compose -f docker-compose.deploy.yml logs celery_worker
   ```

2. Check database:
   ```bash
   docker compose -f docker-compose.deploy.yml exec backend python -c "from app.core.database import AsyncSessionLocal; from app.models.channel import Channel; from sqlalchemy import select; import asyncio; async def count(): async with AsyncSessionLocal() as db: result = await db.execute(select(Channel)); print(len(result.scalars().all())); asyncio.run(count())"
   ```

### STRM files not playing in Emby

1. Check STRM file content:
   ```bash
   cat output/strm_files/Movies/Action/Movie\ Title\ \(2023\)/Movie\ Title\ \(2023\).strm
   ```
   Should contain a stream URL

2. Test URL directly in VLC

3. Check Emby logs for playback errors

---

## 📊 Monitoring

### View Active Celery Tasks

```bash
docker compose -f docker-compose.deploy.yml exec celery_worker celery -A app.tasks.celery_app inspect active
```

### View Health Status

```bash
curl http://localhost:8201/api/health/status
```

### View System Info

```bash
curl http://localhost:8201/api/system/info
```

---

## 🔄 Updating

To update to latest version:

```bash
# Pull latest code
git pull

# Rebuild images
docker compose -f docker-compose.deploy.yml build --no-cache

# Restart services
docker compose -f docker-compose.deploy.yml up -d

# Run any new migrations
docker compose -f docker-compose.deploy.yml exec backend alembic upgrade head
```

---

## 📦 Ports

Make sure these ports are available on your QNAP:

- **3000**: Frontend (Web UI)
- **8201**: Backend API + HDHomeRun emulation
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)
- **8080**: Nginx (serves M3U playlists and static files)

---

## 🎯 Next Steps

Once everything is running:

1. **Add your IPTV providers** (Xstream or M3U)
2. **Sync providers** to import channels
3. **Configure Emby** using HDHomeRun URL
4. **Generate STRM files** for VOD content
5. **Customize settings** in Settings page
6. **Set up automatic syncing** (enabled by default)

Enjoy your IPTV Stream Manager! 🎉
