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

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/ ./backend/

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from build-stage
COPY --from=build-stage /app/iptv-stream-manager-frontend/dist /app/frontend/dist

# Copy entrypoint script
COPY backend/docker-entrypoint.sh /app/backend/
RUN chmod +x /app/backend/docker-entrypoint.sh

# Expose ports
EXPOSE 8000 3000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use entrypoint script
ENTRYPOINT ["/app/backend/docker-entrypoint.sh"]
