# Stage 1: Build the React frontend
FROM node:20-alpine AS build-stage
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-*.json ./
RUN npm ci --only=production || npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the final Python application
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (ffmpeg for stream analysis)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./backend/app ./app
COPY ./backend/alembic ./alembic
COPY ./backend/alembic.ini ./alembic.ini

# Copy built frontend from the build stage
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# Create directories
RUN mkdir -p /app/output /app/logs

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
