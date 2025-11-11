#!/bin/bash

# IPTV Stream Manager - Easy Setup Script
# Just run: ./start.sh

echo "🚀 Starting IPTV Stream Manager..."

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p output logs data

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 5

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T backend alembic upgrade head

# Initialize database
echo "👤 Creating admin user..."
docker-compose exec -T backend python -m app.cli.init_db

echo ""
echo "✅ IPTV Stream Manager is ready!"
echo ""
echo "🌐 Open http://localhost:8080"
echo "👤 Login: admin / admin (change this!)"
echo ""
echo "📋 Next steps:"
echo "   1. Go to Providers and add your IPTV sources"
echo "   2. Click 'Sync' to import channels"
echo "   3. Enjoy merged, quality-prioritized streams!"
echo ""
echo "🛠️  Useful commands:"
echo "   docker-compose logs -f        # View logs"
echo "   docker-compose restart        # Restart services"
echo "   docker-compose down           # Stop everything"
