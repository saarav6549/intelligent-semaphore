"""
YOLO Detection Module
Vehicle detection using YOLOv8/v10
"""

from .detect_vehicles import VehicleDetector
from .roi_mapping import ROIMapper
from .dataset_generator import DatasetGenerator

__all__ = ['VehicleDetector', 'ROIMapper', 'DatasetGenerator']
