# M3U to STRM Processor

A powerful web application that converts M3U playlist files into individual STRM files for use with media servers like Plex, Jellyfin, or Emby. Features intelligent duplicate detection, quality-based merging, and automatic organization.

## ✨ Features

### Core Functionality
- 🎯 **Web-based interface** for easy M3U processing
- 📁 **Converts M3U playlists** to individual STRM files
- 🔄 **Smart duplicate detection** - removes exact URL duplicates
- 🎬 **Quality-based merging** - combines "ESPN", "ESPN HD", "ESPN 4K" intelligently
- 🏆 **Configurable quality preference** - choose best, 4K, HD, SD, or keep all
- 📂 **Category organization** - auto-organize by Sports, News, Movies, etc.
- 🔍 **Fuzzy name matching** - detects similar channels even with different naming
- 🔒 **Security hardened** - path sanitization prevents directory traversal

### Deployment Options
- 🐳 **Docker support** for easy deployment anywhere
- 📦 **QNAP package** (.qpkg) for native QNAP NAS integration
- 🚀 **GitHub Actions CI/CD** - automated builds and releases

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/irfanrajani/m3u-STRM-Processor-.git
cd m3u-STRM-Processor-

# Start everything (auto-configures on first run!)
docker-compose up -d

# That's it! Everything is auto-configured with secure defaults.
```

**First run will:**
- ✅ Auto-generate secure SECRET_KEY
- ✅ Auto-configure database connection
- ✅ Auto-configure Redis connection
- ✅ Create default admin user (admin/admin123)

**Access the application (Docker Compose):**
- Web UI + API (served by backend): http://localhost:8000
- API docs (OpenAPI): http://localhost:8000/docs
- Settings page: http://localhost:8000/settings

**⚠️ Change default password immediately at http://localhost:3000/settings**

### Option 2: Pull from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/irfanrajani/m3u-strm-processor:latest

# Run with docker-compose
docker-compose up -d
```

## 📖 Usage Guide

### Basic Workflow

1. **Enter M3U URL** - Your IPTV provider's playlist URL
2. **Set output path** - Where to save STRM files (relative to `/output`)
3. **Configure options:**
   - ✅ Merge duplicates (recommended)
   - 🎯 Quality preference (best/4K/HD/SD/all)
   - 📂 Organize by category
   - 🔍 Fuzzy match threshold
4. **Click "Create STRM Files"**
5. **Point your media server** at the output folder

### Example

**Input M3U with duplicates:**
```
#EXTINF:-1,ESPN
http://stream.com/espn-sd
#EXTINF:-1,ESPN HD
http://stream.com/espn-hd
#EXTINF:-1,ESPN 4K
http://stream.com/espn-4k
#EXTINF:-1,CNN
http://stream.com/cnn
#EXTINF:-1,CNN HD
http://stream.com/cnn-hd
```

**Output (with merge enabled, prefer "best"):**
```
output/
  ├── ESPN.strm          → http://stream.com/espn-4k (kept 4K)
  └── CNN.strm           → http://stream.com/cnn-hd (kept HD)
```

**Output (with category organization):**
```
output/
  ├── Sports/
  │   └── ESPN.strm
  └── News/
      └── CNN.strm
```

## Current Architecture
- Single container: FastAPI backend + static compiled frontend served on port 8000.
- API base path: http://localhost:8000/api
- Docs: http://localhost:8000/docs
- STRM output directory inside container: /app/output (config OUTPUT_DIR).

## New Endpoint
POST /api/process-m3u/
Request body:
```json
{
  "m3u_url": "https://example.com/playlist.m3u",
  "output_path": "channels",
  "merge_duplicates": true,
  "prefer_quality": "best",
  "organize_by_category": false,
  "fuzzy_match_threshold": 0.85,
  "clean_output_first": false
}
```
Response:
```json
{
  "message": "Successfully created N STRM files (merged from M original entries)",
  "channels_created": N,
  "duplicates_removed": D,
  "categories_used": C,
  "output_dir": "/app/output/channels"
}
```

