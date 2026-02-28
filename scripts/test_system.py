"""
System Test Script
Tests all components before deployment to RunPod
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import config
from carla_integration import CarlaClient, CameraManager, TrafficLightController
from yolo_detection import VehicleDetector, ROIMapper
from sensing_pipeline import VehicleCounter, ObservationBuilder
from loguru import logger


def test_carla_connection():
    """Test CARLA connection"""
    logger.info("Testing CARLA connection...")
    client = CarlaClient()
    success = client.connect()
    if success:
        logger.success("✓ CARLA connection successful")
        client.cleanup()
    else:
        logger.error("✗ CARLA connection failed")
    return success


def test_yolo_model():
    """Test YOLO model loading"""
    logger.info("Testing YOLO model...")
    try:
        import numpy as np
        detector = VehicleDetector(device="cpu")
        
        test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        detections, _ = detector.detect(test_image)
        
        logger.success(f"✓ YOLO model loaded (found {len(detections)} detections in blank image)")
        return True
    except Exception as e:
        logger.error(f"✗ YOLO model test failed: {e}")
        return False


def test_full_pipeline():
    """Test complete sensing pipeline"""
    logger.info("Testing full pipeline...")
    
    client = CarlaClient()
    if not client.connect():
        return False
    
    try:
        client.load_map(config.carla['carla']['map_name'])
        client.setup_synchronous_mode()
        client.spawn_vehicles(20)
        
        camera_manager = CameraManager(client.world)
        cam_config = config.intersection['intersection']['cameras'][0]
        camera_manager.create_intersection_camera(cam_config)
        
        detector = VehicleDetector(device="cpu")
        
        lanes = config.intersection['intersection']['lanes']
        roi_mapper = ROIMapper(lanes)
        
        vehicle_counter = VehicleCounter(config.num_lanes)
        obs_builder = ObservationBuilder(config.num_lanes)
        
        logger.info("Running pipeline for 10 frames...")
        for i in range(10):
            client.tick()
            
            image = camera_manager.get_latest_image(cam_config['name'], timeout=2.0)
            
            if image is not None:
                detections, _ = detector.detect(image)
                
                raw_counts = roi_mapper.count_vehicles_per_lane(detections)
                
                smoothed_counts = vehicle_counter.update(raw_counts)
                
                obs_dict = obs_builder.build_observation(smoothed_counts)
                
                logger.info(f"Frame {i}: Detected {len(detections)} vehicles, counts={raw_counts}")
        
        logger.success("✓ Full pipeline test successful")
        
        camera_manager.cleanup()
        client.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"✗ Pipeline test failed: {e}")
        client.cleanup()
        return False


def test_traffic_lights():
    """Test traffic light control"""
    logger.info("Testing traffic light control...")
    
    client = CarlaClient()
    if not client.connect():
        return False
    
    try:
        controller = TrafficLightController(client.world)
        num_lights = controller.find_intersection_lights()
        
        if num_lights > 0:
            controller.freeze_lights()
            controller.set_all_red()
            time.sleep(1)
            controller.set_all_green()
            logger.success(f"✓ Traffic light control successful ({num_lights} lights)")
            client.cleanup()
            return True
        else:
            logger.warning("✓ No traffic lights found (map dependent)")
            client.cleanup()
            return True
            
    except Exception as e:
        logger.error(f"✗ Traffic light test failed: {e}")
        client.cleanup()
        return False


def run_all_tests():
    """Run all system tests"""
    logger.info("=" * 50)
    logger.info("Running System Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Configuration Loading", lambda: config is not None),
        ("CARLA Connection", test_carla_connection),
        ("YOLO Model", test_yolo_model),
        ("Traffic Lights", test_traffic_lights),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            results.append((test_name, False))
        time.sleep(1)
    
    logger.info("\n" + "=" * 50)
    logger.info("Test Results Summary")
    logger.info("=" * 50)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("All tests passed! System is ready.")
    else:
        logger.warning(f"{total - passed} test(s) failed. Check errors above.")


if __name__ == "__main__":
    run_all_tests()
