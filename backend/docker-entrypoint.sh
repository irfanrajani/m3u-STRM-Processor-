#!/bin/sh
set -euo pipefail

echo "🚀 IPTV Stream Manager container starting..."

# Normalize line endings (in case CRLF slipped in)
dos2unix 2>/dev/null || true

# Directories
mkdir -p /app/data /app/logs /app/output

# If log file directory missing ensure it's there
mkdir -p "$(dirname /app/logs/app.log)"

# Generate .env if missing (minimal bootstrap if backend logic failed earlier)
if [ ! -f /app/data/.env ]; then
  python - <<'PYCODE'
import secrets, json, pathlib
env_path = pathlib.Path("/app/data/.env")
secret = secrets.token_urlsafe(32)
env_path.write_text(f"""SECRET_KEY={secret}
DATABASE_URL=postgresql+asyncpg://iptv_user:iptv_secure_pass_change_me@db:5432/iptv_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3001","http://localhost:8000"]
BACKEND_PORT=8000
FRONTEND_PORT=3001
""")
print("✅ Bootstrap .env written")
PYCODE
fi

# Optional dependency sanity (avoid psycopg2 sync driver)
python - <<'PYCODE'
import pkgutil, sys
bad = []
if pkgutil.find_loader("psycopg2"):
    bad.append("psycopg2 (synchronous driver present; prefer asyncpg)")
if bad:
    print("⚠️ Warning:", ", ".join(bad))
PYCODE

# Run alembic migrations (ignore failure but report)
if command -v alembic >/dev/null 2>&1; then
  echo "🔄 Running migrations (async)..."
  if ! alembic upgrade head; then
    echo "⚠️ Alembic failed; continuing startup"
  fi
fi

echo "✅ Starting API (Uvicorn)"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000