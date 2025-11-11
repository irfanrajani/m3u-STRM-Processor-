#!/bin/bash
set -e

VERSION="${1:-local-$(date +%Y%m%d-%H%M%S)}"
IMAGE_NAME="iptv-stream-manager"

echo "🏗️  Building $IMAGE_NAME:$VERSION..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
npm run build
cd ..

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:latest .

# Create release artifacts
echo "📦 Creating release artifacts..."
mkdir -p release

# Save Docker image
docker save $IMAGE_NAME:$VERSION | gzip > release/$IMAGE_NAME-$VERSION-docker.tar.gz

# Create source archive
tar -czf release/$IMAGE_NAME-$VERSION-source.tar.gz \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.venv' \
  --exclude='release' \
  --exclude='dist' \
  --exclude='build' \
  .

# Package frontend
cd frontend/dist
tar -czf ../../release/$IMAGE_NAME-$VERSION-frontend.tar.gz .
cd ../..

# Generate checksums
cd release
sha256sum *.tar.gz > SHA256SUMS.txt
cd ..

echo "✅ Build complete!"
echo "📦 Artifacts in: ./release/"
echo "🐳 Docker image: $IMAGE_NAME:$VERSION"
echo ""
echo "To run:"
echo "  docker run -d -p 8000:8000 --name iptv-stream-manager $IMAGE_NAME:$VERSION"
