"""
ROI Calibration Tool
Interactive tool to help you set up ROI zones for lane detection
"""

import sys
import cv2
import numpy as np
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from carla_integration import CarlaClient, CameraManager
from loguru import logger


class ROICalibrator:
    """Interactive ROI calibration tool"""
    
    def __init__(self):
        self.image = None
        self.current_roi = []
        self.all_rois = {}
        self.current_lane = 0
        self.num_lanes = 8
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for ROI selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_roi.append((x, y))
            print(f"Point added: ({x}, {y})")
            
            if len(self.current_roi) == 4:
                self.save_current_roi()
    
    def save_current_roi(self):
        """Save current ROI and move to next lane"""
        x1, y1 = self.current_roi[0]
        x2, y2 = self.current_roi[2]
        
        roi_rect = [
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2)
        ]
        
        self.all_rois[self.current_lane] = roi_rect
        
        print(f"Lane {self.current_lane} ROI saved: {roi_rect}")
        
        self.current_lane += 1
        self.current_roi = []
        
        if self.current_lane >= self.num_lanes:
            print("\nAll ROIs defined!")
            self.export_rois()
    
    def draw_rois(self, image):
        """Draw current ROIs on image"""
        result = image.copy()
        
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 128, 0), (128, 0, 128)
        ]
        
        for lane_id, roi in self.all_rois.items():
            x1, y1, x2, y2 = roi
            color = colors[lane_id % len(colors)]
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 3)
            cv2.putText(result, f"Lane {lane_id}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        for i, (x, y) in enumerate(self.current_roi):
            cv2.circle(result, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(result, f"P{i+1}", (x + 10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if self.current_lane < self.num_lanes:
            cv2.putText(result, f"Defining Lane {self.current_lane} - Click 4 corners",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        return result
    
    def export_rois(self):
        """Export ROIs to YAML file"""
        output_path = PROJECT_ROOT / "config" / "rois_calibrated.yaml"
        
        lanes_config = []
        for lane_id, roi in self.all_rois.items():
            lanes_config.append({
                'id': lane_id,
                'name': f"Lane_{lane_id}",
                'roi': [roi]
            })
        
        with open(output_path, 'w') as f:
            yaml.dump({'lanes': lanes_config}, f, default_flow_style=False)
        
        print(f"\n✓ ROIs exported to: {output_path}")
        print("\nCopy these to config/intersection_config.yaml")
    
    def calibrate_from_carla(self):
        """Get image from CARLA and calibrate ROIs"""
        logger.info("Connecting to CARLA...")
        
        client = CarlaClient()
        if not client.connect():
            logger.error("Cannot connect to CARLA")
            return
        
        client.load_map("Town05")
        client.setup_synchronous_mode()
        
        camera_manager = CameraManager(client.world)
        camera = camera_manager.create_camera(
            camera_id="calibration_cam",
            position=(0, 0, 25),
            rotation=(-90, 0, 0),
            width=1920,
            height=1080
        )
        
        logger.info("Capturing image...")
        for _ in range(5):
            client.tick()
        
        self.image = camera_manager.get_latest_image("calibration_cam", timeout=2.0)
        
        camera_manager.cleanup()
        client.cleanup()
        
        if self.image is None:
            logger.error("Failed to capture image")
            return
        
        logger.success("Image captured!")
        self.run_calibration()
    
    def calibrate_from_file(self, image_path: str):
        """Calibrate from saved image"""
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            print(f"Error: Cannot load image from {image_path}")
            return
        
        print(f"Loaded image: {image_path}")
        self.run_calibration()
    
    def run_calibration(self):
        """Run interactive calibration"""
        print("\n" + "=" * 60)
        print("ROI Calibration Tool")
        print("=" * 60)
        print("\nInstructions:")
        print("1. Click 4 corners of each lane ROI (top-left, top-right, bottom-right, bottom-left)")
        print("2. After 4 clicks, the ROI is saved automatically")
        print("3. Repeat for all 8 lanes")
        print("4. Press 'q' to quit, 'r' to reset current lane")
        print("\n")
        
        cv2.namedWindow("ROI Calibration")
        cv2.setMouseCallback("ROI Calibration", self.mouse_callback)
        
        while True:
            display_image = self.draw_rois(self.image)
            cv2.imshow("ROI Calibration", display_image)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.current_roi = []
                print("Current ROI reset")
            
            if self.current_lane >= self.num_lanes:
                print("\nAll lanes defined! Press 'q' to exit.")
        
        cv2.destroyAllWindows()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ROI Calibration Tool")
    parser.add_argument("--image", help="Path to image file (if not using CARLA)")
    parser.add_argument("--carla", action="store_true", help="Get image from CARLA")
    
    args = parser.parse_args()
    
    calibrator = ROICalibrator()
    
    if args.image:
        calibrator.calibrate_from_file(args.image)
    elif args.carla:
        calibrator.calibrate_from_carla()
    else:
        print("Usage:")
        print("  From CARLA: python roi_calibration.py --carla")
        print("  From file:  python roi_calibration.py --image path/to/image.jpg")


if __name__ == "__main__":
    main()
