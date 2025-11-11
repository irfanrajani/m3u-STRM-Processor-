# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_WORKERS=1 \
    SQLALCHEMY_WARN_20=1

WORKDIR /app

# System deps + dos2unix to fix line-ending issues
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg curl ca-certificates netcat-openbsd dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

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
