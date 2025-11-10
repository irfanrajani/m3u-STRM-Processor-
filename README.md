# M3U to STRM Processor

A web application that converts M3U playlist files into individual STRM files for use with media servers like Plex, Jellyfin, or Emby.

## Features

- 🎯 Web-based interface for easy M3U processing
- 📁 Converts M3U playlists to individual STRM files
- 🐳 Docker support for easy deployment
- 📦 QNAP package (.qpkg) for native QNAP NAS integration
- 🔒 Path sanitization to prevent directory traversal attacks

## Quick Start

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

## Usage

1. Enter M3U playlist URL
2. Specify output path (relative to `/output` volume)
3. Click "Create STRM Files"
4. Files will be created in the specified directory

## Development

### Requirements

- Python 3.9+
- Node.js 18+
- Yarn

### Setup

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

## Project Structure

```
.
├── api/                    # FastAPI backend
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   └── package.json
├── qnap/                   # QNAP package files
│   ├── qpkg.cfg
│   ├── shared/
│   └── docker-compose.yml
├── .github/workflows/      # CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## License

MIT
