#!/bin/bash
# Script to safely stop all services on RunPod

echo "Stopping services..."

# Stop container
if docker ps | grep -q carla-system; then
    echo "Stopping carla-system container..."
    docker stop carla-system
    echo "✓ Container stopped"
else
    echo "Container not running"
fi

echo ""
echo "Services stopped. You can now Stop the Pod in RunPod dashboard."
echo ""
echo "To resume later:"
echo "  1. Start the Pod in RunPod dashboard"
echo "  2. Run: docker start carla-system"
echo "  3. Check logs: docker logs -f carla-system"
