#!/bin/sh
set -euo pipefail

echo "🚀 IPTV Stream Manager container starting..."

mkdir -p /app/data /app/logs /app/output
mkdir -p "$(dirname /app/logs/app.log)"

# Derive DB params from env (fallbacks)
DB_USER="${POSTGRES_USER:-iptv_user}"
DB_PASS="${POSTGRES_PASSWORD:-iptv_secure_pass_change_me}"
DB_NAME="${POSTGRES_DB:-iptv_db}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Build DATABASE_URL
export DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Generate .env only if missing (no hard-coded password divergence)
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

python - <<'PYCODE'
import os, asyncio, asyncpg, sys
DB_URL = os.environ["DATABASE_URL"]
parts = DB_URL.split("://",1)[1]
creds, host_part = parts.split("@",1)
user, password = creds.split(":",1)
host_port, dbname = host_part.split("/",1)
host, port = host_port.split(":",1)
async def probe():
    for attempt in range(50):
        try:
            conn = await asyncpg.connect(user=user, password=password, host=host, port=int(port), database=dbname)
            await conn.close()
            print("✅ PostgreSQL reachable.")
            return True
        except asyncpg.InvalidPasswordError:
            print("❌ Invalid PostgreSQL password for user:", user)
            return False
        except Exception as e:
            import time
            time.sleep(0.4)
    print("❌ PostgreSQL not reachable after retries.")
    return False
ok = asyncio.run(probe())
sys.exit(0 if ok else 2)
PYCODE

if [ $? -eq 2 ]; then
  echo "Aborting startup: database unreachable."
  exit 1
fi

# Skip migrations if password invalid (auth failed earlier)
if ! python - <<'PYCODE'
import os, asyncpg, asyncio, sys
url = os.environ["DATABASE_URL"]
creds, rest = url.split("://",1)[1].split("@",1)
user, pwd = creds.split(":",1)
hostport, db = rest.split("/",1)
host, port = hostport.split(":",1)
async def check():
    try:
        c = await asyncpg.connect(user=user,password=pwd,host=host,port=int(port),database=db)
        await c.close()
        return True
    except asyncpg.InvalidPasswordError:
        print("⚠️ Skipping migrations: password auth failed.")
        return False
res = asyncio.run(check())
sys.exit(0 if res else 3)
PYCODE; then
  echo "➡️ Starting API without migrations (fix password or drop volume)."
else
  if command -v alembic >/dev/null 2>&1; then
    echo "🔄 Running migrations..."
    if ! alembic upgrade head; then
      echo "⚠️ Migration failure (continuing)."
    fi
  fi
fi

echo "✅ Launching Uvicorn"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
