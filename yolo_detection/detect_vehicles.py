"""
Vehicle Detector using YOLO (ultralytics)
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
from loguru import logger


class Detection:
    """Represents a single vehicle detection"""
    
    def __init__(self, bbox: Tuple[int, int, int, int], confidence: float, class_id: int, class_name: str):
        """
        Args:
            bbox: Bounding box as (x1, y1, x2, y2)
            confidence: Detection confidence score
            class_id: COCO class ID
            class_name: Class name (car, truck, etc.)
        """
        self.bbox = bbox
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        self.center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)


class VehicleDetector:
    """YOLO-based vehicle detector"""
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        target_classes: List[int] = None,
        device: str = "cuda"
    ):
        """
        Initialize YOLO vehicle detector
        
        Args:
            model_path: Path to YOLO model weights
            confidence_threshold: Minimum confidence for detections
            iou_threshold: NMS IOU threshold
            target_classes: List of class IDs to detect (default: [2,3,5,7] = vehicles)
            device: 'cuda' or 'cpu'
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.target_classes = target_classes or [2, 3, 5, 7]  # car, motorcycle, bus, truck
        self.device = device
        
        logger.info(f"Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        self.model.to(device)
        
        logger.success(f"YOLO model loaded on {device}")
        
        # COCO class names
        self.class_names = {
            2: "car",
            3: "motorcycle", 
            5: "bus",
            7: "truck"
        }
    
    def detect(self, image: np.ndarray, visualize: bool = False) -> Tuple[List[Detection], Optional[np.ndarray]]:
        """
        Detect vehicles in image
        
        Args:
            image: Input image as numpy array (H, W, 3)
            visualize: If True, return annotated image
            
        Returns:
            Tuple of (detections list, annotated image or None)
        """
        results = self.model.predict(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            classes=self.target_classes,
            verbose=False,
            device=self.device
        )
        
        detections = []
        result = results[0]
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)
            
            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = map(int, box)
                class_name = self.class_names.get(cls_id, f"class_{cls_id}")
                
                detection = Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=float(conf),
                    class_id=cls_id,
                    class_name=class_name
                )
                detections.append(detection)
        
        annotated_image = None
        if visualize and len(detections) > 0:
            annotated_image = self._draw_detections(image.copy(), detections)
        
        return detections, annotated_image
    
    def _draw_detections(self, image: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Draw bounding boxes on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Annotated image
        """
        colors = {
            2: (0, 255, 0),      # car - green
            3: (255, 255, 0),    # motorcycle - cyan
            5: (0, 0, 255),      # bus - red
            7: (255, 0, 255)     # truck - magenta
        }
        
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            color = colors.get(det.class_id, (255, 255, 255))
            
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det.class_name} {det.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            cv2.rectangle(
                image,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )
            
            cv2.putText(
                image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
        
        cv2.putText(
            image,
            f"Vehicles: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )
        
        return image
    
    def batch_detect(self, images: List[np.ndarray]) -> List[List[Detection]]:
        """
        Detect vehicles in multiple images (batch processing)
        
        Args:
            images: List of images
            
        Returns:
            List of detection lists
        """
        results = self.model.predict(
            images,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            classes=self.target_classes,
            verbose=False,
            device=self.device,
            stream=True
        )
        
        all_detections = []
        for result in results:
            detections = []
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)
                
                for box, conf, cls_id in zip(boxes, confidences, class_ids):
                    x1, y1, x2, y2 = map(int, box)
                    class_name = self.class_names.get(cls_id, f"class_{cls_id}")
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=float(conf),
                        class_id=cls_id,
                        class_name=class_name
                    )
                    detections.append(detection)
            
            all_detections.append(detections)
        
        return all_detections


if __name__ == "__main__":
    # Test detector
    detector = VehicleDetector(model_path="yolov8n.pt", device="cpu")
    
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    detections, annotated = detector.detect(test_image, visualize=True)
    print(f"Found {len(detections)} vehicles")
