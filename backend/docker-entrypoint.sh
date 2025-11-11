```bash
#!/usr/bin/env sh
set -e

echo "🚀 Starting IPTV Stream Manager..."

# Create necessary directories
mkdir -p /app/data /app/logs /app/output

# Running database migrations...
alembic upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```