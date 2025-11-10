# M3U to STRM Processor

A web application that converts M3U playlist files into individual STRM files for use with media servers like Plex, Jellyfin, or Emby.

## Features

- 🎯 Web-based interface for easy M3U processing
- 📁 Converts M3U playlists to individual STRM files
- 🐳 Docker support for easy deployment
- 📦 QNAP package (.qpkg) for native QNAP NAS integration
- 🔒 Path sanitization to prevent directory traversal attacks
- 📝 Automatic filename sanitization

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

Access the application at `http://localhost:8080`

## QNAP Installation

1. Go to the [GitHub Actions](../../actions/workflows/build_qpkg.yml) page
2. Download the latest `.qpkg` file from the artifacts
3. Log into your QNAP web interface
4. Open **App Center**
5. Click **Install Manually** (gear icon in top-right)
6. Upload the `.qpkg` file
7. Access the app at `http://your-qnap-ip:8080`

**Note:** Requires Container Station to be installed on your QNAP.

## Usage

1. Open the web interface
2. Enter the URL of your M3U playlist
3. Specify the output path (relative to `/output` volume)
4. Click **Create STRM Files**
5. STRM files will be generated in the specified output directory

### Example

- **M3U URL:** `https://example.com/playlist.m3u`
- **Output Path:** `channels`
- **Result:** STRM files created in `/output/channels/`

## Project Structure

```
.
├── api/                    # FastAPI backend
│   └── main.py            # Main application file
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   ├── App.css       # Styles
│   │   └── main.jsx      # React entry point
│   └── package.json
├── qnap/                  # QNAP package files
│   ├── qpkg.cfg          # Package configuration
│   ├── shared/           # Startup scripts
│   └── docker-compose.yml # QNAP deployment config
├── .github/
│   └── workflows/        # CI/CD pipelines
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Local development
├── build_qpkg.sh         # QNAP package build script
└── requirements.txt      # Python dependencies
```

## Development

### Requirements

- Python 3.9+
- Node.js 18+
- Yarn
- Docker (optional)

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

### Building the QNAP Package Locally

```bash
# Download and extract QDK
wget https://github.com/qnap-dev/qdk2/releases/download/v2.4.0/qdk2_2.4.0-x86_64.tar.gz
tar -xvf qdk2_2.4.0-x86_64.tar.gz
export QDK_DIR=$(pwd)/qdk2

# Build the package
chmod +x build_qpkg.sh
./build_qpkg.sh

# Package will be in build/m3u-STRM-Processor.qpkg
```

## GitHub Actions Workflows

- **Test and Lint** - Runs on every push/PR to validate code
- **Build QPKG** - Builds QNAP package on push to main
- **Build and Publish Docker Image** - Publishes to GHCR on push to main
- **Build Docker Image for Download** - Manual workflow for creating downloadable images

## API Documentation

Once running, visit `http://localhost:8080/docs` for interactive API documentation.

### Endpoints

- `POST /process-m3u/` - Process M3U file and create STRM files
  - Body: `{ "m3u_url": "string", "output_path": "string" }`
  - Response: `{ "message": "string" }`

## Security

- Path traversal protection prevents writing outside `/output`
- Filename sanitization removes dangerous characters
- Request timeout (30s) prevents hanging connections
- Input validation via Pydantic models

## Troubleshooting

### QNAP Package Won't Start

1. Check Container Station is installed
2. Check logs: `cat /share/CACHEDEV1_DATA/.qpkg/m3u-STRM-Processor/qpkg.log`
3. Verify Docker image is pulled: `docker images | grep m3u-strm-processor`

### Frontend Not Loading

1. Verify frontend was built: check for `frontend/dist` directory
2. Check Docker build logs for frontend build errors
3. Ensure port 8080 is not blocked by firewall

### STRM Files Not Created

1. Check output volume is properly mounted
2. Verify output path permissions
3. Check application logs for errors

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Author

Irfan Rajani
