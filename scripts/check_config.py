"""
Configuration Checker
Validates all configuration files and shows summary
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import config
from loguru import logger


def check_config():
    """Check and display configuration"""
    print("=" * 60)
    print("Configuration Summary")
    print("=" * 60)
    
    print("\n📊 Intersection Configuration:")
    print(f"  Name: {config.intersection['intersection']['name']}")
    print(f"  Type: {config.intersection['intersection']['type']}")
    print(f"  Number of lanes: {config.num_lanes}")
    print(f"  Number of phases: {config.num_phases}")
    
    print("\n🚗 Lane Details:")
    for lane in config.intersection['intersection']['lanes']:
        print(f"  Lane {lane['id']}: {lane['name']} ({lane['direction']} {lane['movement']})")
    
    print("\n🚦 Traffic Light Phases:")
    for phase in config.intersection['intersection']['traffic_phases']:
        print(f"  Phase {phase['id']}: {phase['name']} (duration: {phase['duration']}s)")
        print(f"    Green lanes: {phase['green_lanes']}")
    
    print("\n📷 Camera Configuration:")
    for cam in config.intersection['intersection']['cameras']:
        print(f"  {cam['name']}:")
        print(f"    Position: ({cam['position']['x']}, {cam['position']['y']}, {cam['position']['z']})")
        print(f"    Resolution: {cam['resolution']['width']}x{cam['resolution']['height']}")
        print(f"    FOV: {cam['fov']}°")
    
    print("\n🎮 CARLA Configuration:")
    print(f"  Map: {config.carla['carla']['map_name']}")
    print(f"  Vehicles: {config.carla['carla']['traffic']['num_vehicles']}")
    print(f"  FPS: {1.0 / config.carla['carla']['fixed_delta_seconds']:.0f}")
    print(f"  Rendering: {'Disabled' if config.carla['carla']['no_rendering_mode'] else 'Enabled'}")
    
    print("\n🤖 YOLO Configuration:")
    print(f"  Model: {config.yolo['yolo']['model_version']}")
    print(f"  Weights: {config.yolo['yolo']['weights']}")
    print(f"  Device: {config.yolo['yolo']['device']}")
    print(f"  Confidence: {config.yolo['yolo']['detection']['confidence_threshold']}")
    print(f"  Target classes: {config.yolo['yolo']['detection']['target_classes']}")
    
    print("\n🔗 RL Interface:")
    print(f"  Observation space: {config.observation_shape}")
    print(f"  Action space: Discrete({config.action_space_size})")
    
    print("\n" + "=" * 60)
    print("Configuration check complete!")
    print("=" * 60)
    
    validation_checks()


def validation_checks():
    """Run validation checks"""
    print("\n✓ Running validation checks...")
    
    issues = []
    
    if config.num_lanes != len(config.intersection['intersection']['lanes']):
        issues.append("⚠️  num_lanes doesn't match lanes list length")
    
    if config.num_phases != len(config.intersection['intersection']['traffic_phases']):
        issues.append("⚠️  num_phases doesn't match traffic_phases list length")
    
    for phase in config.intersection['intersection']['traffic_phases']:
        for lane_id in phase['green_lanes']:
            if lane_id >= config.num_lanes:
                issues.append(f"⚠️  Phase {phase['id']} references invalid lane {lane_id}")
    
    for lane in config.intersection['intersection']['lanes']:
        if not lane.get('roi'):
            issues.append(f"⚠️  Lane {lane['id']} has no ROI defined")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ All validation checks passed!")


if __name__ == "__main__":
    try:
        check_config()
    except Exception as e:
        logger.error(f"Error checking config: {e}")
        sys.exit(1)
