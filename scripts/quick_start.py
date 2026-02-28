"""
Quick Start Script
Demonstrates how to use the vision system
"""

import sys
import time
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


def test_api_connection(base_url: str = "http://localhost:8000"):
    """Test if API is accessible"""
    print(f"Testing connection to {base_url}...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy!")
            print(f"  - CARLA connected: {data['carla_connected']}")
            print(f"  - YOLO loaded: {data['yolo_loaded']}")
            print(f"  - Lanes: {data['num_lanes']}")
            print(f"  - Phases: {data['num_phases']}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("\nMake sure:")
        print("  1. Docker container is running: docker ps")
        print("  2. API is accessible: docker logs carla-system")
        return False


def get_config(base_url: str):
    """Get intersection configuration"""
    print("\nGetting configuration...")
    response = requests.get(f"{base_url}/config")
    config = response.json()
    
    print(f"Intersection Configuration:")
    print(f"  - Lanes: {config['num_lanes']}")
    print(f"  - Phases: {config['num_phases']}")
    print(f"  - Observation shape: {config['observation_shape']}")
    print(f"  - Action space: 0 to {config['action_space_size'] - 1}")
    
    return config


def demo_rl_loop(base_url: str, num_steps: int = 10):
    """Demonstrate RL loop (observation -> action)"""
    print(f"\n{'='*60}")
    print("Demonstrating RL Loop (Team A would do this)")
    print(f"{'='*60}\n")
    
    for step in range(num_steps):
        print(f"Step {step + 1}:")
        
        obs_response = requests.get(f"{base_url}/observation").json()
        
        observation = obs_response['observation']
        raw_counts = obs_response['raw_counts']
        
        print(f"  Raw vehicle counts: {raw_counts}")
        print(f"  Normalized obs: {[f'{x:.2f}' for x in observation]}")
        print(f"  Total vehicles: {sum(raw_counts)}")
        
        action = step % 5
        
        action_request = {"action": action, "duration": 5.0}
        action_response = requests.post(f"{base_url}/action", json=action_request).json()
        
        print(f"  Action taken: {action} ({action_response['phase_name']})")
        
        time.sleep(1)
        print()


def show_camera_info(base_url: str):
    """Show camera stream URL"""
    print(f"\n{'='*60}")
    print("Camera Visualization")
    print(f"{'='*60}")
    print(f"\nOpen this URL in your browser to see live camera feed:")
    print(f"  {base_url}/camera/stream")
    print("\nYou will see:")
    print("  - Real-time CARLA simulation")
    print("  - YOLO bounding boxes around vehicles")
    print("  - ROI zones for each lane (colored)")
    print("  - Vehicle count overlay")


def show_next_steps():
    """Show what to do next"""
    print(f"\n{'='*60}")
    print("Next Steps")
    print(f"{'='*60}")
    print("\n1. Fine-tune YOLO (optional):")
    print("   python scripts/generate_dataset.py --frames 1000")
    print("   python yolo_detection/train_yolo.py")
    print()
    print("2. Adjust ROI zones:")
    print("   Edit config/intersection_config.yaml")
    print("   View results at: http://localhost:8000/camera/stream")
    print()
    print("3. Share API with Team A:")
    print("   Give them: https://[pod-id]-8000.proxy.runpod.net")
    print("   And: docs/API_SPEC.md")
    print()
    print("4. Start training!")
    print("   Team A runs their PPO training loop")
    print("   You monitor at: https://[pod-id]-6080.proxy.runpod.net")


def main():
    """Main quick start demo"""
    print(f"{'='*60}")
    print("Intelligent Traffic Light - Quick Start Demo")
    print("Team B: Vision & Sensing System")
    print(f"{'='*60}\n")
    
    base_url = input("Enter API URL (default: http://localhost:8000): ").strip()
    if not base_url:
        base_url = "http://localhost:8000"
    
    if not test_api_connection(base_url):
        print("\n❌ Cannot connect to API. Exiting.")
        return
    
    config = get_config(base_url)
    
    print("\nWould you like to run a demo RL loop? (y/n): ", end="")
    if input().lower() == 'y':
        demo_rl_loop(base_url, num_steps=10)
    
    show_camera_info(base_url)
    show_next_steps()
    
    print(f"\n{'='*60}")
    print("Demo complete! You're ready to go.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
