#!/bin/bash
# Simple RunPod Setup Script - Run this in RunPod Web Terminal

echo "=========================================="
echo "  Team B Setup on RunPod (No Docker)"
echo "=========================================="

# Update system
echo ""
echo "[1/6] Updating system..."
apt-get update -qq

# Install system packages
echo "[2/6] Installing system packages..."
apt-get install -y wget curl git vim x11vnc xvfb fluxbox novnc websockify

# Install Python dependencies
echo "[3/6] Installing Python packages..."
cd /workspace/intelligent-semaphore
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Download CARLA
echo "[4/6] Downloading CARLA (this will take 5-10 minutes)..."
cd /workspace
if [ ! -d "CARLA_0.9.15" ]; then
    wget -q --show-progress https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.15.tar.gz
    echo "Extracting CARLA..."
    mkdir CARLA_0.9.15
    tar -xzf CARLA_0.9.15.tar.gz -C CARLA_0.9.15
    rm CARLA_0.9.15.tar.gz
else
    echo "CARLA already downloaded!"
fi

# Setup CARLA Python API
echo "[5/6] Setting up CARLA Python API..."
export PYTHONPATH=$PYTHONPATH:/workspace/CARLA_0.9.15/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg

# Setup VNC
echo "[6/6] Setting up VNC..."
mkdir -p ~/.vnc
x11vnc -storepasswd 1234 ~/.vnc/passwd

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "CARLA installed at: /workspace/CARLA_0.9.15"
echo ""
echo "Next steps:"
echo "  1. Run: bash start_services.sh"
echo "  2. Access noVNC: https://[pod-id]-6080.proxy.runpod.net"
echo "  3. Access API: https://[pod-id]-8000.proxy.runpod.net/docs"
echo ""
