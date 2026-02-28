"""
Test YOLO detection
"""

import sys
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from yolo_detection import VehicleDetector
from loguru import logger


def test_yolo():
    """Test YOLO model loading and inference"""
    logger.info("Testing YOLO detector...")
    
    try:
        detector = VehicleDetector(model_path="yolov8n.pt", device="cpu")
        logger.success("YOLO model loaded")
        
        test_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        detections, annotated = detector.detect(test_image, visualize=True)
        
        logger.info(f"Detections: {len(detections)}")
        
        if annotated is not None:
            logger.success("Visualization works")
        
        logger.success("YOLO test passed")
        return True
        
    except Exception as e:
        logger.error(f"YOLO test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_yolo()
    sys.exit(0 if success else 1)
