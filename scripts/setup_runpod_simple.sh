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

# Check if we need sudo
SUDO=""
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
    echo "Note: Using sudo for privileged operations"
fi

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    $SUDO apt-get update
    $SUDO apt-get install -y docker.io
    $SUDO systemctl start docker
    $SUDO systemctl enable docker
    $SUDO usermod -aG docker $USER
    echo "✓ Docker installed"
    echo "Note: You may need to log out and back in for docker group to take effect"
else
    echo "✓ Docker already installed"
fi

# Install NVIDIA Container Toolkit if needed
if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null 2>&1; then
    echo "Installing NVIDIA Container Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | $SUDO apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        $SUDO tee /etc/apt/sources.list.d/nvidia-docker.list > /dev/null
    $SUDO apt-get update
    $SUDO apt-get install -y nvidia-docker2
    $SUDO systemctl restart docker
    echo "✓ NVIDIA Container Toolkit installed"
else
    echo "✓ NVIDIA Container Toolkit already configured"
fi

# Test GPU
echo ""
echo "Testing GPU availability..."
nvidia-smi || echo "Warning: nvidia-smi not available"

# Build Docker image ON THE SERVER (not download)
echo ""
echo "================================================"
echo "   Building Docker image on server...         "
echo "   This will take 15-25 minutes               "
echo "   (downloading CARLA + packages)             "
echo "================================================"
echo ""

$SUDO docker build -t intelligent-traffic-teamb:latest -f docker/Dockerfile .

echo ""
echo "================================================"
echo "   Build Complete!                             "
echo "================================================"
echo ""
echo "Image built successfully!"
$SUDO docker images intelligent-traffic-teamb:latest
echo ""
echo "Next: Run the container"
echo "  $SUDO docker run -d --name carla-system --gpus all \\"
echo "    -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all \\"
echo "    --restart unless-stopped \\"
echo "    -p 2000:2000 -p 8000:8000 -p 6080:6080 \\"
echo "    intelligent-traffic-teamb:latest"
echo ""
