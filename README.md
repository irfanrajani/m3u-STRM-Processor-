# M3U to STRM Processor

A web application that converts M3U playlist files into individual STRM files for use with media servers like Plex, Jellyfin, or Emby.

## Features

- Web-based interface for easy M3U processing
- Converts M3U playlists to individual STRM files
- Docker support for easy deployment
- QNAP package (.qpkg) for native QNAP NAS integration

## Quick Start with Docker

### Pull from GitHub Container Registry

```bash
docker pull ghcr.io/irfanrajani/m3u-strm-processor:latest
docker run -p 8080:8080 -v /path/to/output:/output ghcr.io/irfanrajani/m3u-strm-processor:latest
```

### Build Locally

```bash
docker build -t m3u-strm-processor .
docker run -p 8080:8080 -v /path/to/output:/output m3u-strm-processor
```

### Using Docker Compose

```bash
docker-compose up -d
```

## QNAP Installation

1. Download the latest `.qpkg` file from the [Actions artifacts](../../actions)
2. Log into your QNAP web interface
3. Open App Center
4. Click "Install Manually" (gear icon)
5. Upload the `.qpkg` file
6. Access the app at `http://your-qnap-ip:8080`

## Usage

1. Open the web interface at `http://localhost:8080`
2. Enter the URL of your M3U playlist
3. Specify the output path (relative to `/output` volume)
4. Click "Create STRM Files"
5. STRM files will be generated in the specified output directory

## Development

### Requirements

- Python 3.9+
- Node.js 18+
- Docker (optional)

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
│   └── main.py            # Main application file
├── frontend/              # React frontend
│   ├── src/
│   └── package.json
├── qnap/                  # QNAP package files
│   ├── qpkg.cfg          # Package configuration
│   ├── shared/           # Startup scripts
│   └── docker-compose.yml
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Local development compose
└── requirements.txt      # Python dependencies
```

## License

MIT
