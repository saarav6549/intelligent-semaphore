"""
State Manager - Manages overall intersection state
"""

import time
import numpy as np
from typing import Dict, Optional
from loguru import logger


class StateManager:
    """Manages the complete state of the intersection system"""
    
    def __init__(self, num_lanes: int, num_phases: int):
        """
        Initialize state manager
        
        Args:
            num_lanes: Number of lanes
            num_phases: Number of traffic light phases
        """
        self.num_lanes = num_lanes
        self.num_phases = num_phases
        
        self.current_phase: int = 0
        self.phase_start_time: float = 0.0
        self.phase_duration: float = 0.0
        
        self.vehicle_counts: np.ndarray = np.zeros(num_lanes, dtype=np.int32)
        self.total_vehicles_served: int = 0
        self.total_waiting_time: float = 0.0
        
        self.episode_start_time: float = time.time()
        self.step_count: int = 0
        
        logger.info(f"State manager initialized: {num_lanes} lanes, {num_phases} phases")
    
    def update_state(self, vehicle_counts: np.ndarray, current_phase: int):
        """
        Update state with new observations
        
        Args:
            vehicle_counts: Current vehicle counts per lane
            current_phase: Current traffic light phase
        """
        self.vehicle_counts = vehicle_counts
        
        if current_phase != self.current_phase:
            self.phase_start_time = time.time()
            self.current_phase = current_phase
            logger.info(f"Phase changed to {current_phase}")
        
        self.step_count += 1
    
    def set_phase(self, phase_id: int, duration: float = 30.0):
        """
        Set traffic light phase
        
        Args:
            phase_id: Phase identifier (0 to num_phases-1)
            duration: How long to keep this phase (seconds)
        """
        if not 0 <= phase_id < self.num_phases:
            logger.error(f"Invalid phase {phase_id}, must be 0-{self.num_phases-1}")
            return
        
        self.current_phase = phase_id
        self.phase_duration = duration
        self.phase_start_time = time.time()
        
        logger.info(f"Phase set to {phase_id} for {duration}s")
    
    def get_phase_elapsed_time(self) -> float:
        """Get time elapsed in current phase"""
        return time.time() - self.phase_start_time
    
    def should_change_phase(self) -> bool:
        """Check if current phase duration has expired"""
        return self.get_phase_elapsed_time() >= self.phase_duration
    
    def get_state_dict(self) -> Dict:
        """
        Get complete state as dictionary
        
        Returns:
            State dictionary
        """
        return {
            'vehicle_counts': self.vehicle_counts.tolist(),
            'current_phase': self.current_phase,
            'phase_elapsed_time': self.get_phase_elapsed_time(),
            'phase_duration': self.phase_duration,
            'step_count': self.step_count,
            'total_vehicles': int(np.sum(self.vehicle_counts)),
            'episode_runtime': time.time() - self.episode_start_time
        }
    
    def get_metrics(self) -> Dict:
        """
        Get performance metrics
        
        Returns:
            Metrics dictionary
        """
        return {
            'total_vehicles_served': self.total_vehicles_served,
            'total_waiting_time': self.total_waiting_time,
            'average_waiting_time': self.total_waiting_time / max(1, self.total_vehicles_served),
            'steps': self.step_count,
            'runtime': time.time() - self.episode_start_time
        }
    
    def reset(self):
        """Reset state for new episode"""
        self.current_phase = 0
        self.phase_start_time = time.time()
        self.phase_duration = 0.0
        self.vehicle_counts = np.zeros(self.num_lanes, dtype=np.int32)
        self.total_vehicles_served = 0
        self.total_waiting_time = 0.0
        self.episode_start_time = time.time()
        self.step_count = 0
        
        logger.info("State manager reset")


if __name__ == "__main__":
    # Test state manager
    manager = StateManager(num_lanes=8, num_phases=5)
    
    test_counts = np.array([3, 5, 2, 4, 1, 0, 3, 2])
    manager.update_state(test_counts, 0)
    
    print("Current state:")
    print(manager.get_state_dict())
    
    import time
    time.sleep(1)
    
    manager.set_phase(1, duration=20.0)
    print(f"\nPhase elapsed: {manager.get_phase_elapsed_time():.2f}s")
    
    print("\nMetrics:")
    print(manager.get_metrics())
