#!/bin/bash
echo "🔍 Pre-deployment verification..."

echo -e "\n1️⃣ Checking env.py import (should be 'from app.core.config import settings'):"
if grep -q "from app.core.config import settings" backend/alembic/env.py; then
    echo "   ✅ CORRECT"
else
    echo "   ❌ WRONG - run the fix above"
    grep -n "import.*settings" backend/alembic/env.py
fi

echo -e "\n2️⃣ Checking config.py exports settings:"
if grep -q "^settings = Settings()" backend/app/core/config.py; then
    echo "   ✅ FOUND on line $(grep -n '^settings = Settings()' backend/app/core/config.py | cut -d: -f1)"
else
    echo "   ❌ NOT FOUND"
fi

echo -e "\n3️⃣ Docker status:"
docker compose ps

echo -e "\n4️⃣ Recent backend logs (last 20 lines):"
docker compose logs backend --tail=20 2>/dev/null || echo "Backend not running yet"
