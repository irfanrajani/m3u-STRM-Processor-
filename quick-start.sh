#!/bin/bash
set -e

echo "🚀 Starting IPTV Stream Manager..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
SECRET_KEY=change-this-to-a-random-secret-key-in-production
DEBUG=true
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Database
POSTGRES_USER=iptv_user
POSTGRES_PASSWORD=iptv_pass
POSTGRES_DB=iptv_db
DATABASE_URL=postgresql+asyncpg://iptv_user:iptv_pass@db:5432/iptv_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
EOF
    echo "✅ .env file created"
fi

# ...existing code...