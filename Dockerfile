# Stage 1: Build frontend
FROM node:20-alpine AS build-stage
WORKDIR /app/iptv-stream-manager-frontend
COPY frontend/package*.json ./
# Fix: Install ALL dependencies (including devDependencies) for build
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build
    
# Stage 2: Build the final Python application
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/ ./backend/

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build
COPY --from=build-stage /app/iptv-stream-manager-frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p /app/data /app/output /app/logs && \
    chmod -R 755 /app/data /app/output /app/logs

# Copy entrypoint
COPY backend/docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Expose ports
EXPOSE 8000 3000

# Set working directory to backend
WORKDIR /app/backend

ENTRYPOINT ["/app/docker-entrypoint.sh"]
