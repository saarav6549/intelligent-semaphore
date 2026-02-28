#!/bin/bash
# Start all services (CARLA + VNC + API)

echo "=========================================="
echo "  Starting All Services"
echo "=========================================="

# Setup environment
export DISPLAY=:99
export PYTHONPATH=$PYTHONPATH:/workspace/CARLA_0.9.15/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg

# Start virtual display
echo "[1/4] Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Start window manager
echo "[2/4] Starting window manager..."
fluxbox &
sleep 1

# Start VNC
echo "[3/4] Starting VNC server..."
x11vnc -display :99 -forever -shared -rfbport 5900 -rfbauth ~/.vnc/passwd &
sleep 2

# Start noVNC
echo "[4/4] Starting noVNC..."
websockify -D --web=/usr/share/novnc/ 6080 localhost:5900

echo ""
echo "=========================================="
echo "  VNC Services Started!"
echo "=========================================="
echo ""
echo "Access noVNC: https://[your-pod-id]-6080.proxy.runpod.net"
echo ""
echo "Now starting CARLA..."
echo "This will take 30-60 seconds..."
echo ""

# Start CARLA
cd /workspace/CARLA_0.9.15
./CarlaUE4.sh -RenderOffScreen -carla-rpc-port=2000 &
CARLA_PID=$!

echo "CARLA starting with PID: $CARLA_PID"
echo "Waiting 45 seconds for CARLA to initialize..."
sleep 45

# Test CARLA connection
echo ""
echo "Testing CARLA connection..."
python3 << EOF
import sys
sys.path.append('/workspace/CARLA_0.9.15/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg')
import carla
try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    version = client.get_server_version()
    print(f'✓ CARLA {version} is ready!')
except:
    print('✗ CARLA not ready yet, wait a bit more...')
EOF

echo ""
echo "Starting API server..."
cd /workspace/intelligent-semaphore
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo ""
echo "=========================================="
echo "  All Services Running!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - CARLA:   localhost:2000 (PID: $CARLA_PID)"
echo "  - API:     http://localhost:8000 (PID: $API_PID)"
echo "  - VNC:     vnc://localhost:5900"
echo "  - noVNC:   https://[pod-id]-6080.proxy.runpod.net"
echo ""
echo "API Documentation:"
echo "  https://[pod-id]-8000.proxy.runpod.net/docs"
echo ""
echo "Camera Stream:"
echo "  https://[pod-id]-8000.proxy.runpod.net/camera/stream"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="

# Keep script running
wait
