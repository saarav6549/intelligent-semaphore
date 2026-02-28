# Quick Reference - Team B System

## URLs (Replace [pod-id] with your actual RunPod ID)

| Service | URL | Purpose |
|---------|-----|---------|
| API | `https://[pod-id]-8000.proxy.runpod.net` | REST API |
| API Docs | `https://[pod-id]-8000.proxy.runpod.net/docs` | Interactive docs |
| Camera Stream | `https://[pod-id]-8000.proxy.runpod.net/camera/stream` | Live camera |
| noVNC | `https://[pod-id]-6080.proxy.runpod.net` | CARLA visualization |

---

## Essential Commands

### RunPod Pod Management

```bash
# View running containers
docker ps

# View logs
docker logs -f carla-system

# Restart container
docker restart carla-system

# Stop container
docker stop carla-system

# Enter container
docker exec -it carla-system bash

# Check GPU
nvidia-smi
```

### Git Workflow

```powershell
# On Windows (your machine)
git add .
git commit -m "Update"
git push

# On RunPod
cd /workspace/intelligent_semaphore
git pull
docker restart carla-system
```

---

## API Quick Test

```bash
# Health check
curl https://[pod-id]-8000.proxy.runpod.net/health

# Get observation
curl https://[pod-id]-8000.proxy.runpod.net/observation

# Send action
curl -X POST https://[pod-id]-8000.proxy.runpod.net/action \
  -H "Content-Type: application/json" \
  -d '{"action": 2}'
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `config/carla_config.yaml` | CARLA settings (FPS, weather, vehicles) |
| `config/yolo_config.yaml` | YOLO model and detection settings |
| `config/intersection_config.yaml` | Lane layout and ROI zones |

### Quick Tweaks

**Speed up simulation** (lower quality):
```yaml
# config/carla_config.yaml
fixed_delta_seconds: 0.1  # 10 FPS
no_rendering_mode: true
```

**Reduce GPU memory**:
```yaml
# config/intersection_config.yaml
resolution:
  width: 1280
  height: 720

# config/yolo_config.yaml
model_version: "yolov8n"  # smallest model
```

**More vehicles**:
```yaml
# config/carla_config.yaml
traffic:
  num_vehicles: 100
```

---

## File Structure (Most Important)

```
intelligent_semaphore/
├── config/                   # ← Edit these to customize
│   ├── carla_config.yaml
│   ├── yolo_config.yaml
│   └── intersection_config.yaml
│
├── api/server.py             # ← The API that Team A uses
│
├── carla_integration/        # ← CARLA connection code
├── yolo_detection/           # ← Vehicle detection code
├── sensing_pipeline/         # ← Observation building
│
├── docs/
│   ├── RUNPOD_SETUP.md      # ← How to deploy
│   ├── API_SPEC.md          # ← API documentation
│   └── TROUBLESHOOTING.md   # ← When things break
│
└── scripts/
    ├── test_system.py        # ← Run this to test everything
    └── quick_start.py        # ← Quick demo
```

---

## Troubleshooting (Quick)

| Problem | Solution |
|---------|----------|
| API returns 503 | Wait 30s, CARLA is starting |
| No vehicles detected | Check camera stream, adjust ROIs |
| Out of GPU memory | Use smaller model or lower resolution |
| Cannot connect to CARLA | Check logs: `docker logs carla-system` |
| noVNC shows black screen | Wait 60s or restart VNC |

See `docs/TROUBLESHOOTING.md` for detailed solutions.

---

## Cost Management

### RunPod Pricing (approximate)

- **RTX 3090**: $0.34/hour (~$8.16/day if running 24/7)
- **RTX 4090**: $0.44/hour
- **Storage**: $0.10/GB/month

### Tips to Save Money

1. **Stop when not using**: Stop pod = stop billing
2. **Use Spot instances**: 50-70% cheaper (but can be interrupted)
3. **Disable rendering**: `no_rendering_mode: true` (faster + cheaper GPU)
4. **Local SUMO**: Train PPO on SUMO (CPU), validate on CARLA (GPU)

---

## For Team A: Integration Checklist

- [ ] Got API URL from Team B
- [ ] Health check passes: `GET /health`
- [ ] Can get observations: `GET /observation`
- [ ] Can send actions: `POST /action`
- [ ] Understand observation format (8 floats, 0-1 range)
- [ ] Understand action format (integer 0-4)
- [ ] Implemented reward function
- [ ] Created Gym environment wrapper
- [ ] PPO model configured
- [ ] Training loop ready

---

## Contact Info

**Team B Lead**: [Your contact]  
**GitHub**: [Repository URL]  
**Documentation**: See `docs/` folder

---

## Useful Links

- **CARLA Docs**: https://carla.readthedocs.io/
- **YOLO Docs**: https://docs.ultralytics.com/
- **Stable Baselines3**: https://stable-baselines3.readthedocs.io/
- **RunPod Docs**: https://docs.runpod.io/
