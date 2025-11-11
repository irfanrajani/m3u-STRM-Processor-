#!/bin/bash
echo "🔍 Checking Python import issues..."
echo ""

echo "1️⃣ Checking alembic/env.py line 9:"
LINE9=$(sed -n '9p' backend/alembic/env.py)
if [[ "$LINE9" == *"from app.core.config import settings"* ]]; then
    echo "   ✅ CORRECT: $LINE9"
else
    echo "   ❌ WRONG: $LINE9"
    echo "   Should be: from app.core.config import settings"
fi

echo ""
echo "2️⃣ Checking if config.py exports settings:"
if grep -q "^settings = Settings()" backend/app/core/config.py; then
    echo "   ✅ FOUND: settings = Settings()"
else
    echo "   ❌ MISSING: settings = Settings() not found in config.py"
fi

echo ""
echo "3️⃣ Checking for old 'import settings' (should not exist):"
if grep -q "^import settings$" backend/alembic/env.py; then
    echo "   ❌ FOUND BAD IMPORT: 'import settings' exists in env.py"
else
    echo "   ✅ GOOD: No bare 'import settings' found"
fi

echo ""
echo "4️⃣ Docker status:"
docker compose ps
