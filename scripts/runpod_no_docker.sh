#!/usr/bin/env bash
set -euo pipefail

echo "================================================"
echo " RunPod (no docker) - CARLA + API + noVNC setup "
echo "================================================"
echo ""

if [[ "$(id -u)" -ne 0 ]]; then
  echo "ERROR: Please run as root (RunPod pods usually are root)."
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Repo root: $REPO_ROOT"

echo ""
echo "Installing system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  wget curl git ca-certificates \
  x11vnc xvfb fluxbox \
  net-tools \
  novnc websockify \
  software-properties-common \
  xdg-user-dirs iproute2 \
  libvulkan1 vulkan-utils mesa-utils \
  dos2unix

echo ""
echo "Ensuring Python 3.8 + pip..."
if ! command -v python3.8 >/dev/null 2>&1; then
  add-apt-repository -y ppa:deadsnakes/ppa
  apt-get update
  apt-get install -y python3.8 python3.8-dev python3.8-distutils python3.8-venv
fi

if ! python3.8 -m pip --version >/dev/null 2>&1; then
  curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8
fi

python3.8 -m pip install --upgrade pip setuptools wheel

echo ""
echo "Installing Python requirements (retries + long timeouts)..."
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_DEFAULT_TIMEOUT=600
export PIP_PROGRESS_BAR=off
for i in 1 2 3 4 5; do
  echo "pip install attempt $i/5"
  if python3.8 -m pip install --retries 10 --timeout 600 --progress-bar off -r requirements.txt; then
    break
  fi
  if [[ "$i" -eq 5 ]]; then
    echo "ERROR: pip install failed after 5 attempts"
    exit 1
  fi
  echo "pip install failed; retrying in 30s..."
  sleep 30
done

echo ""
echo "Installing CARLA Python client for Python 3.8 (match simulator 0.9.15)..."
# Prefer the wheel shipped with the CARLA package when available to avoid mismatches/segfaults.
python3.8 -m pip uninstall -y carla >/dev/null 2>&1 || true

CARLA_DIST_DIR="/home/carla/PythonAPI/carla/dist"
CARLA_WHEEL=""
if [[ -d "$CARLA_DIST_DIR" ]]; then
  # Pick a cp38 wheel if present (e.g. carla-0.9.15-cp38-cp38-manylinux_2_27_x86_64.whl)
  CARLA_WHEEL="$(ls -1 "$CARLA_DIST_DIR"/carla-0.9.15-cp38-*.whl 2>/dev/null | head -n 1 || true)"
fi

if [[ -n "$CARLA_WHEEL" ]]; then
  echo "Using local CARLA wheel: $CARLA_WHEEL"
  python3.8 -m pip install "$CARLA_WHEEL"
else
  echo "Local cp38 wheel not found; trying PyPI carla==0.9.15"
  python3.8 -m pip install carla==0.9.15
fi

python3.8 -m pip install loguru

echo ""
echo "Preparing VNC/noVNC..."
mkdir -p /root/.vnc
x11vnc -storepasswd 1234 /root/.vnc/passwd

mkdir -p /workspace/logs 2>/dev/null || true

export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
fluxbox &
sleep 1
x11vnc -display :99 -forever -shared -rfbport 5900 -rfbauth /root/.vnc/passwd &
sleep 2
websockify -D --web=/usr/share/novnc/ 6080 localhost:5900

echo ""
echo "Starting CARLA (offscreen) and API..."
echo "- noVNC: :6080 (password 1234)"
echo "- API:   :8000"
echo ""

CARLA_FLAGS=(
  -RenderOffScreen
  -carla-rpc-port=2000
  -nosound
  -stdout
  -FullStdOutLogOutput
  -log
)

if [[ ! -x /home/carla/CarlaUE4.sh ]]; then
  echo "ERROR: /home/carla/CarlaUE4.sh not found."
  echo "This script expects the pod image to be based on CARLA (e.g. carlasim/carla:0.9.15)."
  exit 1
fi

set +e
(
  cd /home/carla
  # CARLA refuses root; run as the built-in 'carla' user if available
  if id carla >/dev/null 2>&1; then
    su -p carla -s /bin/bash -c "cd /home/carla && ./CarlaUE4.sh ${CARLA_FLAGS[*]}" 2>&1 | tee -a /workspace/logs/carla.log
  else
    ./CarlaUE4.sh "${CARLA_FLAGS[@]}" 2>&1 | tee -a /workspace/logs/carla.log
  fi
) &

sleep 5

cd "$REPO_ROOT"
python3.8 -m uvicorn api.server:app --host 0.0.0.0 --port 8000

