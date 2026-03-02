# Dockerfile for CARLA + YOLO + VNC on RunPod
# This container runs CARLA simulator with GPU, YOLO detection, and VNC for remote viewing

FROM carlasim/carla:0.9.15

USER root

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=600
ENV PIP_PROGRESS_BAR=off

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    vim \
    sudo \
    x11vnc \
    xvfb \
    fluxbox \
    net-tools \
    novnc \
    websockify \
    software-properties-common \
    xdg-user-dirs \
    iproute2 \
    libvulkan1 \
    vulkan-utils \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.8 (CARLA comes with 3.7, but we need newer for packages)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-distutils python3.8-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.8
RUN curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8

# Upgrade pip tooling (helps with large wheels)
RUN python3.8 -m pip install --upgrade pip setuptools wheel

# Copy requirements and install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN set -e; \
    for i in 1 2 3 4 5; do \
      echo "pip install attempt $i/5"; \
      python3.8 -m pip install --retries 10 --timeout 600 --progress-bar off -r /tmp/requirements.txt && exit 0; \
      echo "pip install failed; retrying in 30s..." >&2; \
      sleep 30; \
    done; \
    echo "pip install failed after 5 attempts" >&2; \
    exit 1

# Install CARLA Python client for Python 3.8
RUN python3.8 -m pip install carla==0.9.13

# Install additional tools
RUN python3.8 -m pip install loguru

# Create workspace directory
WORKDIR /workspace

# Copy project files
COPY . /workspace/

# Create necessary directories
RUN mkdir -p /workspace/logs \
    /workspace/datasets \
    /workspace/runs \
    /workspace/models \
    /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Set up VNC
RUN mkdir -p ~/.vnc && \
    x11vnc -storepasswd 1234 ~/.vnc/passwd

# Expose ports
# 2000-2002: CARLA
# 8000: FastAPI
# 5900: VNC
# 6080: noVNC (Web VNC)
EXPOSE 2000 2001 2002 8000 5900 6080

# Copy entrypoint script and fix line endings
COPY docker/entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh 2>/dev/null || sed -i 's/\r$//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure workspace is writable by the built-in `carla` user (uid 1000 in base image)
RUN chown -R carla:carla /workspace && \
    mkdir -p /workspace/logs && \
    chown -R carla:carla /workspace/logs

# Set environment variables
ENV DISPLAY=:99
ENV CARLA_ROOT=/home/carla
ENV PYTHONPATH=/home/carla/PythonAPI/carla:/workspace

# NVIDIA Container Toolkit: we need graphics libs for Vulkan/OpenGL (CARLA offscreen rendering)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all

ENTRYPOINT ["/entrypoint.sh"]
CMD ["all"]
