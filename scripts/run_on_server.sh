#!/bin/bash
# Run on RunPod server after pushing image to Docker Hub
# Usage: bash scripts/run_on_server.sh <your-dockerhub-username>

set -e

DOCKER_USERNAME=${1:-}

if [ -z "$DOCKER_USERNAME" ]; then
    echo "Usage: bash scripts/run_on_server.sh <your-dockerhub-username>"
    exit 1
fi

IMAGE_NAME="${DOCKER_USERNAME}/intelligent-traffic-teamb:latest"

echo "================================================"
echo "   Running CARLA System on RunPod              "
echo "================================================"
echo ""
echo "Pulling image: $IMAGE_NAME"
echo "This will take 5-10 minutes..."
echo ""

# Pull the image
docker pull $IMAGE_NAME

# Stop existing container if any
if docker ps -a | grep -q carla-system; then
    echo "Stopping existing container..."
    docker stop carla-system 2>/dev/null || true
    docker rm carla-system 2>/dev/null || true
fi

# Run the container
echo ""
echo "Starting container..."
docker run -d \
    --name carla-system \
    --gpus all \
    --restart unless-stopped \
    -p 2000:2000 \
    -p 8000:8000 \
    -p 6080:6080 \
    $IMAGE_NAME

echo ""
echo "Waiting for services to start (40 seconds)..."
sleep 40

echo ""
echo "Checking logs..."
docker logs carla-system

echo ""
echo "================================================"
echo "   ✅ System is Running!                        "
echo "================================================"
echo ""
echo "Get your Pod ID from RunPod dashboard, then access:"
echo ""
echo "  noVNC:  https://[pod-id]-6080.proxy.runpod.net"
echo "  API:    https://[pod-id]-8000.proxy.runpod.net/docs"
echo ""
echo "Commands:"
echo "  View logs:    docker logs -f carla-system"
echo "  Restart:      docker restart carla-system"
echo "  Stop:         docker stop carla-system"
echo ""
echo "🎉 Give the API URL to Team A!"
echo ""
