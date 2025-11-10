# Installation Guide

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- 10GB+ disk space

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd m3u-STRM-Processor-
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your preferred settings
nano .env
```

**Important Environment Variables:**
```env
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql+asyncpg://iptv:iptv_password@db:5432/iptv_manager
```

### Step 3: Start Services
```bash
docker-compose up -d
```

### Step 4: Access Web Interface
Open your browser and navigate to:
```
http://localhost:8080
```

### Step 5: Add Your First Provider

1. Navigate to **Providers** in the web interface
2. Click **Add Provider**
3. Fill in your IPTV provider details:
   - **Name**: TorrentDay (or your provider name)
   - **Type**: M3U or Xstream
   - For M3U:
     - **M3U URL**: Your provider's M3U playlist URL
   - For Xstream:
     - **Host**: Provider server URL
     - **Username**: Your username
     - **Password**: Your password
4. Click **Test Connection** to verify
5. Click **Save**

### Step 6: Initial Sync

After adding providers:
1. Click **Sync** on each provider to fetch channels
2. Wait for synchronization to complete (check logs)
3. Navigate to **Channels** to see merged channels

## QNAP Installation

### Using Container Station

1. Open Container Station
2. Click **Create Container**
3. Select **Create Container via Docker Compose**
4. Copy the contents of `docker-compose.yml`
5. Modify volume paths for QNAP:
   ```yaml
   volumes:
     - /share/Container/iptv/output:/app/output
     - /share/Container/iptv/logs:/app/logs
   ```
6. Click **Create**

### Using SSH

```bash
ssh admin@your-qnap-ip
cd /share/Container
git clone <repository-url>
cd m3u-STRM-Processor-
docker-compose up -d
```

## Manual Installation (Advanced)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+
- FFmpeg

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create database
createdb iptv_manager

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run build

# For development
npm run dev
```

### Celery Workers

```bash
# Terminal 1 - Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 2 - Beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

## Configuration

### Channel Matching Settings

Adjust fuzzy matching threshold (0-100):
- **85+**: Strict matching (fewer false positives)
- **70-84**: Moderate matching (recommended)
- **<70**: Loose matching (may merge incorrect channels)

### Health Check Schedule

Default: Daily at 3 AM (`0 3 * * *`)

Common schedules:
- Every 6 hours: `0 */6 * * *`
- Twice daily: `0 3,15 * * *`
- Weekly: `0 3 * * 0`

### VOD Organization

The app organizes VOD content as:
```
output/
├── strm_files/
│   ├── Movies/
│   │   ├── Action/
│   │   │   └── Movie Title (2023)/
│   │   │       └── Movie Title (2023).strm
│   │   └── Comedy/
│   └── TV Shows/
│       └── Series Title (2020)/
│           ├── Season 01/
│           │   ├── Series - S01E01 - Episode Title.strm
│           │   └── Series - S01E02 - Episode Title.strm
│           └── Season 02/
└── playlists/
    ├── merged_playlist_all.m3u
    └── merged_playlist_Sports.m3u
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View database logs
docker logs iptv_db
```

### No Channels After Sync

1. Check provider status in web interface
2. View backend logs: `docker logs iptv_backend`
3. Manually trigger sync: Click **Sync** button
4. Verify provider credentials

### Health Check Not Running

```bash
# Check Celery beat status
docker logs iptv_celery_beat

# Manually trigger health check via API
curl -X POST http://localhost:8080/api/health/check
```

### FFprobe Errors

FFprobe is used for quality analysis. If disabled:
1. Go to **Settings**
2. Uncheck "Enable bitrate analysis"
3. Save settings

## Updating

### Docker Installation

```bash
cd m3u-STRM-Processor-
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Manual Installation

```bash
git pull
cd backend
pip install -r requirements.txt
alembic upgrade head
cd ../frontend
npm install
npm run build
```

## Backup & Restore

### Backup Database

```bash
docker exec iptv_db pg_dump -U iptv iptv_manager > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i iptv_db psql -U iptv iptv_manager
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation
- Open an issue on GitHub
