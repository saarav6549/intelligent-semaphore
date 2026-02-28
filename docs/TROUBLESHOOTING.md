# Troubleshooting Guide

## Common Issues and Solutions

### CARLA Issues

#### Issue: "RuntimeError: time-out of 10000ms while waiting for the simulator"

**Cause**: CARLA server not running or not ready

**Solutions**:
1. Check if CARLA is running:
   ```bash
   docker logs carla-system | grep "CARLA"
   ps aux | grep CarlaUE4
   ```

2. Wait longer - CARLA takes 30-60 seconds to start

3. Restart container:
   ```bash
   docker restart carla-system
   ```

4. Check GPU availability:
   ```bash
   nvidia-smi
   ```

---

#### Issue: CARLA runs but shows black screen in noVNC

**Cause**: Display or rendering issue

**Solutions**:
1. Check if Xvfb is running:
   ```bash
   docker exec carla-system ps aux | grep Xvfb
   ```

2. Restart VNC:
   ```bash
   docker exec carla-system pkill x11vnc
   docker exec carla-system x11vnc -display :99 -forever -shared -rfbport 5900 -rfbauth ~/.vnc/passwd &
   ```

3. Try with rendering disabled (faster anyway):
   Edit `config/carla_config.yaml`:
   ```yaml
   no_rendering_mode: true
   ```

---

### YOLO Issues

#### Issue: "CUDA out of memory"

**Cause**: GPU memory exhausted

**Solutions**:
1. Use smaller YOLO model:
   ```yaml
   # In config/yolo_config.yaml
   model_version: "yolov8n"  # smallest
   ```

2. Reduce image resolution:
   ```yaml
   # In config/intersection_config.yaml
   resolution:
     width: 1280
     height: 720
   ```

3. Enable half precision:
   ```yaml
   # In config/yolo_config.yaml
   half_precision: true
   ```

4. Use CPU for YOLO (slower but works):
   ```yaml
   device: "cpu"
   ```

---

#### Issue: YOLO not detecting any vehicles

**Cause**: Wrong classes or low confidence threshold

**Solutions**:
1. Lower confidence threshold:
   ```yaml
   confidence_threshold: 0.3  # default is 0.5
   ```

2. Check if vehicles are in frame:
   - View camera stream: `http://[API_URL]/camera/stream`

3. Verify YOLO is loaded:
   ```bash
   curl http://[API_URL]/health
   ```

---

### ROI Mapping Issues

#### Issue: All lanes show 0 vehicles even though vehicles are visible

**Cause**: ROI coordinates don't match camera view

**Solutions**:
1. Visualize ROIs:
   - Open: `http://[API_URL]/camera/stream`
   - You should see colored polygons on lanes

2. Adjust ROI coordinates in `config/intersection_config.yaml`

3. Use helper script to find correct ROIs:
   ```python
   # TODO: Create ROI calibration tool
   ```

---

### API Issues

#### Issue: "503 Service Unavailable - System not initialized"

**Cause**: API started but background services failed

**Solutions**:
1. Check logs:
   ```bash
   docker logs carla-system | grep ERROR
   ```

2. Check health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

3. Common causes:
   - CARLA not connected: Wait 30s more
   - YOLO weights missing: Will auto-download first time
   - Config file error: Check YAML syntax

---

#### Issue: API is very slow (>5 seconds per request)

**Cause**: YOLO or CARLA bottleneck

**Solutions**:
1. Use smaller YOLO model (yolov8n)
2. Reduce camera resolution
3. Check GPU usage:
   ```bash
   nvidia-smi -l 1
   ```
4. Increase CARLA time step (lower FPS)

---

### Docker Issues

#### Issue: "docker: Error response from daemon: could not select device driver"

**Cause**: NVIDIA Docker runtime not installed

**Solutions**:
1. Install NVIDIA Container Toolkit:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
   apt-get update
   apt-get install -y nvidia-docker2
   systemctl restart docker
   ```

2. On RunPod: Should be pre-installed, contact support if not

---

#### Issue: "Port is already allocated"

**Cause**: Another container using the same port

**Solutions**:
1. Find what's using the port:
   ```bash
   docker ps
   netstat -tulpn | grep [PORT]
   ```

2. Stop the other container:
   ```bash
   docker stop [container-name]
   ```

3. Or use different ports:
   ```bash
   docker run -p 8001:8000 ...  # Use 8001 instead of 8000
   ```

---

### Network Issues

#### Issue: Cannot access API from Team A's machine

**Cause**: Firewall or incorrect URL

**Solutions**:
1. On RunPod: Use the proxy URL
   ```
   https://[pod-id]-8000.proxy.runpod.net
   ```
   NOT: `http://[pod-ip]:8000`

2. Check if port is exposed:
   - RunPod Dashboard > Your Pod > TCP Port Mappings

3. Test locally first:
   ```bash
   docker exec carla-system curl http://localhost:8000/health
   ```

---

### Performance Issues

#### Issue: System is laggy / low FPS

**Solutions**:
1. **Disable rendering** (if you don't need to see it):
   ```yaml
   # config/carla_config.yaml
   no_rendering_mode: true
   ```

2. **Reduce simulation fidelity**:
   ```yaml
   fixed_delta_seconds: 0.1  # 10 FPS instead of 20
   ```

3. **Fewer vehicles**:
   ```yaml
   traffic:
     num_vehicles: 20  # instead of 50
   ```

4. **Use faster YOLO**:
   ```yaml
   model_version: "yolov8n"
   ```

---

## Debugging Tools

### Check what's running

```bash
# Inside container
docker exec -it carla-system bash

# Check processes
ps aux | grep -E "Carla|python|x11vnc"

# Check ports
netstat -tulpn
```

### Monitor GPU

```bash
# GPU usage
nvidia-smi -l 1

# Detailed GPU info
nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv -l 1
```

### Test individual components

```bash
# Test CARLA connection
python3 -c "import carla; c = carla.Client('localhost', 2000); c.set_timeout(10); print(c.get_server_version())"

# Test YOLO
python3 -c "from ultralytics import YOLO; m = YOLO('yolov8n.pt'); print('YOLO OK')"

# Test API
curl http://localhost:8000/health
```

### View logs in real-time

```bash
# All logs
docker logs -f carla-system

# Only errors
docker logs carla-system 2>&1 | grep -i error

# Last 100 lines
docker logs carla-system --tail 100
```

---

## Getting Help

1. **Check logs first**: 90% of issues are in the logs
2. **Test locally**: Try `docker-compose up` on your machine
3. **RunPod support**: If GPU/infrastructure issue
4. **Contact Team B lead**: For code/integration issues

---

## Performance Benchmarks

Expected performance on RTX 3090:

- CARLA: 20-30 FPS (synchronous mode)
- YOLO inference: 100-150 FPS (yolov8n), 50-80 FPS (yolov8s)
- End-to-end pipeline: 15-20 FPS
- API response time: 50-200ms per request

If you're not hitting these numbers, something is misconfigured.
