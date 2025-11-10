#!/bin/bash

# IPTV Stream Manager - Build Script for QNAP Deployment
# Run this on your Mac to build AMD64 images

set -e

echo "========================================"
echo "Building IPTV Stream Manager for QNAP"
echo "========================================"
echo ""

QNAP_IP="192.168.68.75"
QNAP_PATH="/share/CE_CACHEDEV1_DATA/Multimedia/RajaniServer"

echo "🏗️  Building backend image for AMD64..."
docker build --platform linux/amd64 -t iptv-backend:local -f docker/Dockerfile.backend ./backend
echo "✅ Backend built"
echo ""

echo "🏗️  Building frontend image for AMD64..."
docker build --platform linux/amd64 -t iptv-frontend:local -f docker/Dockerfile.frontend ./frontend
echo "✅ Frontend built"
echo ""

echo "💾 Saving backend image..."
docker save iptv-backend:local | gzip > iptv-backend.tar.gz
echo "✅ Backend saved ($(du -h iptv-backend.tar.gz | cut -f1))"
echo ""

echo "💾 Saving frontend image..."
docker save iptv-frontend:local | gzip > iptv-frontend.tar.gz
echo "✅ Frontend saved ($(du -h iptv-frontend.tar.gz | cut -f1))"
echo ""

echo "📤 Transferring to QNAP..."
scp iptv-backend.tar.gz iptv-frontend.tar.gz docker-compose.deploy.yml deploy-qnap.sh admin@${QNAP_IP}:${QNAP_PATH}/
echo "✅ Files transferred"
echo ""

echo "========================================"
echo "✅ Build Complete!"
echo "========================================"
echo ""
echo "📖 Next steps on QNAP:"
echo ""
echo "1. SSH into QNAP:"
echo "   ssh admin@${QNAP_IP}"
echo ""
echo "2. Navigate to directory:"
echo "   cd ${QNAP_PATH}"
echo ""
echo "3. Load images and deploy:"
echo "   docker load < iptv-backend.tar.gz"
echo "   docker load < iptv-frontend.tar.gz"
echo "   chmod +x deploy-qnap.sh"
echo "   ./deploy-qnap.sh"
echo ""
echo "Or run all at once:"
echo "   cd ${QNAP_PATH} && docker load < iptv-backend.tar.gz && docker load < iptv-frontend.tar.gz && chmod +x deploy-qnap.sh && ./deploy-qnap.sh"
echo ""
