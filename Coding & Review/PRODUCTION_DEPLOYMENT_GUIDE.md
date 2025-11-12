# Production Deployment Guide
## M3U-STRM-Processor - Enterprise-Grade Deployment

**Version**: 1.0
**Last Updated**: 2025-01-12
**Target Environment**: Production (Cloud/On-Premise)

---

## Table of Contents

1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Environment Configuration](#2-environment-configuration)
3. [Database Migration Strategy](#3-database-migration-strategy)
4. [SSL/HTTPS Setup](#4-sslhttps-setup)
5. [Production Docker Compose](#5-production-docker-compose)
6. [Nginx Configuration](#6-nginx-configuration)
7. [Health Checks & Monitoring](#7-health-checks--monitoring)
8. [Backup & Disaster Recovery](#8-backup--disaster-recovery)
9. [Zero-Downtime Deployment](#9-zero-downtime-deployment)
10. [Rollback Procedures](#10-rollback-procedures)
11. [Security Hardening](#11-security-hardening)
12. [Performance Tuning](#12-performance-tuning)

---

## 1. Pre-Deployment Checklist

**Before deploying to production, ensure:**

### Critical Security Issues Fixed
- [ ] Change hardcoded admin password (`main.py:62`)
- [ ] Enable rate limiting on all endpoints
- [ ] Configure HTTPS/SSL certificates
- [ ] Update all default passwords in `.env`
- [ ] Review and secure firewall rules
- [ ] Enable CORS with specific origins only

### Performance Optimizations Applied
- [ ] Add database indexes (migration `004_add_performance_indexes.py`)
- [ ] Fix N+1 queries in health checks
- [ ] Configure connection pool properly
- [ ] Enable Redis caching
- [ ] Configure proper timeout values

### Testing Completed
- [ ] Load testing (1000+ concurrent users)
- [ ] Database migration tested on staging
- [ ] Backup/restore procedures verified
- [ ] Rollback plan tested
- [ ] Health check endpoints working
- [ ] SSL certificate valid and working

### Infrastructure Ready
- [ ] Domain name configured
- [ ] DNS records updated
- [ ] SSL certificate obtained
- [ ] Firewall rules configured
- [ ] Monitoring/alerting setup
- [ ] Backup storage configured

---

## 2. Environment Configuration

### Production Environment Variables

Create `/backend/.env.production`:

```bash
# ==================================
# APPLICATION SETTINGS
# ==================================
APP_NAME=IPTV Stream Manager
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=<GENERATE_RANDOM_64_CHAR_STRING>
LOG_LEVEL=INFO

# ==================================
# EXTERNAL URL (Your Domain)
# ==================================
EXTERNAL_URL=https://iptv.yourdomain.com
ALLOWED_ORIGINS=["https://iptv.yourdomain.com"]

# ==================================
# DATABASE (PostgreSQL)
# ==================================
DATABASE_URL=postgresql+asyncpg://iptv_user:CHANGE_THIS_PASSWORD@postgres:5432/iptv_manager
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false

# ==================================
# REDIS
# ==================================
REDIS_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/0
CELERY_BROKER_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/0
CELERY_RESULT_BACKEND=redis://:CHANGE_THIS_PASSWORD@redis:6379/1

# ==================================
# SECURITY
# ==================================
# JWT
JWT_SECRET_KEY=<GENERATE_RANDOM_64_CHAR_STRING>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Hashing (Argon2)
ARGON2_TIME_COST=2
ARGON2_MEMORY_COST=65536
ARGON2_PARALLELISM=4

# ==================================
# RATE LIMITING
# ==================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/2

# ==================================
# FILE PATHS (Docker Volumes)
# ==================================
OUTPUT_DIR=/app/output
PLAYLISTS_DIR=/app/output/playlists
STRM_DIR=/app/output/strm_files
EPG_DIR=/app/output/epg
LOG_FILE=/app/logs/app.log

# ==================================
# HEALTH CHECKS
# ==================================
DEFAULT_HEALTH_CHECK_TIMEOUT=10
DEFAULT_HEALTH_CHECK_SCHEDULE=0 3 * * *
MAX_CONCURRENT_HEALTH_CHECKS=100
VERIFY_SSL=true

# ==================================
# PERFORMANCE
# ==================================
ENABLE_BITRATE_ANALYSIS=true
FFPROBE_TIMEOUT=15
ENABLE_LOGO_MATCHING=true
DEFAULT_FUZZY_MATCH_THRESHOLD=85

# ==================================
# HDHR EMULATION
# ==================================
HDHR_PROXY_MODE=direct
HDHR_DEVICE_ID=IPTV-MGR-PROD
HDHR_TUNER_COUNT=6

# ==================================
# MONITORING
# ==================================
ENABLE_PROMETHEUS_METRICS=true
PROMETHEUS_PORT=9090
```

### Generate Secure Random Keys

```bash
# Generate SECRET_KEY and JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate strong database password
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment-Specific Configs

**Staging** (`.env.staging`):
- Same as production but with staging domain
- Can use self-signed SSL for testing
- Debug logging enabled

**Production** (`.env.production`):
- Must use valid SSL certificate
- Debug logging disabled
- Strict CORS policy
- Rate limiting aggressive

---

## 3. Database Migration Strategy

### Zero-Downtime Migration Process

#### Step 1: Backup Current Database

```bash
# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec iptv-postgres pg_dump -U iptv_user iptv_manager > backup_${TIMESTAMP}.sql

# Compress backup
gzip backup_${TIMESTAMP}.sql

# Upload to secure storage (S3/Backblaze)
aws s3 cp backup_${TIMESTAMP}.sql.gz s3://your-backup-bucket/db-backups/
```

#### Step 2: Test Migration on Staging

```bash
# Copy production data to staging
psql -U iptv_user -d iptv_manager_staging < backup_${TIMESTAMP}.sql

# Run migrations on staging
docker exec iptv-backend alembic upgrade head

# Verify data integrity
docker exec iptv-backend python -m pytest tests/test_migrations.py
```

#### Step 3: Schedule Maintenance Window (Optional)

For major schema changes:
- Notify users 24-48 hours in advance
- Schedule during lowest traffic period (typically 2-5 AM)
- Estimated downtime: 5-15 minutes

#### Step 4: Production Migration

```bash
# Put app in maintenance mode (optional)
docker exec iptv-nginx cp /etc/nginx/maintenance.html /usr/share/nginx/html/index.html

# Stop backend to prevent writes
docker-compose stop backend celery-worker celery-beat

# Backup current state
docker exec iptv-postgres pg_dump -U iptv_user iptv_manager > pre_migration_backup.sql

# Run migrations
docker-compose run --rm backend alembic upgrade head

# Verify migration success
docker-compose run --rm backend alembic current

# Start services
docker-compose up -d

# Remove maintenance mode
docker exec iptv-nginx cp /etc/nginx/production.html /usr/share/nginx/html/index.html
```

#### Step 5: Verify Migration

```bash
# Check application logs
docker-compose logs -f backend | grep -i error

# Test critical endpoints
curl https://iptv.yourdomain.com/api/health
curl https://iptv.yourdomain.com/api/providers

# Monitor database connections
docker exec iptv-postgres psql -U iptv_user -d iptv_manager -c "SELECT count(*) FROM pg_stat_activity;"
```

### Migration Rollback Plan

If migration fails:

```bash
# Stop services immediately
docker-compose stop backend celery-worker celery-beat

# Restore database from backup
docker exec -i iptv-postgres psql -U iptv_user -d iptv_manager < pre_migration_backup.sql

# Downgrade Alembic to previous version
docker-compose run --rm backend alembic downgrade -1

# Restart services
docker-compose up -d

# Verify rollback
curl https://iptv.yourdomain.com/api/health
```

---

## 4. SSL/HTTPS Setup

### Option A: Let's Encrypt (Recommended - Free)

#### Install Certbot

```bash
# On host machine
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

#### Obtain Certificate

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
  -d iptv.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --non-interactive

# Certificates will be at:
# /etc/letsencrypt/live/iptv.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/iptv.yourdomain.com/privkey.pem
```

#### Configure Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (renews every 12 hours)
echo "0 */12 * * * certbot renew --quiet --post-hook 'docker-compose restart nginx'" | sudo crontab -
```

#### Update Docker Compose to Use Certificates

```yaml
# docker-compose.prod.yml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
    - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
```

### Option B: Cloudflare (Easiest - Free)

1. Point domain to Cloudflare DNS
2. Enable "Full (Strict)" SSL mode
3. Cloudflare handles SSL automatically
4. Origin certificate from Cloudflare dashboard → install on server

**Benefits:**
- Free SSL
- DDoS protection
- CDN caching
- No cert renewal needed

### Option C: Commercial SSL (Paid)

Buy from DigiCert, Sectigo, etc. and install manually.

---

## 5. Production Docker Compose

### File: `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  # ==================================
  # DATABASE
  # ==================================
  postgres:
    image: postgres:15-alpine
    container_name: iptv-postgres-prod
    restart: unless-stopped
    environment:
      POSTGRES_DB: iptv_manager
      POSTGRES_USER: iptv_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"  # Only localhost access
    networks:
      - iptv-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U iptv_user -d iptv_manager"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  # ==================================
  # REDIS
  # ==================================
  redis:
    image: redis:7-alpine
    container_name: iptv-redis-prod
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"  # Only localhost access
    networks:
      - iptv-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  # ==================================
  # BACKEND API
  # ==================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: iptv-backend-prod
    restart: unless-stopped
    env_file:
      - .env.production
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - iptv-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      replicas: 2  # Run 2 instances for high availability
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  # ==================================
  # CELERY WORKERS
  # ==================================
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: iptv-celery-worker-prod
    restart: unless-stopped
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4 --max-tasks-per-child=1000
    env_file:
      - .env.production
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - iptv-network
    deploy:
      replicas: 2  # Scale workers for heavy tasks
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G

  # ==================================
  # CELERY BEAT (Scheduler)
  # ==================================
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: iptv-celery-beat-prod
    restart: unless-stopped
    command: celery -A app.tasks.celery_app beat --loglevel=info
    env_file:
      - .env.production
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - iptv-network
    deploy:
      replicas: 1  # Only 1 instance of beat
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ==================================
  # FRONTEND
  # ==================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
      args:
        VITE_API_URL: https://iptv.yourdomain.com/api
    container_name: iptv-frontend-prod
    restart: unless-stopped
    networks:
      - iptv-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ==================================
  # NGINX (Reverse Proxy)
  # ==================================
  nginx:
    image: nginx:alpine
    container_name: iptv-nginx-prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - iptv-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  iptv-network:
    driver: bridge
```

### Production Dockerfile for Backend

```dockerfile
# /backend/Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development target
FROM base as development
ENV ENVIRONMENT=development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production target
FROM base as production
ENV ENVIRONMENT=production

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 iptv && chown -R iptv:iptv /app
USER iptv

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
```

### Deploy to Production

```bash
# Pull latest code
git pull origin main

# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify health
curl https://iptv.yourdomain.com/api/health
```

---

## 6. Nginx Configuration

### File: `nginx/nginx.prod.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Upstream backends
    upstream backend {
        least_conn;
        server backend:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream frontend {
        server frontend:3001;
    }

    # HTTP → HTTPS Redirect
    server {
        listen 80;
        listen [::]:80;
        server_name iptv.yourdomain.com;

        # Allow Let's Encrypt verification
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect all other traffic to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name iptv.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/iptv.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/iptv.yourdomain.com/privkey.pem;

        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_stapling on;
        ssl_stapling_verify on;

        # HSTS (uncomment after testing)
        # add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Root location (Frontend)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth endpoints (stricter rate limit)
        location /api/auth/ {
            limit_req zone=auth burst=5 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket timeout
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }

        # HDHomeRun endpoints (streaming)
        location /discover.json {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_buffering off;
        }

        location /lineup.json {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_buffering off;
        }

        location /auto/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_buffering off;
            proxy_read_timeout 3600s;
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://backend/api/health;
        }

        # Static files (if serving directly)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Block access to sensitive files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
```

---

## 7. Health Checks & Monitoring

### Add Health Endpoint to Backend

```python
# /backend/app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check"""

    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "checks": {}
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"

    # Redis check
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"

    # Celery check (optional)
    try:
        from app.tasks.celery_app import celery
        inspector = celery.control.inspect()
        stats = inspector.stats()
        if stats:
            health_status["checks"]["celery"] = "healthy"
        else:
            health_status["checks"]["celery"] = "no workers"
    except Exception as e:
        health_status["checks"]["celery"] = f"unhealthy: {str(e)}"

    return health_status
```

### Prometheus Metrics (Optional)

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# /backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### External Monitoring Services

**Uptime Monitoring:**
- UptimeRobot (free, 50 monitors)
- Better Uptime
- Pingdom

**Health Check URL:**
```
https://iptv.yourdomain.com/api/health
```

Check every 5 minutes, alert if down.

---

## 8. Backup & Disaster Recovery

### Automated Database Backups

**Backup Script** (`/scripts/backup-db.sh`):

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="iptv_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec iptv-postgres-prod pg_dump -U iptv_user -d iptv_manager > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3/Backblaze (optional)
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://your-bucket/db-backups/
fi

# Delete old backups (keep last 30 days)
find $BACKUP_DIR -name "iptv_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**Cron Job** (daily at 2 AM):

```bash
0 2 * * * /scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop backend celery-worker celery-beat

# Restore database
gunzip -c /backups/postgres/iptv_backup_20250112_020000.sql.gz | \
  docker exec -i iptv-postgres-prod psql -U iptv_user -d iptv_manager

# Restart application
docker-compose -f docker-compose.prod.yml start backend celery-worker celery-beat

# Verify
curl https://iptv.yourdomain.com/api/health
```

### Configuration Backup

```bash
# Backup .env and configs
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env.production \
  nginx/nginx.prod.conf \
  docker-compose.prod.yml

# Store securely (encrypted)
gpg --encrypt --recipient admin@yourdomain.com config_backup_20250112.tar.gz
```

---

## 9. Zero-Downtime Deployment

### Blue-Green Deployment Strategy

**Step 1: Deploy to "Green" Environment**

```bash
# Build new version
docker-compose -f docker-compose.prod.yml build

# Tag current as "blue"
docker tag iptv-backend:latest iptv-backend:blue

# Deploy new version as "green"
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
```

**Step 2: Health Check Green**

```bash
# Check new backend health
docker exec iptv-backend-prod curl http://localhost:8000/health
```

**Step 3: Switch Traffic**

```bash
# Update nginx to point to new backend
docker-compose -f docker-compose.prod.yml restart nginx

# Monitor for errors
docker-compose logs -f nginx backend
```

**Step 4: Rollback if Needed**

```bash
# Rollback to blue
docker tag iptv-backend:blue iptv-backend:latest
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
docker-compose restart nginx
```

### Rolling Update (Docker Swarm)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml iptv

# Update with zero downtime
docker service update --image iptv-backend:v2 iptv_backend

# Rollback
docker service rollback iptv_backend
```

---

## 10. Rollback Procedures

### Emergency Rollback Checklist

**Scenario A: Bad Code Deployment**

```bash
# 1. Stop new version
docker-compose -f docker-compose.prod.yml stop backend

# 2. Restore previous image
docker tag iptv-backend:previous iptv-backend:latest

# 3. Start previous version
docker-compose -f docker-compose.prod.yml up -d backend

# 4. Verify
curl https://iptv.yourdomain.com/api/health
```

**Scenario B: Bad Database Migration**

```bash
# 1. Stop services
docker-compose stop backend celery-worker celery-beat

# 2. Restore database
gunzip -c /backups/postgres/pre_migration_backup.sql.gz | \
  docker exec -i iptv-postgres-prod psql -U iptv_user -d iptv_manager

# 3. Downgrade migration
docker-compose run --rm backend alembic downgrade -1

# 4. Restart services
docker-compose up -d

# 5. Verify
curl https://iptv.yourdomain.com/api/health
```

---

## 11. Security Hardening

### Firewall Configuration (UFW)

```bash
# Default deny
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Fail2Ban for Brute Force Protection

```bash
# Install
sudo apt install fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Add nginx jail
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
```

### Docker Security

```bash
# Run containers as non-root
USER iptv

# Use read-only filesystem where possible
docker run --read-only ...

# Limit resources
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## 12. Performance Tuning

### PostgreSQL Tuning

```sql
-- /etc/postgresql/postgresql.conf

-- Memory
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 16MB
maintenance_work_mem = 256MB

-- Connections
max_connections = 200

-- Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB

-- Query Planning
random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200
```

### Redis Tuning

```bash
# maxmemory for cache
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence (optional, reduces performance)
save ""  # Disable RDB snapshots for cache-only use

# Append-only file (optional)
appendonly no
```

### Application Performance

```python
# /backend/app/core/config.py

# Connection pool
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 40

# Celery workers
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Health checks
MAX_CONCURRENT_HEALTH_CHECKS = 100
```

---

## Quick Start Commands

```bash
# Initial setup
cp .env.example .env.production
# Edit .env.production with your settings
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Health check
curl https://iptv.yourdomain.com/api/health

# Backup database
./scripts/backup-db.sh

# Update application
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## Production Checklist

Before going live:

- [ ] SSL certificate installed and tested
- [ ] Firewall configured
- [ ] Database backups automated
- [ ] Monitoring/alerting configured
- [ ] Load testing completed
- [ ] Health checks working
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Admin password changed
- [ ] Environment variables secured
- [ ] Rollback plan tested
- [ ] Documentation complete

**You're ready for production! 🚀**
