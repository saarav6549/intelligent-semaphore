# Team A Integration Guide

## שלום חבר צוות A! 👋

זהו המדריך המלא לשימוש במערכת הזיהוי והחישה של Team B.

---

## TL;DR - מה אני צריך לדעת?

1. **API שלנו**: `https://[pod-id]-8000.proxy.runpod.net`
2. **Observation**: וקטור של 8 מספרים (ספירת רכבים לפי נתיב, מנורמל 0-1)
3. **Action**: מספר שלם 0-4 (פאזת רמזור)
4. **אתה אחראי על**: חישוב reward, אימון PPO, החלטה על episode length

---

## ה-Interface המלא

### Observation Space

```python
observation_space = spaces.Box(
    low=0.0,
    high=1.0,
    shape=(8,),
    dtype=np.float32
)
```

**משמעות**:
- 8 ערכים (lane 0 עד lane 7)
- כל ערך = מספר רכבים מנורמל (0 = ריק, 1 = מלא, בערך 20 רכבים)
- המערכת מחליקה (smoothing) על 3 frames למניעת רעש

### Action Space

```python
action_space = spaces.Discrete(5)
```

**פאזות**:
- 0: צפון-דרום ישר
- 1: צפון-דרום שמאלה
- 2: מזרח-מערב ישר
- 3: מזרח-מערב שמאלה
- 4: הכל אדום (למקרי חירום)

---

## דוגמת קוד - Training Loop

```python
import requests
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
import gymnasium as gym
from gymnasium import spaces


class TrafficLightEnv(gym.Env):
    """Gym environment wrapper for Team B's API"""
    
    def __init__(self, api_url: str):
        super().__init__()
        
        self.api_url = api_url
        
        # Get config from Team B
        config = requests.get(f"{api_url}/config").json()
        
        self.num_lanes = config['num_lanes']
        self.num_phases = config['num_phases']
        
        # Define spaces
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self.num_lanes,),
            dtype=np.float32
        )
        
        self.action_space = spaces.Discrete(self.num_phases)
        
        self.current_step = 0
        self.max_steps = 1000
    
    def reset(self, seed=None, options=None):
        """Reset environment"""
        super().reset(seed=seed)
        
        requests.post(f"{self.api_url}/reset")
        
        obs_response = requests.get(f"{self.api_url}/observation").json()
        observation = np.array(obs_response['observation'], dtype=np.float32)
        
        self.current_step = 0
        
        return observation, {}
    
    def step(self, action: int):
        """Take action and get next observation"""
        action_request = {"action": int(action), "duration": 10.0}
        requests.post(f"{self.api_url}/action", json=action_request)
        
        obs_response = requests.get(f"{self.api_url}/observation").json()
        observation = np.array(obs_response['observation'], dtype=np.float32)
        raw_counts = obs_response['raw_counts']
        
        # YOUR REWARD FUNCTION
        reward = self._calculate_reward(raw_counts, action)
        
        self.current_step += 1
        terminated = self.current_step >= self.max_steps
        truncated = False
        
        return observation, reward, terminated, truncated, {}
    
    def _calculate_reward(self, vehicle_counts: list, action: int) -> float:
        """
        Calculate reward - THIS IS YOUR RESPONSIBILITY
        
        Example reward function:
        - Penalize total waiting vehicles
        - Penalize uneven distribution
        - Penalize frequent phase changes
        """
        total_vehicles = sum(vehicle_counts)
        max_queue = max(vehicle_counts)
        avg_queue = total_vehicles / len(vehicle_counts)
        std_queue = np.std(vehicle_counts)
        
        reward = 0.0
        reward -= total_vehicles * 0.1
        reward -= max_queue * 0.5
        reward -= std_queue * 0.2
        
        return reward
    
    def render(self):
        """Rendering handled by Team B's camera stream"""
        pass
    
    def close(self):
        """Close environment"""
        pass


# Training script
def train_ppo(api_url: str):
    """Train PPO agent"""
    
    env = TrafficLightEnv(api_url)
    
    check_env(env)
    
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        tensorboard_log="./ppo_traffic_logs/"
    )
    
    print("Starting training...")
    model.learn(total_timesteps=100000, progress_bar=True)
    
    model.save("ppo_traffic_light")
    print("Training complete! Model saved.")
    
    return model


if __name__ == "__main__":
    API_URL = "https://xxxxx-8000.proxy.runpod.net"  # Replace with actual URL
    
    # Train
    model = train_ppo(API_URL)
    
    # Test trained agent
    env = TrafficLightEnv(API_URL)
    obs, _ = env.reset()
    
    for i in range(100):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, _ = env.step(action)
        
        print(f"Step {i}: Action={action}, Reward={reward:.2f}")
        
        if terminated or truncated:
            obs, _ = env.reset()
```