## ⚙️ Configuration Options

### Merge Duplicates
When enabled, channels with similar names are merged into a single STRM file.

- `ESPN`, `ESPN HD`, `ESPN 4K` → becomes **one file**
- Fuzzy matching detects variants like `HBO` vs `HBO-HD` vs `H B O`

### Quality Preference

- **Best Available**: Automatically selects highest quality (4K > FHD > HD > SD)
- **4K Only**: Keep only 4K streams, skip others
- **HD Only**: Keep only HD streams
- **SD Only**: Keep only SD streams
- **Keep All Variants**: Don't merge, create separate files for each quality

### Fuzzy Match Threshold

Controls how similar channel names must be to merge (0.0 - 1.0):

- **0.95** - Very strict (only exact matches with minor differences)
- **0.85** - Recommended (catches most variants)
- **0.75** - Moderate (may merge some unrelated channels)
- **0.50** - Aggressive (not recommended)

### Organize by Category

When enabled, channels are grouped into subfolders based on their `group-title` attribute in the M3U file:

```
output/
  ├── Sports/
  ├── News/
  ├── Movies/
  └── Entertainment/
```

## 🛠️ Development

### Local Development (hot reload)

Use the Vite dev server for the frontend (port 3000) and run the backend separately (port 8000):

Requirements:
- Python 3.11+
- Node.js 18+

Backend (FastAPI):
```bash
# From project root
docker-compose up -d  # starts db, redis, backend on :8000
# Or run locally if you prefer: uvicorn app.main:app --reload --port 8000
```

Frontend (Vite):
```bash
cd frontend
npm install
npm run dev  # serves http://localhost:3000 and proxies /api to http://localhost:8000
```

Access during development:
- Frontend (hot reload): http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Running Tests

```bash
# Backend linting
flake8 api

# Frontend build test
cd frontend && yarn build
```

## 📁 Project Structure

```
.
├── api/
│   └── main.py              # FastAPI backend with smart merging logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React UI with all controls
│   │   ├── App.css          # Styling
│   │   └── main.jsx
│   └── package.json
├── qnap/
│   ├── qpkg.cfg             # QNAP package config
│   ├── shared/
│   │   └── m3u-STRM-Processor.sh
│   └── docker-compose.yml   # QNAP deployment
├── .github/workflows/        # CI/CD pipelines
├── Dockerfile               # Multi-stage build
├── docker-compose.yml
└── requirements.txt
```

## 🔧 API Endpoint

### POST /process-m3u/

**Request Body:**
```json
{
  "m3u_url": "https://example.com/playlist.m3u",
  "output_path": "channels",
  "merge_duplicates": true,
  "prefer_quality": "best",
  "organize_by_category": false,
  "fuzzy_match_threshold": 0.85
}
```

**Response:**
```json
{
  "message": "Successfully created 150 STRM files (merged from 320 original entries)",
  "channels_created": 150,
  "duplicates_removed": 170
}
```

## 🐛 Troubleshooting

### No files created
- Check output volume is properly mounted
- Verify M3U URL is accessible
- Check application logs for errors

### Too many duplicates kept
- Lower fuzzy match threshold (try 0.75)
- Ensure channel names in M3U have quality indicators

### Channels merged incorrectly
- Raise fuzzy match threshold (try 0.95)
- Disable merging and organize manually

### QNAP package won't start
- Ensure Container Station is installed
- Check logs: `cat /share/CACHEDEV1_DATA/.qpkg/m3u-STRM-Processor/qpkg.log`
- Verify Docker image pulled: `docker images | grep m3u-strm-processor`

## 📜 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 👤 Author

Irfan Rajani

---

**Note:** This tool creates STRM files that reference streams. It does not provide, host, or stream any content. You must have legal access to the streams referenced in your M3U playlists.
