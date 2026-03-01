#!/bin/bash
# Build Docker image locally on Windows/Linux
# Run this ONCE on your local machine with good internet

set -e

echo "================================================"
echo "   Building CARLA Vision System Docker Image   "
echo "================================================"
echo ""
echo "⚠️  WARNING: This will download ~15GB base image!"
echo "    Make sure you have:"
echo "    - 30GB free disk space"
echo "    - Good internet connection"
echo "    - Docker Desktop running"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo ""
echo "Step 1/3: Pulling base image (carlasim/carla:0.9.15)..."
echo "         This will take 10-20 minutes..."
docker pull carlasim/carla:0.9.15

echo ""
echo "Step 2/3: Building our custom image..."
echo "         This will take 5-10 minutes..."
cd "$(dirname "$0")/.."
docker build -t intelligent-traffic-teamb:latest -f docker/Dockerfile .

echo ""
echo "Step 3/3: Verifying image..."
docker images | grep intelligent-traffic-teamb

echo ""
echo "================================================"
echo "   ✅ Build Complete!                           "
echo "================================================"
echo ""
echo "Image size:"
docker images intelligent-traffic-teamb:latest --format "{{.Size}}"
echo ""
echo "Next steps:"
echo "1. Test locally:"
echo "   bash scripts/test_local.sh"
echo ""
echo "2. Push to Docker Hub:"
echo "   bash scripts/push_image.sh"
echo ""
