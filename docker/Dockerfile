# Dockerfile for CARLA + YOLO + VNC on RunPod
# This container runs CARLA simulator with GPU, YOLO detection, and VNC for remote viewing

FROM carlasim/carla:0.9.15

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
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
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN pip3 install --upgrade pip setuptools wheel

# Copy requirements and install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Install additional tools
RUN pip3 install loguru

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

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV DISPLAY=:99
ENV CARLA_ROOT=/home/carla
ENV PYTHONPATH="${PYTHONPATH}:/home/carla/PythonAPI/carla/dist/carla-0.9.15-py3.7-linux-x86_64.egg"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["all"]
