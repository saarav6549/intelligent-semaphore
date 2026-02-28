#!/bin/bash
# Setup script for RunPod - Run this inside your RunPod terminal

set -e

echo "================================================"
echo "   RunPod Setup Script - Team B                "
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt-get update
apt-get install -y wget curl git vim

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
else
    echo "✓ Docker already installed"
fi

# Install NVIDIA Container Toolkit if not present
if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "Installing NVIDIA Container Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update
    apt-get install -y nvidia-docker2
    systemctl restart docker
else
    echo "✓ NVIDIA Container Toolkit already configured"
fi

# Install Python dependencies (for scripts outside Docker)
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Test GPU
echo ""
echo "Testing GPU availability..."
nvidia-smi

# Build Docker image
echo ""
echo "Building Docker image (this will take 15-30 minutes)..."
docker build -t carla-vision-system:latest -f docker/Dockerfile .

echo ""
echo "================================================"
echo "   Setup Complete!                             "
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Run the container:"
echo "   docker run -d --name carla-system --gpus all -p 2000:2000 -p 8000:8000 -p 6080:6080 -v \$(pwd):/workspace carla-vision-system:latest"
echo ""
echo "2. Check logs:"
echo "   docker logs -f carla-system"
echo ""
echo "3. Access noVNC:"
echo "   https://[your-pod-id]-6080.proxy.runpod.net"
echo ""
echo "4. Access API:"
echo "   https://[your-pod-id]-8000.proxy.runpod.net/docs"
echo ""
