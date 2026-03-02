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
        self._load_dotenv()
        self.carla = self._load_yaml("carla_config.yaml")
        self.yolo = self._load_yaml("yolo_config.yaml")
        self.intersection = self._load_yaml("intersection_config.yaml")
        self._apply_env_overrides()
    
    def _load_dotenv(self) -> None:
        """
        Load a local .env file if present (minimal parser).
        This enables easy overrides without editing YAML.
        """
        env_path = PROJECT_ROOT / ".env"
        if not env_path.exists():
            return
        
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)
        
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        filepath = CONFIG_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def _apply_env_overrides(self) -> None:
        """Override YAML configs from environment variables when provided."""
        carla_cfg = self.carla.setdefault("carla", {})
        
        if os.getenv("CARLA_HOST"):
            carla_cfg["host"] = os.environ["CARLA_HOST"]
        if os.getenv("CARLA_PORT"):
            carla_cfg["port"] = int(os.environ["CARLA_PORT"])
        if os.getenv("CARLA_TIMEOUT"):
            carla_cfg["timeout"] = float(os.environ["CARLA_TIMEOUT"])
        if os.getenv("CARLA_MAP_NAME"):
            carla_cfg["map_name"] = os.environ["CARLA_MAP_NAME"]
        
        yolo_cfg = self.yolo.setdefault("yolo", {})
        if os.getenv("YOLO_MODEL"):
            yolo_cfg["weights"] = os.environ["YOLO_MODEL"]
        if os.getenv("YOLO_DEVICE"):
            yolo_cfg["device"] = os.environ["YOLO_DEVICE"]
        if os.getenv("YOLO_CONFIDENCE"):
            yolo_cfg.setdefault("detection", {})["confidence_threshold"] = float(os.environ["YOLO_CONFIDENCE"])
    
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
