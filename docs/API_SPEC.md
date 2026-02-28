# API Specification - Team B Vision System

This document specifies the REST API interface between Team B (Vision & Sensing) and Team A (PPO Agent).

## Base URL

- **Local**: `http://localhost:8000`
- **RunPod**: `https://[your-pod-id]-8000.proxy.runpod.net`

## Interactive Documentation

- **Swagger UI**: `{BASE_URL}/docs`
- **ReDoc**: `{BASE_URL}/redoc`

---

## Core Endpoints (RL Interface)

### 1. GET `/observation`

**Purpose**: Get current observation (vehicle counts per lane)

**Response**: `ObservationResponse`
```json
{
  "observation": [0.15, 0.25, 0.10, 0.20, 0.05, 0.0, 0.15, 0.10],
  "frame_id": 1523,
  "timestamp": 1234567890.123,
  "num_lanes": 8,
  "raw_counts": [3, 5, 2, 4, 1, 0, 3, 2]
}
```

**Fields**:
- `observation`: Normalized vehicle counts [0, 1] per lane (THIS IS YOUR RL STATE)
- `frame_id`: Sequential frame number
- `timestamp`: Unix timestamp
- `num_lanes`: Number of lanes in intersection
- `raw_counts`: Actual vehicle counts (non-normalized)

**Usage Example (Python)**:
```python
import requests

response = requests.get("http://localhost:8000/observation")
obs = response.json()

state = obs["observation"]  # Use this as input to your PPO network
```

---

### 2. POST `/action`

**Purpose**: Set traffic light action (called by PPO agent)

**Request**: `ActionRequest`
```json
{
  "action": 2,
  "duration": 25.0
}
```

**Fields**:
- `action`: Traffic phase ID (0 to num_phases-1)
- `duration`: Optional duration in seconds (defaults to config)

**Response**:
```json
{
  "status": "success",
  "phase_set": 2,
  "phase_name": "East_West_Straight",
  "duration": 25.0
}
```

**Usage Example (Python)**:
```python
import requests

action = {"action": 2, "duration": 30.0}
response = requests.post("http://localhost:8000/action", json=action)
print(response.json())
```

---

## Monitoring Endpoints

### 3. GET `/state`

**Purpose**: Get complete intersection state

**Response**: `StateResponse`
```json
{
  "vehicle_counts": [3, 5, 2, 4, 1, 0, 3, 2],
  "current_phase": 2,
  "phase_elapsed_time": 12.5,
  "phase_duration": 30.0,
  "step_count": 1523,
  "total_vehicles": 20,
  "episode_runtime": 1834.2
}
```

---

### 4. GET `/health`

**Purpose**: Check system health

**Response**: `HealthResponse`
```json
{
  "status": "healthy",
  "carla_connected": true,
  "yolo_loaded": true,
  "num_lanes": 8,
  "num_phases": 5,
  "uptime": 3600.5
}
```

---

### 5. GET `/config`

**Purpose**: Get intersection configuration

**Response**: `ConfigResponse`
```json
{
  "num_lanes": 8,
  "num_phases": 5,
  "observation_shape": [8],
  "action_space_size": 5,
  "lanes": [...],
  "phases": [...]
}
```

---

### 6. GET `/metrics`

**Purpose**: Get performance metrics

**Response**: `MetricsResponse`
```json
{
  "total_vehicles_served": 523,
  "total_waiting_time": 1234.5,
  "average_waiting_time": 2.36,
  "steps": 1523,
  "runtime": 1834.2
}
```

---

### 7. POST `/reset`

**Purpose**: Reset episode (for training)

**Response**:
```json
{
  "status": "success",
  "message": "Episode reset"
}
```

---

### 8. GET `/camera/stream`

**Purpose**: Live camera stream with detections and ROIs (for debugging)

**Response**: MJPEG stream

**Usage**: Open in browser or video player:
```
http://localhost:8000/camera/stream
```

---

## RL Training Loop Example (Team A)

```python
import requests
import numpy as np
from stable_baselines3 import PPO

BASE_URL = "http://localhost:8000"

# Initialize your PPO model
model = PPO("MlpPolicy", ...)

# Training loop
for episode in range(1000):
    # Reset episode
    requests.post(f"{BASE_URL}/reset")
    
    done = False
    episode_reward = 0
    
    while not done:
        # Get observation from Team B's system
        obs_response = requests.get(f"{BASE_URL}/observation").json()
        state = np.array(obs_response["observation"])
        
        # Your PPO decides action
        action, _ = model.predict(state)
        
        # Send action to Team B's system
        action_request = {"action": int(action)}
        requests.post(f"{BASE_URL}/action", json=action_request)
        
        # Calculate reward (your responsibility, Team A)
        reward = calculate_reward(obs_response)
        
        # Train your model
        # ... (your PPO training code)
        
        episode_reward += reward
        
        # Check if episode should end
        if episode_steps > MAX_STEPS:
            done = True
    
    print(f"Episode {episode}: Reward = {episode_reward}")
```

---

## Error Responses

All endpoints may return:

**503 Service Unavailable**:
```json
{
  "detail": "System not initialized"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Error message here"
}
```

**400 Bad Request**:
```json
{
  "detail": "Invalid action 10, must be 0-4"
}
```

---

## Rate Limits

- No rate limits currently
- Recommended: Max 20 requests/second for `/observation`

---

## Notes for Team A

1. **Observation Vector**: Always use the `observation` field (normalized) as input to your PPO network
2. **Action Space**: Discrete space from 0 to `num_phases - 1`
3. **Reward Function**: YOU (Team A) calculate the reward based on observations
4. **Episode Length**: Decide your own episode length (typical: 500-2000 steps)
5. **Synchronization**: Each call to `/observation` advances CARLA by one tick

---

## Quick Start for Team A

1. Check health: `GET /health`
2. Get config: `GET /config` (to know observation/action spaces)
3. Start training loop:
   - Get observation: `GET /observation`
   - Decide action with PPO
   - Send action: `POST /action`
   - Calculate reward
   - Train model
   - Repeat

---

## Questions?

Contact Team B (that's me!) if you need:
- Different observation format
- Additional state features
- Changes to the interface
