#!/bin/bash
set -euo pipefail

echo "================================================"
echo "   Intelligent Traffic Light - Team B System   "
echo "================================================"

# Cleanup on exit
cleanup() {
  kill "${XVFB_PID:-}" "${VNC_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT

# Start Xvfb (virtual display)
echo "Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
XVFB_PID=$!
sleep 2

# Start window manager
echo "Starting window manager..."
fluxbox &
sleep 1

# Start VNC server
echo "Starting VNC server on port 5900..."
x11vnc -display :99 -forever -shared -rfbport 5900 -rfbauth ~/.vnc/passwd &
VNC_PID=$!
sleep 2

# Start noVNC (web VNC client)
echo "Starting noVNC on port 6080..."
websockify -D --web=/usr/share/novnc/ 6080 localhost:5900
sleep 2

echo "VNC services started!"
echo "  - VNC: port 5900 (password: 1234)"
echo "  - noVNC: port 6080 (web browser)"
echo ""

# Ensure logs directory exists and is writable for `carla`
mkdir -p /workspace/logs
chown -R carla:carla /workspace/logs 2>/dev/null || true

# Determine what to run
MODE=${1:-all}

CARLA_FLAGS=(
  -RenderOffScreen
  -carla-rpc-port=2000
  -nosound
  -stdout
  -FullStdOutLogOutput
  -log
)

# On some environments (notably Docker Desktop/WSL2), NVIDIA "graphics" driver
# libraries are not available inside containers. CARLA then exits instantly with
# Vulkan/GLX loader errors. We detect this and fail fast with a clear message.
if ! ldconfig -p 2>/dev/null | grep -q 'libGLX_nvidia.so.0'; then
  echo ""
  echo "WARNING: NVIDIA graphics libraries (libGLX_nvidia.so.0) not found in container."
  echo "CARLA requires Vulkan/OpenGL user-mode driver libs to start."
  echo ""
  echo "If you are running on Docker Desktop/WSL2 (Windows), GPU compute may work (nvidia-smi)"
  echo "but graphics libs often are not exposed to Linux containers."
  echo ""
  echo "Recommended: run this image on a Linux host with NVIDIA drivers (e.g., RunPod)."
  echo "If you still want to try locally, ensure you run with:"
  echo "  -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all"
  echo ""
fi

case $MODE in
  carla)
    echo "Starting CARLA server only..."
    cd /home/carla
    # CARLA refuses root; run as built-in `carla` user (preserve env like DISPLAY)
    su -p carla -s /bin/bash -c "cd /home/carla && ./CarlaUE4.sh ${CARLA_FLAGS[*]}" 2>&1 | tee -a /workspace/logs/carla.log
    ;;
    
  api)
    echo "Starting API server only..."
    cd /workspace
    python3.8 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
    ;;
    
  all)
    echo "Starting CARLA server..."
    cd /home/carla
    # Run CARLA as `carla` with headless-friendly flags; keep logs in docker logs + file
    (su -p carla -s /bin/bash -c "cd /home/carla && ./CarlaUE4.sh ${CARLA_FLAGS[*]}" 2>&1 | tee -a /workspace/logs/carla.log) &
    CARLA_PID=$!
    
    echo "Waiting for CARLA to start (30 seconds)..."
    sleep 30
    
    echo "Testing CARLA connection..."
    python3.8 -c "import carla; client = carla.Client('localhost', 2000); client.set_timeout(10.0); print(f'CARLA version: {client.get_server_version()}')" || echo "CARLA not ready yet, continuing..."
    
    echo "Starting API server..."
    cd /workspace
    python3.8 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    echo ""
    echo "================================================"
    echo "   All services started successfully!          "
    echo "================================================"
    echo "Services:"
    echo "  - CARLA: localhost:2000"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - VNC: vnc://localhost:5900 (password: 1234)"
    echo "  - noVNC: http://localhost:6080"
    echo ""
    echo "Access from outside (RunPod):"
    echo "  - API: https://[pod-id]-8000.proxy.runpod.net"
    echo "  - noVNC: https://[pod-id]-6080.proxy.runpod.net"
    echo "================================================"
    
    wait $CARLA_PID $API_PID
    ;;
    
  *)
    echo "Usage: $0 {carla|api|all}"
    exit 1
    ;;
esac
