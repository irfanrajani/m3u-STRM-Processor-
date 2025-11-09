#!/bin/bash

# IPTV Stream Manager - Quick Start Script

set -e

echo "======================================"
echo "IPTV Stream Manager - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env 2>/dev/null || echo "Warning: .env.example not found, using defaults"
fi

# Create output directories
echo "📁 Creating output directories..."
mkdir -p output/{playlists,strm_files,epg}
mkdir -p logs

echo "✅ Directories created"
echo ""

# Start Docker Compose
echo "🚀 Starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "======================================"
echo "✅ IPTV Stream Manager is starting!"
echo "======================================"
echo ""
echo "📍 Web Interface: http://localhost:8080"
echo "📍 API Documentation: http://localhost:8080/docs"
echo ""
echo "📖 Next steps:"
echo "  1. Open http://localhost:8080 in your browser"
echo "  2. Add your IPTV providers"
echo "  3. Click 'Sync' to fetch channels"
echo ""
echo "📚 For detailed instructions, see:"
echo "  - TESTING.md (test with your providers)"
echo "  - USAGE.md (full usage guide)"
echo "  - INSTALLATION.md (installation details)"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
