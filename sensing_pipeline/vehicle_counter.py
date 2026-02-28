"""
Vehicle Counter - Maintains vehicle counts per lane
"""

import numpy as np
from typing import Dict, List
from collections import deque
from loguru import logger


class VehicleCounter:
    """Counts and tracks vehicles per lane with temporal smoothing"""
    
    def __init__(self, num_lanes: int, smoothing_window: int = 3):
        """
        Initialize vehicle counter
        
        Args:
            num_lanes: Number of lanes to track
            smoothing_window: Number of frames to average for smoothing
        """
        self.num_lanes = num_lanes
        self.smoothing_window = smoothing_window
        
        self.history = {i: deque(maxlen=smoothing_window) for i in range(num_lanes)}
        self.current_counts = np.zeros(num_lanes, dtype=np.int32)
        
        logger.info(f"Vehicle counter initialized for {num_lanes} lanes")
    
    def update(self, raw_counts: np.ndarray) -> np.ndarray:
        """
        Update vehicle counts with new observation
        
        Args:
            raw_counts: Raw vehicle counts from current frame
            
        Returns:
            Smoothed vehicle counts
        """
        if len(raw_counts) != self.num_lanes:
            logger.error(f"Expected {self.num_lanes} lanes, got {len(raw_counts)}")
            return self.current_counts
        
        for lane_id in range(self.num_lanes):
            self.history[lane_id].append(raw_counts[lane_id])
        
        smoothed_counts = np.array([
            int(np.mean(self.history[i])) for i in range(self.num_lanes)
        ], dtype=np.int32)
        
        self.current_counts = smoothed_counts
        return smoothed_counts
    
    def get_counts(self) -> np.ndarray:
        """Get current vehicle counts"""
        return self.current_counts.copy()
    
    def get_total_vehicles(self) -> int:
        """Get total number of vehicles across all lanes"""
        return int(np.sum(self.current_counts))
    
    def get_lane_count(self, lane_id: int) -> int:
        """Get vehicle count for specific lane"""
        if 0 <= lane_id < self.num_lanes:
            return int(self.current_counts[lane_id])
        return 0
    
    def get_statistics(self) -> Dict:
        """Get statistics about current state"""
        return {
            'total_vehicles': self.get_total_vehicles(),
            'counts_per_lane': self.current_counts.tolist(),
            'max_lane_count': int(np.max(self.current_counts)),
            'min_lane_count': int(np.min(self.current_counts)),
            'avg_lane_count': float(np.mean(self.current_counts)),
            'std_lane_count': float(np.std(self.current_counts))
        }
    
    def reset(self):
        """Reset all counts"""
        for i in range(self.num_lanes):
            self.history[i].clear()
        self.current_counts = np.zeros(self.num_lanes, dtype=np.int32)
        logger.info("Vehicle counter reset")


if __name__ == "__main__":
    # Test vehicle counter
    counter = VehicleCounter(num_lanes=8, smoothing_window=3)
    
    test_counts = [
        np.array([3, 5, 2, 4, 1, 0, 3, 2]),
        np.array([4, 5, 2, 3, 2, 1, 3, 2]),
        np.array([3, 6, 3, 4, 1, 0, 4, 3]),
    ]
    
    for i, counts in enumerate(test_counts):
        smoothed = counter.update(counts)
        print(f"Frame {i}: Raw={counts}, Smoothed={smoothed}")
    
    print("\nStatistics:")
    print(counter.get_statistics())
