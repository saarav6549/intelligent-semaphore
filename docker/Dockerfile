# Dockerfile for CARLA + YOLO + VNC on RunPod
# This container runs CARLA simulator with GPU, YOLO detection, and VNC for remote viewing

FROM carlasim/carla:0.9.15

USER root

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

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
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.8 (CARLA comes with 3.7, but we need newer for packages)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-distutils python3.8-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.8
RUN curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8

# Copy requirements and install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN python3.8 -m pip install -r /tmp/requirements.txt

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

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV DISPLAY=:99
ENV CARLA_ROOT=/home/carla
ENV PYTHONPATH=/home/carla/PythonAPI/carla:/workspace

ENTRYPOINT ["/entrypoint.sh"]
CMD ["all"]
