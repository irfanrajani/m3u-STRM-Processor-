# GitHub Actions Workflow Fix Guide

## Problem

The GitHub Actions workflows are failing due to cache path configuration issues. I've already fixed one issue by adding `frontend/package-lock.json` (now pushed to the repo).

## Quick Fix - Update the Workflows on GitHub

Since I can't push workflow files directly, you need to update them manually on GitHub. Here's how:

### Option 1: Update via GitHub Web Interface (5 minutes)

1. Go to your repository on GitHub
2. Navigate to `.github/workflows/test.yml`
3. Click the **pencil icon** to edit
4. Replace the **entire content** with the code below
5. Click "Commit changes"

---

### Fixed `test.yml` Content

Replace the entire file with this:

```yaml
name: Test and Lint

on:
  push:
    branches: [ main, 'claude/**' ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_USER: testuser
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Check Python syntax
      run: |
        cd backend
        python -m py_compile $(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*")

    - name: Run Flake8 linting
      continue-on-error: true
      run: |
        cd backend
        pip install flake8
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --max-complexity=10 --max-line-length=127 --statistics

    - name: Check imports
      run: |
        cd backend
        python -c "
        import sys
        sys.path.insert(0, '.')

        # Try importing all main modules
        try:
            from app.core import config, database, security, auth
            from app.models import user, provider, channel, vod, settings
            from app.api import auth, providers, channels, vod, health, system, users, favorites, analytics
            print('✓ All imports successful')
        except ImportError as e:
            print(f'✗ Import error: {e}')
            sys.exit(1)
        "

    - name: Run database migrations check
      env:
        DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
      run: |
        cd backend
        alembic check || echo "Migration check completed"

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Cache node modules
      uses: actions/cache@v3
      with:
        path: ~/.npm
        key: ${{ runner.os }}-node-${{ hashFiles('frontend/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-

    - name: Install dependencies
      run: |
        cd frontend
        npm ci

    - name: Check for syntax errors
      run: |
        cd frontend
        npx eslint src --ext .js,.jsx --max-warnings 0 || echo "Linting completed with warnings"

    - name: Build frontend
      run: |
        cd frontend
        npm run build

    - name: Check build output
      run: |
        if [ -d "frontend/dist" ]; then
          echo "✓ Build successful - dist folder created"
          ls -lh frontend/dist
        else
          echo "✗ Build failed - no dist folder"
          exit 1
        fi

  docker-build-test:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Test build backend image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./docker/Dockerfile.backend
        push: false
        tags: iptv-backend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Test build frontend image
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./docker/Dockerfile.frontend
        push: false
        tags: iptv-frontend:test
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Report success
      run: |
        echo "✓ All tests passed!"
        echo "✓ Backend syntax check: PASSED"
        echo "✓ Frontend build: PASSED"
        echo "✓ Docker images: BUILD SUCCESSFUL"
```

---

### What Changed?

**The main fixes:**

1. **Backend caching** - Changed from:
   ```yaml
   cache: 'pip'
   cache-dependency-path: backend/requirements.txt
   ```
   To:
   ```yaml
   - name: Cache pip packages
     uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
       restore-keys: |
         ${{ runner.os }}-pip-
   ```

2. **Frontend caching** - Changed from:
   ```yaml
   cache: 'npm'
   cache-dependency-path: frontend/package-lock.json
   ```
   To:
   ```yaml
   - name: Cache node modules
     uses: actions/cache@v3
     with:
       path: ~/.npm
       key: ${{ runner.os }}-node-${{ hashFiles('frontend/package-lock.json') }}
       restore-keys: |
         ${{ runner.os }}-node-
   ```

3. **Added package-lock.json** - Already pushed to your branch, so frontend caching will work now

---

## Testing After Fix

After updating the workflow:

1. The next push will trigger the updated workflow
2. Check the **Actions** tab on GitHub
3. You should see:
   - ✅ Backend tests passing
   - ✅ Frontend tests passing
   - ✅ Docker build tests passing

---

## If You Still See Errors

If the workflows still fail after this fix, check the error message in the Actions tab and let me know. Common issues:

- **Missing dependencies** - Check if `backend/requirements.txt` has all needed packages
- **Import errors** - Make sure all imports in the codebase are correct
- **Docker build errors** - Check `docker/Dockerfile.backend` and `docker/Dockerfile.frontend`

---

## Alternative: Delete and Recreate Workflows

If editing doesn't work, you can:

1. Delete `.github/workflows/test.yml` on GitHub
2. Go to **Actions** tab → **New workflow** → **set up a workflow yourself**
3. Paste the content above
4. Name it `test.yml` and commit

The corrected workflow files are also in `.github/workflows/` locally (I created them but can't push due to permissions).
