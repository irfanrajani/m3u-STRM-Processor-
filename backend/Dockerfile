```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/output /app/logs && \
    chmod -R 755 /app/data /app/output /app/logs

# Copy the entrypoint script into the container at /app
COPY ./entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the entrypoint to the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
```