#!/bin/bash
# Push Docker image to Docker Hub
# Run this after build_local.sh succeeds

set -e

echo "================================================"
echo "   Push Image to Docker Hub                    "
echo "================================================"
echo ""

# Get Docker Hub username
read -p "Enter your Docker Hub username: " DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Username required!"
    exit 1
fi

# Tag the image
IMAGE_NAME="${DOCKER_USERNAME}/intelligent-traffic-teamb:latest"
echo ""
echo "Tagging image as: $IMAGE_NAME"
docker tag intelligent-traffic-teamb:latest $IMAGE_NAME

# Login to Docker Hub
echo ""
echo "Logging in to Docker Hub..."
docker login

# Push the image
echo ""
echo "Pushing image (this will take 5-15 minutes)..."
docker push $IMAGE_NAME

echo ""
echo "================================================"
echo "   ✅ Push Complete!                            "
echo "================================================"
echo ""
echo "Your image is now available at:"
echo "  docker pull $IMAGE_NAME"
echo ""
echo "Save this for RunPod:"
echo "  IMAGE=$IMAGE_NAME"
echo ""
echo "Next: Run on RunPod server:"
echo "  bash scripts/run_on_server.sh $DOCKER_USERNAME"
echo ""
