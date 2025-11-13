#!/bin/bash
set -e

echo "🚀 IPTV Stream Manager container starting..."
echo "📝 DB Config: ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL (${POSTGRES_HOST}:${POSTGRES_PORT})..."
MAX_TRIES=30
COUNT=0
until nc -z ${POSTGRES_HOST} ${POSTGRES_PORT} || [ $COUNT -eq $MAX_TRIES ]; do
  COUNT=$((COUNT+1))
  sleep 1
done

if [ $COUNT -eq $MAX_TRIES ]; then
  echo "❌ PostgreSQL not available after ${MAX_TRIES} seconds"
  exit 1
fi

echo "✅ PostgreSQL connection successful (attempt $COUNT)"

# Run migrations (with error handling for existing schema)
echo "🔄 Running migrations..."
cd /app/backend

# Check current revision
echo "📊 Checking current alembic revision..."
alembic current || echo "No current revision set"

echo "📊 Running alembic upgrade head..."
if alembic upgrade head 2>&1 | tee /tmp/migration.log; then
  echo "✅ Migrations completed successfully"
  echo "📊 Final revision:"
  alembic current
else
  EXIT_CODE=$?
  echo "❌ Migration failed with exit code: $EXIT_CODE"
  if grep -q "DuplicateTableError\|DuplicateColumnError" /tmp/migration.log; then
    echo "⚠️  Database already initialized, marking current revision..."
    alembic stamp head
    echo "✅ Migration state synchronized"
  else
    echo "⚠️ Migration failed - full output:"
    cat /tmp/migration.log
    echo "⚠️ Continuing anyway (this may cause errors)..."
  fi
fi

# Start the application
echo "✅ Launching Uvicorn on port ${BACKEND_PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-8000}