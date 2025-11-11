#!/bin/sh
set -euo pipefail

echo "🚀 IPTV Stream Manager container starting..."

# Directories
mkdir -p /app/data /app/logs /app/output

# Derive DB params from env
DB_USER="${POSTGRES_USER:-iptv_user}"
DB_PASS="${POSTGRES_PASSWORD:-iptv_secure_pass_change_me}"
DB_NAME="${POSTGRES_DB:-iptv_db}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Build DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

echo "📝 DB Config: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Generate .env only if missing
if [ ! -f /app/data/.env ]; then
  cat > /app/data/.env <<EOF
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
CELERY_BROKER_URL=${CELERY_BROKER_URL:-redis://redis:6379/0}
CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-redis://redis:6379/0}
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3001","http://localhost:8000"]
BACKEND_PORT=8000
FRONTEND_PORT=3001
EOF
  echo "✅ Created /app/data/.env"
fi

echo "⏳ Waiting for PostgreSQL (${DB_HOST}:${DB_PORT})..."

# Test database connection
python - <<'PYCODE'
import os, asyncio, asyncpg, sys, time

DB_URL = os.environ["DATABASE_URL"]
parts = DB_URL.split("://",1)[1]
creds, host_part = parts.split("@",1)
user, password = creds.split(":",1)
host_port, dbname = host_part.split("/",1)
host, port = host_port.split(":",1)

async def probe():
    for attempt in range(30):
        try:
            conn = await asyncpg.connect(
                user=user, 
                password=password, 
                host=host, 
                port=int(port), 
                database=dbname,
                timeout=5
            )
            await conn.close()
            print(f"✅ PostgreSQL connection successful (attempt {attempt+1})")
            return True
        except asyncpg.InvalidPasswordError as e:
            print(f"❌ Invalid password for user '{user}'")
            print(f"💡 Fix: Ensure docker-compose.yml POSTGRES_PASSWORD matches Dockerfile default")
            print(f"💡 Or run: docker-compose down -v && docker-compose up -d")
            return False
        except Exception as e:
            if attempt < 29:
                time.sleep(1)
            else:
                print(f"❌ Database unreachable after 30 attempts: {e}")
                return False
    return False

ok = asyncio.run(probe())
sys.exit(0 if ok else 1)
PYCODE

if [ $? -ne 0 ]; then
  echo "❌ Database connection failed. Exiting."
  exit 1
fi

# Run migrations
if command -v alembic >/dev/null 2>&1; then
  echo "🔄 Running migrations..."
  if ! alembic upgrade head; then
    echo "⚠️ Migration failed (continuing anyway)"
  else
    echo "✅ Migrations complete"
  fi
fi

echo "✅ Launching Uvicorn on port 8000"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000