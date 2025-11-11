#!/bin/bash
set -e

echo "🚀 Starting IPTV Stream Manager..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Database
POSTGRES_USER=iptv_user
POSTGRES_PASSWORD=iptv_pass
POSTGRES_DB=iptv_db
DATABASE_URL=postgresql://iptv_user:iptv_pass@db:5432/iptv_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
EOF
    echo "✅ .env file created"
fi

# Create docker-compose file if it doesn't exist
if [ ! -f docker-compose.yml ]; then
    echo "📝 Creating docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-iptv_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-iptv_pass}
      POSTGRES_DB: ${POSTGRES_DB:-iptv_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-iptv_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ghcr.io/irfanrajani/m3u-strm-processor:latest
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
      - DEBUG=${DEBUG:-false}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    ports:
      - "8000:8000"
      - "3000:3000"
    volumes:
      - ./data:/app/data

volumes:
  postgres_data:
EOF
    echo "✅ docker-compose.yml created"
fi

# Start with docker-compose
echo "🐳 Starting all services..."
docker-compose up -d

echo ""
echo "✅ IPTV Stream Manager is starting!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "⚠️  First time? Wait 30 seconds for database setup, then visit http://localhost:3000"
