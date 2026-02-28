"""
ROI Mapper - Maps vehicle detections to specific lanes
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
from loguru import logger


class ROIMapper:
    """Maps bounding box detections to lane-specific regions of interest"""
    
    def __init__(self, lane_configs: List[Dict]):
        """
        Initialize ROI mapper
        
        Args:
            lane_configs: List of lane configurations with ROI definitions
        """
        self.lane_configs = lane_configs
        self.num_lanes = len(lane_configs)
        
        self.roi_polygons = {}
        for lane in lane_configs:
            lane_id = lane['id']
            rois = lane.get('roi', [])
            
            polygons = []
            for roi in rois:
                if len(roi) == 4:
                    x1, y1, x2, y2 = roi
                    polygon = np.array([
                        [x1, y1],
                        [x2, y1],
                        [x2, y2],
                        [x1, y2]
                    ], dtype=np.int32)
                    polygons.append(polygon)
            
            self.roi_polygons[lane_id] = polygons
        
        logger.info(f"ROI Mapper initialized with {self.num_lanes} lanes")
    
    def point_in_roi(self, point: Tuple[int, int], lane_id: int) -> bool:
        """
        Check if a point is inside a lane's ROI
        
        Args:
            point: (x, y) coordinates
            lane_id: Lane identifier
            
        Returns:
            True if point is inside ROI
        """
        if lane_id not in self.roi_polygons:
            return False
        
        for polygon in self.roi_polygons[lane_id]:
            result = cv2.pointPolygonTest(polygon, point, False)
            if result >= 0:
                return True
        
        return False
    
    def map_detections_to_lanes(self, detections: List) -> Dict[int, List]:
        """
        Map vehicle detections to specific lanes
        
        Args:
            detections: List of Detection objects
            
        Returns:
            Dictionary mapping lane_id to list of detections
        """
        lane_detections = {i: [] for i in range(self.num_lanes)}
        
        for detection in detections:
            center = detection.center
            
            for lane_id in range(self.num_lanes):
                if self.point_in_roi(center, lane_id):
                    lane_detections[lane_id].append(detection)
                    break
        
        return lane_detections
    
    def count_vehicles_per_lane(self, detections: List) -> np.ndarray:
        """
        Count vehicles in each lane (creates observation vector)
        
        Args:
            detections: List of Detection objects
            
        Returns:
            Numpy array of vehicle counts [lane0_count, lane1_count, ...]
        """
        lane_detections = self.map_detections_to_lanes(detections)
        counts = np.array([len(lane_detections[i]) for i in range(self.num_lanes)], dtype=np.int32)
        return counts
    
    def visualize_rois(self, image: np.ndarray, detections: List = None) -> np.ndarray:
        """
        Draw ROIs on image for debugging
        
        Args:
            image: Input image
            detections: Optional list of detections to show mapping
            
        Returns:
            Image with ROIs drawn
        """
        result_image = image.copy()
        
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 128, 0), (128, 0, 128)
        ]
        
        for lane_id, polygons in self.roi_polygons.items():
            color = colors[lane_id % len(colors)]
            
            for polygon in polygons:
                cv2.polylines(result_image, [polygon], isClosed=True, color=color, thickness=3)
                
                centroid = polygon.mean(axis=0).astype(int)
                cv2.putText(
                    result_image,
                    f"Lane {lane_id}",
                    tuple(centroid),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )
        
        if detections:
            lane_detections = self.map_detections_to_lanes(detections)
            
            for lane_id, lane_dets in lane_detections.items():
                for det in lane_dets:
                    color = colors[lane_id % len(colors)]
                    cv2.circle(result_image, det.center, 8, color, -1)
        
        return result_image
    
    def get_lane_info(self, lane_id: int) -> Dict:
        """Get lane configuration info"""
        for lane in self.lane_configs:
            if lane['id'] == lane_id:
                return lane
        return {}


if __name__ == "__main__":
    # Test ROI mapping
    import sys
    sys.path.append('..')
    from config import config
    
    lanes = config.intersection['intersection']['lanes']
    mapper = ROIMapper(lanes)
    
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    test_point = (150, 300)
    for i in range(mapper.num_lanes):
        if mapper.point_in_roi(test_point, i):
            print(f"Point {test_point} is in Lane {i}")
    
    vis_image = mapper.visualize_rois(test_image)
    cv2.imwrite("roi_visualization.png", vis_image)
    print("ROI visualization saved to roi_visualization.png")
