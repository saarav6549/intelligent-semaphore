"""
Dataset Generator for YOLO Training
Collects images and annotations from CARLA for fine-tuning YOLO
"""

import os
import cv2
import json
import carla
import numpy as np
from pathlib import Path
from typing import List, Dict
from loguru import logger


class DatasetGenerator:
    """Generates labeled dataset from CARLA for YOLO training"""
    
    def __init__(self, output_dir: str = "./datasets/carla_vehicles"):
        """
        Initialize dataset generator
        
        Args:
            output_dir: Directory to save dataset
        """
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.labels_dir = self.output_dir / "labels"
        
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        
        self.frame_count = 0
        
        logger.info(f"Dataset generator initialized: {self.output_dir}")
    
    def save_frame(self, image: np.ndarray, vehicles_in_view: List[carla.Actor], 
                   camera_transform: carla.Transform, camera_fov: float,
                   image_width: int, image_height: int):
        """
        Save a frame with YOLO annotations
        
        Args:
            image: Camera image
            vehicles_in_view: List of vehicle actors visible in frame
            camera_transform: Camera transform
            camera_fov: Camera field of view
            image_width: Image width
            image_height: Image height
        """
        frame_name = f"frame_{self.frame_count:06d}"
        
        image_path = self.images_dir / f"{frame_name}.jpg"
        cv2.imwrite(str(image_path), image)
        
        annotations = []
        for vehicle in vehicles_in_view:
            bbox = self._get_vehicle_bbox_in_image(
                vehicle,
                camera_transform,
                camera_fov,
                image_width,
                image_height
            )
            
            if bbox is not None:
                x_center, y_center, width, height = bbox
                class_id = self._get_vehicle_class_id(vehicle)
                annotations.append(f"{class_id} {x_center} {y_center} {width} {height}")
        
        label_path = self.labels_dir / f"{frame_name}.txt"
        with open(label_path, 'w') as f:
            f.write('\n'.join(annotations))
        
        self.frame_count += 1
        
        if self.frame_count % 50 == 0:
            logger.info(f"Saved {self.frame_count} frames")
    
    def _get_vehicle_bbox_in_image(
        self,
        vehicle: carla.Actor,
        camera_transform: carla.Transform,
        camera_fov: float,
        image_width: int,
        image_height: int
    ) -> tuple:
        """
        Calculate vehicle bounding box in image coordinates (YOLO format)
        
        Returns:
            (x_center, y_center, width, height) normalized to [0, 1], or None if not visible
        """
        bbox = vehicle.bounding_box
        vehicle_transform = vehicle.get_transform()
        
        vertices = bbox.get_world_vertices(vehicle_transform)
        
        camera_matrix = self._build_projection_matrix(image_width, image_height, camera_fov)
        
        points_2d = []
        for vertex in vertices:
            point_camera = self._world_to_camera(vertex, camera_transform)
            
            if point_camera[2] < 0:
                return None
            
            point_2d = self._camera_to_image(point_camera, camera_matrix, image_width, image_height)
            points_2d.append(point_2d)
        
        points_2d = np.array(points_2d)
        
        x_min = np.min(points_2d[:, 0])
        x_max = np.max(points_2d[:, 0])
        y_min = np.min(points_2d[:, 1])
        y_max = np.max(points_2d[:, 1])
        
        if x_max < 0 or x_min > image_width or y_max < 0 or y_min > image_height:
            return None
        
        x_center = (x_min + x_max) / 2 / image_width
        y_center = (y_min + y_max) / 2 / image_height
        width = (x_max - x_min) / image_width
        height = (y_max - y_min) / image_height
        
        x_center = np.clip(x_center, 0, 1)
        y_center = np.clip(y_center, 0, 1)
        width = np.clip(width, 0, 1)
        height = np.clip(height, 0, 1)
        
        return (x_center, y_center, width, height)
    
    def _world_to_camera(self, point: carla.Location, camera_transform: carla.Transform) -> np.ndarray:
        """Transform world coordinates to camera coordinates"""
        world_point = np.array([point.x, point.y, point.z, 1.0])
        
        camera_matrix = np.array(camera_transform.get_inverse_matrix())
        camera_point = camera_matrix @ world_point
        
        return np.array([camera_point[1], -camera_point[2], camera_point[0]])
    
    def _camera_to_image(self, point_camera: np.ndarray, projection_matrix: np.ndarray,
                        image_width: int, image_height: int) -> np.ndarray:
        """Project camera coordinates to image coordinates"""
        point_2d = projection_matrix @ np.array([point_camera[0], point_camera[1], point_camera[2], 1.0])
        point_2d = point_2d[:2] / point_2d[2]
        
        point_2d[0] = (point_2d[0] + 1.0) * image_width / 2.0
        point_2d[1] = (1.0 - point_2d[1]) * image_height / 2.0
        
        return point_2d
    
    def _build_projection_matrix(self, image_width: int, image_height: int, fov: float) -> np.ndarray:
        """Build camera projection matrix"""
        focal = image_width / (2.0 * np.tan(fov * np.pi / 360.0))
        K = np.identity(3)
        K[0, 0] = K[1, 1] = focal
        K[0, 2] = image_width / 2.0
        K[1, 2] = image_height / 2.0
        return K
    
    def _get_vehicle_class_id(self, vehicle: carla.Actor) -> int:
        """
        Get YOLO class ID for vehicle type
        
        Returns:
            2 for car, 3 for motorcycle, 5 for bus, 7 for truck
        """
        type_id = vehicle.type_id.lower()
        
        if 'motorcycle' in type_id or 'bike' in type_id:
            return 3
        elif 'truck' in type_id or 'carlacola' in type_id or 'cybertruck' in type_id:
            return 7
        elif 'bus' in type_id or 'van' in type_id:
            return 5
        else:
            return 2
    
    def create_data_yaml(self, train_split: float = 0.8):
        """
        Create data.yaml file for YOLO training
        
        Args:
            train_split: Fraction of data for training (rest for validation)
        """
        all_images = list(self.images_dir.glob("*.jpg"))
        num_train = int(len(all_images) * train_split)
        
        train_dir = self.output_dir / "train"
        val_dir = self.output_dir / "val"
        train_dir.mkdir(exist_ok=True)
        val_dir.mkdir(exist_ok=True)
        
        data_yaml = {
            'path': str(self.output_dir.absolute()),
            'train': 'images',
            'val': 'images',
            'names': {
                0: 'car',
                1: 'motorcycle',
                2: 'bus',
                3: 'truck'
            },
            'nc': 4
        }
        
        yaml_path = self.output_dir / "data.yaml"
        import yaml
        with open(yaml_path, 'w') as f:
            yaml.dump(data_yaml, f, default_flow_style=False)
        
        logger.success(f"Created data.yaml with {len(all_images)} images")
