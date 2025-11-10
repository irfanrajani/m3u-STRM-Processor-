# IPTV Stream Manager

A comprehensive IPTV stream management application for Emby, featuring intelligent channel merging, quality-based stream prioritization, automatic health checking, and VOD management.

## ⚡ Quick Start

**Prerequisites:** Docker & Docker Compose

```bash
# 1. Clone the repository
git clone <repository-url>
cd m3u-STRM-Processor-

# 2. Start everything with one command
./start.sh
```

That's it! Open http://localhost:8080 in your browser.

**First Time Setup:**
1. Add your IPTV providers (see TESTING.md for your exact configs)
2. Click "Sync" for each provider
3. Watch as channels merge automatically!

## 🎯 Features

### Core Functionality
- ✅ **Multi-Provider Support**: Xstream API and M3U/M3U8 playlists
- ✅ **Intelligent Channel Merging**: Automatically merges duplicate channels across providers
- ✅ **Region/Variant Detection**: Keeps "Sportsnet West" and "Sportsnet East" separate
- ✅ **Quality-Based Prioritization**: 4K > 1080p > 720p > 480p with automatic failover
- ✅ **Dead Stream Detection**: Automatic health checks remove non-functional streams
- ✅ **Multi-Quality Failover**: If primary stream fails, automatically use next best quality

### VOD Management
- ✅ **Xstream VOD Support**: Fetch movies and series from Xstream providers
- ✅ **Auto .strm Generation**: Creates Emby-compatible .strm files
- ✅ **Genre Organization**: Movies and series organized by genre
- ✅ **Season/Episode Structure**: Proper TV show organization

### Automation
- ✅ **Scheduled Syncing**: Hourly provider sync (configurable)
- ✅ **Health Checks**: Daily stream testing (configurable)
- ✅ **EPG Refresh**: Daily guide updates (configurable)
- ✅ **Background Processing**: All heavy tasks run asynchronously

### Output
- ✅ **Merged Playlists**: Single M3U with best quality streams
- ✅ **Multi-Quality Playlists**: All qualities available for manual selection
- ✅ **Category Playlists**: Separate playlists per category
- ✅ **Emby Integration**: Direct .strm file support

## 📚 Documentation

- **[TESTING.md](TESTING.md)** - Test with your providers (5-minute guide)
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation instructions
- **[USAGE.md](USAGE.md)** - Complete usage guide
- **[API Documentation](http://localhost:8080/docs)** - Interactive API docs (after starting)

## 🏗️ Architecture

**Backend:**
- FastAPI (Python 3.11+) - High-performance async web framework
- PostgreSQL - Reliable data storage
- Celery + Redis - Distributed task queue
- FFprobe - Stream quality analysis

**Frontend:**
- React 18 - Modern UI framework
- Vite - Lightning-fast build tool
- TailwindCSS - Utility-first styling
- React Query - Server state management

**Deployment:**
- Docker Compose - Multi-container orchestration
- Nginx - Reverse proxy & static file serving

## 🔧 Configuration

### Default Settings (Ready to Use)
- Health checks: Daily at 3 AM
- Provider sync: Every hour
- EPG refresh: Daily at 2 AM
- Fuzzy matching: 85% threshold
- Quality analysis: Enabled

### Customize Settings
All settings configurable via web GUI:
1. Navigate to **Settings**
2. Adjust thresholds, schedules, timeouts
3. Save changes - takes effect immediately

## 📊 How It Works

### Channel Merging Example

**Your Providers:**
- TorrentDay: "CNN", "ESPN HD", "Sportsnet West"
- Strong8K: "CNN 1080p", "ESPN", "Sportsnet West 4K"
- TrexTV: "CNN HD", "ESPN 720p", "Sportsnet East"

**After Merging:**
- **CNN** (3 streams: 1080p, HD, SD) - Defaults to 1080p
- **ESPN** (3 streams: HD, 720p, SD) - Defaults to HD
- **Sportsnet West** (2 streams: 4K, SD) - Separate channel
- **Sportsnet East** (1 stream) - Separate channel

### Quality Prioritization

Each channel's streams are sorted by:
1. **Resolution**: 4K > 1440p > 1080p > 720p > 480p
2. **Bitrate**: Higher is better (within same resolution)
3. **Provider Priority**: Configurable per provider
4. **Response Time**: Faster streams preferred

### Automatic Failover

When watching a channel:
1. Player uses highest quality stream (Stream #1)
2. If Stream #1 buffers/fails → Auto-switch to Stream #2
3. If Stream #2 fails → Auto-switch to Stream #3
4. Health check runs daily to remove dead streams

## 🚀 Performance

**Tested with:**
- 3 providers (TorrentDay, Strong8K, TrexTV)
- 90,000+ total streams
- 30,000+ channels per provider

**Results:**
- Merges down to ~25-35k unique channels
- Sync time: 15-30 min per provider
- Health check: 30-60 min for all streams
- Memory usage: 2-4 GB
- Playlist generation: <1 minute

## 🔍 Troubleshooting

**Services won't start:**
```bash
docker-compose down && docker-compose up -d
```

**No channels appearing:**
```bash
docker-compose logs -f celery_worker
# Check for sync errors
```

**Channels merging incorrectly:**
1. Go to Settings
2. Increase fuzzy threshold to 90 (less merging)
3. Or decrease to 75 (more aggressive)
4. Re-sync providers

**Streams not playing:**
```bash
# Run health check
curl -X POST http://localhost:8080/api/health/check
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Credits

Inspired by: Threadfin, Dispatcharr, xTeVe, StreamMaster

Built for the IPTV community 🎬📺
