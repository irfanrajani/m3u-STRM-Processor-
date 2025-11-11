# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim

# Environment variables (can be overridden by docker-compose)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=1 \
    SQLALCHEMY_WARN_20=1 \
    POSTGRES_USER=iptv_user \
    POSTGRES_PASSWORD=iptv_secure_pass_change_me \
    POSTGRES_DB=iptv_db \
    POSTGRES_HOST=db \
    POSTGRES_PORT=5432

WORKDIR /app

# System deps + dos2unix to fix line-ending issues
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg curl ca-certificates netcat-openbsd dos2unix nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Add this BEFORE copying backend code to bust cache
ARG CACHEBUST=1

# Copy backend code
COPY backend/ /app/backend/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Copy and fix entrypoint script
COPY backend/docker-entrypoint.sh ./docker-entrypoint.sh
RUN dos2unix docker-entrypoint.sh && chmod +x docker-entrypoint.sh

# Create runtime directories
RUN mkdir -p /app/data /app/logs /app/output

EXPOSE 8000 3001

WORKDIR /app/backend
ENTRYPOINT ["/app/docker-entrypoint.sh"]
