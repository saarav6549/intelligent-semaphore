# 🚦 Intelligent Traffic Light - Team B

> **CARLA Vision System** for Reinforcement Learning Traffic Control

Complete system for running CARLA simulator with YOLO vehicle detection on GPU, providing a REST API for PPO agents.

---

## 🎯 Start Here

### New to this project?
👉 **Read:** [`🎯_קרא_אותי_ראשון.md`](🎯_קרא_אותי_ראשון.md)

### Ready to deploy?
👉 **Follow:** [`SIMPLE_DEPLOY.md`](SIMPLE_DEPLOY.md) - Deploy in 3 steps (~28 minutes)

---

## 📚 Documentation

| Document | Description | When to Read |
|----------|-------------|--------------|
| **🎯_קרא_אותי_ראשון.md** | Overview & quick start | Start here! |
| **SIMPLE_DEPLOY.md** | Deploy to RunPod (recommended) | Ready to deploy |
| **BUILD_AND_DEPLOY.md** | Build locally & push | Alternative approach |
| **GET_STARTED.md** | Quick reference commands | Need a reminder |
| **PROJECT_SUMMARY.md** | Complete file overview | Want to understand structure |
| **ARCHITECTURE.md** | System architecture | Deep dive into design |
| **TEAM_A_INTEGRATION.md** | API guide for Team A | Integrating with RL agent |

---

## ⚡ Quick Start

```bash
# 1. Clone & Push to GitHub
git clone <this-repo>
cd intelligent-semaphore
git remote add origin https://github.com/[YOU]/intelligent-semaphore.git
git push -u origin main

# 2. Deploy on RunPod
# - Go to runpod.io
# - Deploy RTX 3090, expose ports: 2000, 8000, 6080

# 3. Build on server
git clone https://github.com/[YOU]/intelligent-semaphore.git
cd intelligent-semaphore
bash scripts/setup_runpod_simple.sh

# 4. Run
docker run -d --name carla-system --gpus all --restart unless-stopped \
  -p 2000:2000 -p 8000:8000 -p 6080:6080 \
  intelligent-traffic-teamb:latest
```

**Access:**
- noVNC: `https://[pod-id]-6080.proxy.runpod.net`
- API: `https://[pod-id]-8000.proxy.runpod.net/docs`

---

## 🏗️ What's Inside

```
intelligent-semaphore/
├── 📂 carla_integration/     # CARLA client & camera management
├── 📂 yolo_detection/        # Vehicle detection with YOLO
├── 📂 sensing_pipeline/      # ROI mapping & observation builder
├── 📂 api/                   # REST API for RL agents
├── 📂 config/                # Configuration files
├── 📂 docker/                # Dockerfile & entrypoint
├── 📂 scripts/               # Setup & utility scripts
├── 📂 docs/                  # Detailed documentation
└── 📂 tests/                 # Test files
```

---

## 🔧 System Requirements

### For Deployment (RunPod):
- GPU: RTX 3090 or better
- RAM: 16GB+
- Storage: 60GB+
- OS: Ubuntu 18.04+ (handled by Docker)

### For Local Development (optional):
- Docker Desktop
- 30GB free disk space
- Internet connection

---

## 🚀 Features

- ✅ **CARLA 0.9.15** - High-fidelity traffic simulation
- ✅ **YOLOv8** - Real-time vehicle detection
- ✅ **ROI Mapping** - Lane-based vehicle counting
- ✅ **REST API** - Easy integration with RL agents
- ✅ **VNC Access** - Remote visualization
- ✅ **GPU Accelerated** - Fast inference
- ✅ **Docker** - One-command deployment

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Reset environment |
| `/step` | POST | Execute action, get observation |
| `/health` | GET | System health check |
| `/camera/stream` | GET | Live camera feed |
| `/docs` | GET | Interactive API documentation |

**Full API docs:** [`docs/API_SPEC.md`](docs/API_SPEC.md)

---

## 🤝 For Team A (RL Agent)

Your PPO agent can connect to this system via the REST API.

**Read:** [`TEAM_A_INTEGRATION.md`](TEAM_A_INTEGRATION.md)

**Quick example:**
```python
import requests

API_URL = "https://your-pod-8000.proxy.runpod.net"

# Reset environment
response = requests.post(f"{API_URL}/reset")
observation = response.json()

# Execute action
action = {"phase": 0, "duration": 30}
response = requests.post(f"{API_URL}/step", json=action)
next_obs, reward, done, info = response.json()
```

---

## 💰 Cost Estimate

| Component | Cost |
|-----------|------|
| Setup (1 time) | ~$0.11 |
| Running (per hour) | $0.34 |
| 10 hours of training | $3.51 |

**Tip:** Stop the pod when not in use!

---

## 🐛 Troubleshooting

**Common issues:**

1. **Container not starting**
   ```bash
   docker logs carla-system
   ```

2. **GPU not detected**
   ```bash
   docker exec carla-system nvidia-smi
   ```

3. **Port already in use**
   ```bash
   netstat -tlnp | grep 2000
   ```

**Full troubleshooting guide:** [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

---

## 📝 License

This project is part of an academic research project on intelligent traffic control.

---

## 🙏 Acknowledgments

- **CARLA Simulator** - https://carla.org
- **Ultralytics YOLO** - https://ultralytics.com
- **FastAPI** - https://fastapi.tiangolo.com
- **RunPod** - https://runpod.io

---

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the team.

---

**Ready to start? → [`SIMPLE_DEPLOY.md`](SIMPLE_DEPLOY.md)** 🚀
