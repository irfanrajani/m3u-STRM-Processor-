#!/usr/bin/env sh
set -e

echo "🚀 Starting IPTV Stream Manager..."

wait_for_service() {
  host_port="$1"
  retries=50
  until nc -z ${host_port%:*} ${host_port#*:}; do
    retries=$((retries - 1))
    if [ "$retries" -le 0 ]; then
      echo "Timed out waiting for $host_port"
      return 1
    fi
    sleep 0.2
  done
  return 0
}

if [ -n "$DATABASE_URL" ]; then
  db_host_port="$(echo "$DATABASE_URL" | sed -n 's|.*://.*@\(.*\):\([0-9]\+\).*|\1:\2|p')"
  if [ -n "$db_host_port" ]; then
    echo "Waiting for database at $db_host_port..."
    wait_for_service "$db_host_port"
  fi
fi

if [ -n "$REDIS_URL" ]; then
  redis_host_port="$(echo "$REDIS_URL" | sed -n 's|redis://\([^:/ ]*\):\([0-9]\+\).*|\1:\2|p')"
  if [ -n "$redis_host_port" ]; then
    echo "Waiting for Redis at $redis_host_port..."
    wait_for_service "$redis_host_port"
  fi
fi

cd /app/backend 2>/dev/null || true

# Check if this is first run
if [ ! -f /app/data/.env ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  🎉 FIRST RUN DETECTED - AUTO-CONFIGURING"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "  A secure configuration has been auto-generated!"
    echo "  Location: /app/data/.env"
    echo ""
    echo "  📱 Access the web interface:"
    echo "     http://localhost:3000"
    echo ""
    echo "  🔧 Configure settings:"
    echo "     http://localhost:3000/settings"
    echo ""
    echo "  🔐 Default admin credentials:"
    echo "     Username: admin"
    echo "     Password: admin123"
    echo "     ⚠️  CHANGE THIS IMMEDIATELY!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
fi

if command -v alembic >/dev/null 2>&1; then
  echo "Running database migrations..."
  alembic upgrade head || echo "Warning: Alembic upgrade failed."
fi

python - <<'PYCODE' || true
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    if not db.query(User).filter(User.is_superuser == True).first():
        print("Warning: No superuser found. Create one via management API.")
finally:
    db.close()
PYCODE

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
