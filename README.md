# Intelligent Traffic Light System - Team B (Vision & Sensing)

## Project Overview
This is the **Vision & Sensing module** for an intelligent traffic light system that uses:
- **CARLA**: Realistic driving simulator for visualization
- **YOLO**: Vehicle detection from intersection cameras  
- **ROI Mapping**: Converting detections to lane-based vehicle counts
- **REST API**: Providing observations to Team A's PPO reinforcement learning agent

## Architecture

```
RunPod GPU Instance (Cloud)
├── CARLA Simulator (renders intersection)
├── YOLO Detector (detects vehicles)
├── ROI Mapper (counts vehicles per lane)
└── REST API (sends observations)
      ↓
Team A's PPO Agent (receives observations, returns actions)
```

## Project Structure

```
intelligent_semaphore/
├── docker/
│   ├── Dockerfile                    # Full CARLA + YOLO + VNC environment
│   ├── docker-compose.yml            # Optional local testing
│   └── entrypoint.sh                 # Container startup script
├── carla_integration/
│   ├── __init__.py
│   ├── carla_client.py               # Connect to CARLA server
│   ├── camera_setup.py               # Setup intersection cameras
│   ├── traffic_light_controller.py   # Control traffic light phases
│   └── scenario_loader.py            # Load traffic scenarios
├── yolo_detection/
│   ├── __init__.py
│   ├── train_yolo.py                 # Fine-tune YOLO on CARLA data
│   ├── detect_vehicles.py            # Real-time vehicle detection
│   ├── roi_mapping.py                # Map bounding boxes to lanes
│   └── dataset_generator.py          # Generate training data from CARLA
├── sensing_pipeline/
│   ├── __init__.py
│   ├── vehicle_counter.py            # Count vehicles per lane
│   ├── observation_builder.py        # Build observation vector for RL
│   └── state_manager.py              # Manage intersection state
├── api/
│   ├── __init__.py
│   ├── server.py                     # FastAPI REST server
│   └── schemas.py                    # API data models
├── tests/
│   ├── test_carla_connection.py
│   ├── test_yolo_detection.py
│   └── test_api.py
├── config/
│   ├── carla_config.yaml             # CARLA settings
│   ├── yolo_config.yaml              # YOLO model settings
│   └── intersection_config.yaml      # Intersection layout (ROIs, lanes)
├── scripts/
│   ├── run_local.sh                  # Run locally (if CARLA installed)
│   ├── setup_runpod.sh               # Setup RunPod instance
│   └── generate_dataset.py           # Collect CARLA images for YOLO training
├── docs/
│   ├── RUNPOD_SETUP.md               # Complete RunPod guide
│   ├── API_SPEC.md                   # API documentation for Team A
│   └── TROUBLESHOOTING.md            # Common issues
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick Start (RunPod)

### Step 1: Prepare Your Code
```bash
git init
git add .
git commit -m "Initial Team B setup"
```

### Step 2: Deploy to RunPod
See `docs/RUNPOD_SETUP.md` for detailed instructions.

### Step 3: Access the System
- **VNC/noVNC**: `https://[your-pod-id]-6080.proxy.runpod.net`
- **API Endpoint**: `https://[your-pod-id]-8000.proxy.runpod.net`

## The Interface Contract (with Team A)

### Observation (S): Vehicle counts per lane
```python
{
  "observation": [3, 5, 2, 4, 1, 0, 3, 2],  # 8 lanes example
  "timestamp": 1234567890.123,
  "frame_id": 1523
}
```

### Action (A): Traffic light phase
```python
{
  "action": 2,  # Integer representing traffic light phase
  "duration": 10.0  # Optional: how long to keep this phase
}
```

## Technologies Used

- **CARLA 0.9.15**: Autonomous driving simulator
- **YOLOv8/v10**: Real-time object detection (Ultralytics)
- **Python 3.10**: Main programming language
- **FastAPI**: REST API framework
- **OpenCV**: Image processing
- **Docker**: Containerization
- **TigerVNC + noVNC**: Remote visualization

## Development Workflow

1. **Local Development** (if you have CARLA installed locally)
2. **Cloud Deployment** (RunPod with GPU)
3. **Integration Testing** (Connect with Team A's PPO agent)
4. **Fine-tuning** (Optimize YOLO and ROI mappings)

## Next Steps

1. Read `docs/RUNPOD_SETUP.md` for complete RunPod deployment guide
2. Customize `config/intersection_config.yaml` for your specific intersection
3. Generate YOLO training dataset: `python scripts/generate_dataset.py`
4. Start the system: Container automatically runs all services
5. Test API: See `docs/API_SPEC.md`

## Team Coordination

- **Your responsibility**: Provide accurate vehicle counts per lane via API
- **Team A's responsibility**: Consume observations, train PPO, return actions
- **Interface**: REST API (see `docs/API_SPEC.md`)

## Support

For issues and troubleshooting, see `docs/TROUBLESHOOTING.md`.
