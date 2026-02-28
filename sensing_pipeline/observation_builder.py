"""
Observation Builder - Creates observation vectors for RL agent
This is the critical interface with Team A's PPO agent
"""

import numpy as np
import time
from typing import Dict, Optional
from loguru import logger


class ObservationBuilder:
    """Builds standardized observations for reinforcement learning agent"""
    
    def __init__(self, num_lanes: int, normalize: bool = True, max_vehicles_per_lane: int = 20):
        """
        Initialize observation builder
        
        Args:
            num_lanes: Number of lanes (observation vector size)
            normalize: If True, normalize counts to [0, 1]
            max_vehicles_per_lane: Maximum expected vehicles per lane (for normalization)
        """
        self.num_lanes = num_lanes
        self.normalize = normalize
        self.max_vehicles_per_lane = max_vehicles_per_lane
        
        self.frame_id = 0
        self.last_observation: Optional[np.ndarray] = None
        self.last_timestamp: float = 0.0
        
        logger.info(f"Observation builder initialized: {num_lanes} lanes, normalize={normalize}")
    
    def build_observation(self, vehicle_counts: np.ndarray, additional_features: Dict = None) -> Dict:
        """
        Build observation dictionary for RL agent
        
        Args:
            vehicle_counts: Vehicle counts per lane
            additional_features: Optional additional state features
            
        Returns:
            Observation dictionary with standardized format
        """
        if len(vehicle_counts) != self.num_lanes:
            logger.error(f"Invalid vehicle counts size: expected {self.num_lanes}, got {len(vehicle_counts)}")
            vehicle_counts = np.zeros(self.num_lanes, dtype=np.float32)
        
        observation = vehicle_counts.astype(np.float32)
        
        if self.normalize:
            observation = np.clip(observation / self.max_vehicles_per_lane, 0.0, 1.0)
        
        self.last_observation = observation
        self.last_timestamp = time.time()
        self.frame_id += 1
        
        obs_dict = {
            'observation': observation.tolist(),
            'frame_id': self.frame_id,
            'timestamp': self.last_timestamp,
            'num_lanes': self.num_lanes,
            'raw_counts': vehicle_counts.tolist()
        }
        
        if additional_features:
            obs_dict['additional_features'] = additional_features
        
        return obs_dict
    
    def get_observation_space_info(self) -> Dict:
        """
        Get information about observation space for RL agent configuration
        
        Returns:
            Dictionary with observation space specifications
        """
        return {
            'shape': (self.num_lanes,),
            'dtype': 'float32',
            'low': 0.0,
            'high': 1.0 if self.normalize else float(self.max_vehicles_per_lane),
            'description': 'Vehicle counts per lane (normalized)' if self.normalize else 'Vehicle counts per lane'
        }
    
    def validate_observation(self, observation: np.ndarray) -> bool:
        """
        Validate observation format
        
        Args:
            observation: Observation array
            
        Returns:
            True if valid
        """
        if not isinstance(observation, np.ndarray):
            logger.error("Observation must be numpy array")
            return False
        
        if observation.shape != (self.num_lanes,):
            logger.error(f"Invalid shape: expected ({self.num_lanes},), got {observation.shape}")
            return False
        
        if self.normalize:
            if np.any(observation < 0) or np.any(observation > 1):
                logger.error("Normalized observation must be in [0, 1]")
                return False
        
        return True
    
    def reset(self):
        """Reset observation builder state"""
        self.frame_id = 0
        self.last_observation = None
        self.last_timestamp = 0.0
        logger.info("Observation builder reset")


if __name__ == "__main__":
    # Test observation builder
    builder = ObservationBuilder(num_lanes=8, normalize=True)
    
    test_counts = np.array([3, 5, 2, 4, 1, 0, 3, 2])
    
    obs_dict = builder.build_observation(test_counts)
    
    print("Observation:")
    print(f"  Raw counts: {obs_dict['raw_counts']}")
    print(f"  Normalized: {obs_dict['observation']}")
    print(f"  Frame ID: {obs_dict['frame_id']}")
    print(f"  Timestamp: {obs_dict['timestamp']}")
    
    print("\nObservation Space Info:")
    print(builder.get_observation_space_info())
