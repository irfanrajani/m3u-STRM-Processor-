#!/bin/bash

# IPTV Stream Manager - QNAP Deployment Script

set -e

echo "========================================"
echo "IPTV Stream Manager - QNAP Deployment"
echo "========================================"
echo ""

# Find docker-compose command
DOCKER_COMPOSE=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif command -v /usr/local/bin/docker-compose &> /dev/null; then
    DOCKER_COMPOSE="/usr/local/bin/docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ docker-compose not found!"
    echo "Please install Docker Compose or use Container Station"
    exit 1
fi

echo "✅ Found docker-compose: $DOCKER_COMPOSE"
echo ""

# Check if images are loaded
echo "📦 Checking Docker images..."
if ! docker images | grep -q "iptv-backend"; then
    echo "❌ iptv-backend:local image not found!"
    echo "Please load the image first:"
    echo "  docker load < iptv-backend-fixed.tar.gz"
    exit 1
fi

if ! docker images | grep -q "iptv-frontend"; then
    echo "⚠️  iptv-frontend:local image not found!"
    echo "Frontend will not be available. Load it with:"
    echo "  docker load < iptv-frontend.tar.gz"
fi

echo "✅ Docker images ready"
echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE -f docker-compose.deploy.yml down 2>/dev/null || true
echo ""

# Remove old containers
echo "🗑️  Removing old containers..."
docker rm -f iptv_backend iptv_celery_worker iptv_celery_beat iptv_frontend iptv_nginx 2>/dev/null || true
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p output/{playlists,strm_files,epg}
mkdir -p logs
echo "✅ Directories created"
echo ""

# Start services
echo "🚀 Starting services..."
$DOCKER_COMPOSE -f docker-compose.deploy.yml up -d
echo ""

# Wait for database
echo "⏳ Waiting for database..."
sleep 15
echo ""

# Run migrations
echo "🔧 Running database migrations..."
docker exec iptv_backend alembic upgrade head
echo "✅ Migrations complete"
echo ""

# Check service status
echo "🔍 Checking service status..."
$DOCKER_COMPOSE -f docker-compose.deploy.yml ps
echo ""

# Wait for backend
echo "⏳ Waiting for backend to start..."
sleep 5
echo ""

# Test backend
echo "🧪 Testing backend API..."
if curl -s http://localhost:8201/api/status > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
else
    echo "⚠️  Backend may not be ready yet. Check logs:"
    echo "  docker logs iptv_backend"
fi
echo ""

echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "📍 Web Interface: http://192.168.68.75:8080"
echo "📍 API: http://192.168.68.75:8201"
echo "📍 API Docs: http://192.168.68.75:8201/docs"
echo ""
echo "📖 Next steps:"
echo "  1. Open http://192.168.68.75:8080 in your browser"
echo "  2. Add your IPTV providers (see TESTING.md)"
echo "  3. Sync providers to fetch channels"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: $DOCKER_COMPOSE -f docker-compose.deploy.yml logs -f"
echo "  - Stop: $DOCKER_COMPOSE -f docker-compose.deploy.yml down"
echo "  - Restart: $DOCKER_COMPOSE -f docker-compose.deploy.yml restart"
echo ""
