# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies with verbose logging
RUN npm install --verbose || npm ci --verbose

# Copy all frontend source files
COPY frontend/ ./

# Build the application
RUN npm run build

# Verify the build output exists
RUN ls -la dist/ && test -f dist/index.html

# Final image
FROM python:3.11-slim

# Set environment variables
# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      curl \
      ca-certificates \
      netcat-openbsd \
      dos2unix \
      \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Copy the BUILT frontend from the build stage
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Copy and prepare entrypoint
COPY backend/docker-entrypoint.sh ./docker-entrypoint.sh
RUN dos2unix docker-entrypoint.sh && chmod +x docker-entrypoint.sh

# Create data directories
RUN mkdir -p /app/data /app/logs /app/output

# Set working directory for the backend
WORKDIR /app/backend

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
