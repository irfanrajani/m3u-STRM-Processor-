#!/bin/bash

echo "=== Checking alembic/env.py line 9 ==="
sed -n '9p' backend/alembic/env.py

echo ""
echo "=== Checking config.py last 10 lines ==="
tail -10 backend/app/core/config.py

echo ""
echo "=== Checking if 'settings = Settings()' exists in config.py ==="
grep -n "settings = Settings()" backend/app/core/config.py

echo ""
echo "=== Checking if 'import settings' still exists in env.py (BAD) ==="
grep -n "^import settings" backend/alembic/env.py || echo "Good - no bare 'import settings' found"

echo ""
echo "=== Checking if 'from app.core.config import settings' exists in env.py (GOOD) ==="
grep -n "from app.core.config import settings" backend/alembic/env.py || echo "ERROR - correct import not found!"
