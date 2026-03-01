#!/bin/bash
# Simple RunPod setup - Build on server directly
# Run this inside your RunPod terminal

set -e

echo "================================================"
echo "   RunPod Setup - Build on Server             "
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "docker/Dockerfile" ]; then
    echo "Error: Please run this script from the project root directory"
    echo "Expected: git clone your-repo && cd your-repo && bash scripts/setup_runpod_simple.sh"
    exit 1
fi

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
else
    echo "✓ Docker already installed"
fi

# Install NVIDIA Container Toolkit if needed
if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "Installing NVIDIA Container Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update
    apt-get install -y nvidia-docker2
    systemctl restart docker
else
    echo "✓ NVIDIA Container Toolkit already configured"
fi

# Test GPU
echo ""
echo "Testing GPU availability..."
nvidia-smi

# Build Docker image ON THE SERVER (not download)
echo ""
echo "================================================"
echo "   Building Docker image on server...         "
echo "   This will take 15-25 minutes               "
echo "   (downloading CARLA + packages)             "
echo "================================================"
echo ""

docker build -t intelligent-traffic-teamb:latest -f docker/Dockerfile .

echo ""
echo "================================================"
echo "   Build Complete!                             "
echo "================================================"
echo ""
echo "Image built successfully!"
docker images intelligent-traffic-teamb:latest
echo ""
echo "Next: Run the container"
echo "  docker run -d --name carla-system --gpus all --restart unless-stopped -p 2000:2000 -p 8000:8000 -p 6080:6080 intelligent-traffic-teamb:latest"
echo ""
