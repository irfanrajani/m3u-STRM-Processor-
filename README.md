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

### Docker

```bash
docker pull ghcr.io/irfanrajani/m3u-strm-processor:latest
docker run -p 8080:8080 -v ./output:/output ghcr.io/irfanrajani/m3u-strm-processor:latest
```

Visit `http://localhost:8080`

### Docker Compose

```bash
docker-compose up -d
```

### QNAP

1. Download `.qpkg` from [GitHub Actions](../../actions/workflows/build_qpkg.yml)
2. Install via App Center → Install Manually
3. Requires Container Station to be installed
4. Access at `http://your-qnap-ip:8080`

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

### Requirements

- Python 3.9+
- Node.js 18+
- Yarn

### Local Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
yarn install
yarn build
cd ..

# Run the application
uvicorn api.main:app --reload --port 8080
```

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