---

## Reward Function - רעיונות

זו **האחריות שלך**, אבל הנה כמה רעיונות:

### Reward Function 1: Minimize Total Waiting

```python
def calculate_reward(vehicle_counts, action):
    total_waiting = sum(vehicle_counts)
    reward = -total_waiting  # Less vehicles waiting = better
    return reward
```

### Reward Function 2: Balance Queues

```python
def calculate_reward(vehicle_counts, action):
    max_queue = max(vehicle_counts)
    min_queue = min(vehicle_counts)
    imbalance = max_queue - min_queue
    
    reward = -imbalance  # Balanced queues = better
    return reward
```

### Reward Function 3: Comprehensive

```python
def calculate_reward(vehicle_counts, action, prev_action=None):
    total_vehicles = sum(vehicle_counts)
    max_queue = max(vehicle_counts)
    std_queue = np.std(vehicle_counts)
    
    # Penalize total waiting
    reward = -total_vehicles * 0.1
    
    # Penalize longest queue
    reward -= max_queue * 0.5
    
    # Penalize imbalance
    reward -= std_queue * 0.2
    
    # Penalize frequent changes (optional)
    if prev_action is not None and action != prev_action:
        reward -= 1.0
    
    # Bonus for empty lanes
    empty_lanes = sum(1 for c in vehicle_counts if c == 0)
    reward += empty_lanes * 0.5
    
    return reward
```

**בחר או שנה לפי המטרות שלך!**

---

## API Endpoints - סיכום

### Main Endpoints

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/observation` | Get current state | Vehicle counts per lane |
| POST | `/action` | Set traffic phase | Confirmation |
| GET | `/state` | Get full state | Complete state info |
| GET | `/health` | Health check | System status |
| POST | `/reset` | Reset episode | Confirmation |

### Complete API Docs

See `docs/API_SPEC.md` for full specifications.

---

## Testing Your Integration

### Quick Test

```python
import requests

API_URL = "https://xxxxx-8000.proxy.runpod.net"

# 1. Check health
health = requests.get(f"{API_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Get configuration
config = requests.get(f"{API_URL}/config").json()
print(f"Lanes: {config['num_lanes']}, Phases: {config['num_phases']}")

# 3. Get observation
obs = requests.get(f"{API_URL}/observation").json()
print(f"Current state: {obs['observation']}")
print(f"Raw counts: {obs['raw_counts']}")

# 4. Send action
action = {"action": 2}
result = requests.post(f"{API_URL}/action", json=action).json()
print(f"Action result: {result}")
```

---

## Monitoring During Training

### View Live Simulation

Open in browser:
```
https://[pod-id]-6080.proxy.runpod.net
```

You'll see CARLA running with vehicles!

### View Camera + Detections

```
https://[pod-id]-8000.proxy.runpod.net/camera/stream
```

You'll see:
- Vehicle bounding boxes (YOLO)
- Lane ROI zones
- Vehicle counts

### API Metrics

```python
metrics = requests.get(f"{API_URL}/metrics").json()
print(f"Vehicles served: {metrics['total_vehicles_served']}")
print(f"Average wait: {metrics['average_waiting_time']:.2f}s")
```

---

## Performance Expectations

- **API latency**: 50-200ms per request
- **Throughput**: ~20 observations/second
- **Training speed**: ~1000 steps per 10 minutes
- **Episode length**: Recommend 500-2000 steps

---

## Coordination

### What Team B (me) provides:
✅ CARLA simulator running on GPU  
✅ YOLO vehicle detection  
✅ Vehicle counts per lane (observation)  
✅ Traffic light control (action execution)  
✅ REST API for communication  
✅ Camera visualization  

### What Team A (you) provides:
🔲 PPO algorithm implementation  
🔲 Reward function definition  
🔲 Training loop and hyperparameters  
🔲 Performance analysis and graphs  

---

## Questions?

If something doesn't work or you need:
- Different observation format (e.g., add waiting times)
- Additional state information
- Changes to action space
- Help debugging

**Contact Team B!**

---

## Example: Baseline Comparison

To show your PPO is better than fixed-time control:

```python
# Baseline: Fixed-time controller
def baseline_controller(step):
    """Simple fixed-time baseline"""
    cycle = [0, 0, 0, 1, 2, 2, 2, 3]  # Repeat this pattern
    return cycle[step % len(cycle)]

# Run baseline
total_reward = 0
for step in range(1000):
    action = baseline_controller(step)
    obs, reward, done, _, _ = env.step(action)
    total_reward += reward

print(f"Baseline reward: {total_reward}")

# Then compare to your trained PPO!
```

---

Good luck with your PPO training! 🚀🤖
