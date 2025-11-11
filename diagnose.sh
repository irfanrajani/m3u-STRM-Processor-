#!/bin/bash
echo "🔍 Running full diagnostic..."
echo "============================"

echo -e "\n1. CONTAINER STATUS:"
docker compose ps

echo -e "\n2. LATEST BACKEND LOGS (last 50 lines):"
docker compose logs backend --tail=50

echo -e "\n3. CHECKING FRONTEND FILES INSIDE THE CONTAINER:"
echo "Checking contents of /app/frontend/dist/ ..."
docker compose exec backend ls -lA /app/frontend/dist/ 2>/dev/null || echo "   ❌ ERROR: Could not list files in /app/frontend/dist/. The backend container might be crashing."

echo -e "\n4. CHECKING FOR index.html INSIDE THE CONTAINER:"
docker compose exec backend ls -l /app/frontend/dist/index.html 2>/dev/null || echo "   ❌ ERROR: index.html not found in /app/frontend/dist/"

echo -e "\n5. TESTING NETWORK CONNECTIVITY:"
curl -s -o /dev/null -w "   - API Health Check (http://localhost:8000/api/health): HTTP %{http_code}\n" http://localhost:8000/api/health || echo "   - API Health Check: FAILED to connect"
curl -s -o /dev/null -w "   - Frontend Root (http://localhost:8000): HTTP %{http_code}\n" http://localhost:8000 || echo "   - Frontend Root: FAILED to connect"

echo -e "\nDiagnostic complete. Please provide this full output."
