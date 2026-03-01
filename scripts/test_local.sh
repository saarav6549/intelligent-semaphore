#!/bin/bash
# Test the Docker image locally before pushing to server

set -e

echo "================================================"
echo "   Testing CARLA Vision System Locally         "
echo "================================================"
echo ""

# Stop any existing container
if docker ps -a | grep -q carla-test; then
    echo "Stopping existing test container..."
    docker stop carla-test 2>/dev/null || true
    docker rm carla-test 2>/dev/null || true
fi

echo "Starting container in test mode..."
docker run -d \
    --name carla-test \
    --gpus all \
    -p 2000:2000 \
    -p 8000:8000 \
    -p 6080:6080 \
    intelligent-traffic-teamb:latest

echo ""
echo "Container started! Checking logs..."
echo ""
sleep 5
docker logs carla-test

echo ""
echo "================================================"
echo "   Container is running!                        "
echo "================================================"
echo ""
echo "Access URLs:"
echo "  - noVNC: http://localhost:6080"
echo "  - API: http://localhost:8000/docs"
echo "  - CARLA: localhost:2000"
echo ""
echo "Commands:"
echo "  View logs:    docker logs -f carla-test"
echo "  Stop test:    docker stop carla-test"
echo "  Remove test:  docker rm carla-test"
echo ""
echo "Press Ctrl+C when done testing..."
echo ""

# Follow logs
docker logs -f carla-test
