# Stage 1: Build the React frontend
FROM node:18-alpine AS build-stage
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ ./
RUN yarn build

# Stage 2: Build the final Python application
FROM python:3.9-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./api ./api

# Copy built frontend from the build stage
COPY --from=build-stage /app/frontend/dist ./frontend/dist

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
