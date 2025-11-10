# GitHub Actions - Fix Import Check

## Problem

The "Check imports" step is failing because your code requires environment variables to import:
```
DATABASE_URL, REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND
```

## Solution

Update the `.github/workflows/test.yml` file on GitHub.

---

## Step-by-Step Fix

### 1. Go to GitHub
Navigate to: `.github/workflows/test.yml`

### 2. Find the "Check imports" Step

Look for this section (around line 55-70):

```yaml
    - name: Check imports
      run: |
        cd backend
        python -c "
        import sys
        sys.path.insert(0, '.')

        # Try importing all main modules
        try:
            from app.core import config, database, security, auth
            ...
```

### 3. Replace It With This

```yaml
    - name: Check imports
      env:
        DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        REDIS_URL: redis://localhost:6379/0
        CELERY_BROKER_URL: redis://localhost:6379/0
        CELERY_RESULT_BACKEND: redis://localhost:6379/0
        SECRET_KEY: test-secret-key-for-ci
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
```

**Key Change:** Added the `env:` section with all required environment variables.

---

## Complete Fixed Workflow Section

Here's the complete "backend-tests" job with the fix applied:

```yaml
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
      env:
        DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        REDIS_URL: redis://localhost:6379/0
        CELERY_BROKER_URL: redis://localhost:6379/0
        CELERY_RESULT_BACKEND: redis://localhost:6379/0
        SECRET_KEY: test-secret-key-for-ci
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
```

---

## How to Apply This Fix

### Option 1: Edit on GitHub (Recommended)

1. Go to: https://github.com/irfanrajani/m3u-STRM-Processor-/blob/main/.github/workflows/test.yml
2. Click the **pencil icon** (Edit this file)
3. Find the "Check imports" step
4. Add the `env:` section as shown above
5. Click **"Commit changes"**

### Option 2: Replace Entire File

If easier, replace the entire file contents with the complete workflow from `WORKFLOW_FIX_GUIDE.md` (which already has this fix).

---

## After Applying the Fix

Once you commit the change:
1. GitHub Actions will run again automatically
2. The "Check imports" step should now **PASS** ✅
3. Backend tests should complete successfully

---

## Expected Result

```
✓ All imports successful
```

Instead of:
```
❌ pydantic_core._pydantic_core.ValidationError: 4 validation errors
```

---

**This is a quick 2-minute fix on GitHub!** Just add those environment variables to the workflow. 🚀
