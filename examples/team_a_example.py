"""
Example code for Team A - How to use Team B's API
This shows how Team A can train their PPO agent using our vision system
"""

import requests
import numpy as np
import time
from typing import Tuple


class TeamBAPIClient:
    """
    Simple client for Team B's vision API
    Team A can use this to interact with the system
    """
    
    def __init__(self, api_url: str):
        """
        Initialize API client
        
        Args:
            api_url: Base URL of Team B's API (e.g., https://xxxxx-8000.proxy.runpod.net)
        """
        self.api_url = api_url.rstrip('/')
        self._check_connection()
    
    def _check_connection(self):
        """Verify API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✓ Connected to Team B API")
                print(f"  Lanes: {health['num_lanes']}, Phases: {health['num_phases']}")
            else:
                raise Exception(f"API returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"Cannot connect to Team B API: {e}")
    
    def get_observation(self) -> Tuple[np.ndarray, dict]:
        """
        Get current observation (vehicle counts)
        
        Returns:
            Tuple of (observation array, full response dict)
        """
        response = requests.get(f"{self.api_url}/observation")
        response.raise_for_status()
        
        data = response.json()
        observation = np.array(data['observation'], dtype=np.float32)
        
        return observation, data
    
    def send_action(self, action: int, duration: float = None) -> dict:
        """
        Send action (traffic light phase)
        
        Args:
            action: Phase ID (0 to num_phases-1)
            duration: Optional duration in seconds
            
        Returns:
            Response dictionary
        """
        payload = {"action": action}
        if duration is not None:
            payload["duration"] = duration
        
        response = requests.post(f"{self.api_url}/action", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def reset(self) -> dict:
        """Reset episode"""
        response = requests.post(f"{self.api_url}/reset")
        response.raise_for_status()
        return response.json()
    
    def get_state(self) -> dict:
        """Get full intersection state"""
        response = requests.get(f"{self.api_url}/state")
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> dict:
        """Get performance metrics"""
        response = requests.get(f"{self.api_url}/metrics")
        response.raise_for_status()
        return response.json()


def simple_reward_function(vehicle_counts: list, action: int) -> float:
    """
    Example reward function - Team A should customize this!
    
    Args:
        vehicle_counts: Raw vehicle counts per lane
        action: Action taken
        
    Returns:
        Reward value
    """
    total_vehicles = sum(vehicle_counts)
    max_queue = max(vehicle_counts)
    
    reward = -total_vehicles * 0.1
    reward -= max_queue * 0.5
    
    return reward


def demo_manual_control(api_url: str, num_steps: int = 50):
    """
    Demo: Manual control without RL
    Just cycles through phases
    """
    print("Demo: Manual Control")
    print("=" * 60)
    
    client = TeamBAPIClient(api_url)
    client.reset()
    
    total_reward = 0.0
    
    for step in range(num_steps):
        obs, obs_data = client.get_observation()
        
        action = step % 5
        
        client.send_action(action, duration=5.0)
        
        reward = simple_reward_function(obs_data['raw_counts'], action)
        total_reward += reward
        
        if step % 10 == 0:
            print(f"Step {step}: Obs={obs}, Action={action}, Reward={reward:.2f}")
        
        time.sleep(0.5)
    
    print(f"\nTotal reward: {total_reward:.2f}")


def demo_random_policy(api_url: str, num_episodes: int = 5, steps_per_episode: int = 100):
    """
    Demo: Random policy (baseline)
    """
    print("Demo: Random Policy Baseline")
    print("=" * 60)
    
    client = TeamBAPIClient(api_url)
    
    episode_rewards = []
    
    for episode in range(num_episodes):
        client.reset()
        episode_reward = 0.0
        
        for step in range(steps_per_episode):
            obs, obs_data = client.get_observation()
            
            action = np.random.randint(0, 5)
            
            client.send_action(action)
            
            reward = simple_reward_function(obs_data['raw_counts'], action)
            episode_reward += reward
        
        episode_rewards.append(episode_reward)
        print(f"Episode {episode + 1}: Reward = {episode_reward:.2f}")
    
    avg_reward = np.mean(episode_rewards)
    print(f"\nAverage reward: {avg_reward:.2f} (+/- {np.std(episode_rewards):.2f})")


def demo_greedy_policy(api_url: str, num_steps: int = 100):
    """
    Demo: Greedy policy - always choose phase that serves most vehicles
    """
    print("Demo: Greedy Policy")
    print("=" * 60)
    
    client = TeamBAPIClient(api_url)
    client.reset()
    
    config_data = requests.get(f"{api_url}/config").json()
    phases = config_data['phases']
    
    total_reward = 0.0
    
    for step in range(num_steps):
        obs, obs_data = client.get_observation()
        vehicle_counts = obs_data['raw_counts']
        
        best_action = 0
        best_score = -float('inf')
        
        for phase_id, phase in enumerate(phases):
            green_lanes = phase['green_lanes']
            score = sum(vehicle_counts[lane] for lane in green_lanes)
            
            if score > best_score:
                best_score = score
                best_action = phase_id
        
        client.send_action(best_action)
        
        reward = simple_reward_function(vehicle_counts, best_action)
        total_reward += reward
        
        if step % 20 == 0:
            print(f"Step {step}: Best action={best_action} (serves {best_score} vehicles)")
    
    print(f"\nTotal reward: {total_reward:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Team A Example Usage")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Team B API URL"
    )
    parser.add_argument(
        "--demo",
        choices=['manual', 'random', 'greedy', 'all'],
        default='manual',
        help="Which demo to run"
    )
    
    args = parser.parse_args()
    
    if args.demo == 'manual':
        demo_manual_control(args.url, num_steps=50)
    elif args.demo == 'random':
        demo_random_policy(args.url, num_episodes=5)
    elif args.demo == 'greedy':
        demo_greedy_policy(args.url, num_steps=100)
    elif args.demo == 'all':
        demo_manual_control(args.url, num_steps=30)
        print("\n")
        demo_random_policy(args.url, num_episodes=3)
        print("\n")
        demo_greedy_policy(args.url, num_steps=50)
