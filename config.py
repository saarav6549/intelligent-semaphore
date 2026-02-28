"""
Central Configuration Manager
Loads all YAML configs and provides easy access
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent
CONFIG_DIR = PROJECT_ROOT / "config"


class Config:
    """Centralized configuration manager"""
    
    def __init__(self):
        self.carla = self._load_yaml("carla_config.yaml")
        self.yolo = self._load_yaml("yolo_config.yaml")
        self.intersection = self._load_yaml("intersection_config.yaml")
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        filepath = CONFIG_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    @property
    def num_lanes(self) -> int:
        """Get number of lanes (observation vector size)"""
        return self.intersection['intersection']['num_lanes']
    
    @property
    def num_phases(self) -> int:
        """Get number of traffic light phases (action space size)"""
        return len(self.intersection['intersection']['traffic_phases'])
    
    @property
    def observation_shape(self) -> tuple:
        """Shape of observation vector for RL agent"""
        return (self.num_lanes,)
    
    @property
    def action_space_size(self) -> int:
        """Size of discrete action space"""
        return self.num_phases


# Global config instance
config = Config()


if __name__ == "__main__":
    # Test configuration loading
    print(f"Number of lanes: {config.num_lanes}")
    print(f"Number of phases: {config.num_phases}")
    print(f"Observation shape: {config.observation_shape}")
    print(f"Action space size: {config.action_space_size}")
