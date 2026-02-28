"""
Main Entry Point - Run the complete vision system
Can run standalone or as part of Docker container
"""

import sys
import time
import argparse
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from config import config
from carla_integration import CarlaClient, CameraManager, TrafficLightController
from yolo_detection import VehicleDetector, ROIMapper
from sensing_pipeline import VehicleCounter, ObservationBuilder, StateManager


class VisionSystem:
    """Complete vision and sensing system"""
    
    def __init__(self):
        """Initialize all components"""
        self.carla_client = None
        self.camera_manager = None
        self.traffic_controller = None
        self.detector = None
        self.roi_mapper = None
        self.vehicle_counter = None
        self.obs_builder = None
        self.state_manager = None
        
    def initialize(self):
        """Initialize all systems"""
        logger.info("Initializing vision system...")
        
        logger.info("Connecting to CARLA...")
        self.carla_client = CarlaClient(
            host=config.carla['carla']['host'],
            port=config.carla['carla']['port']
        )
        
        if not self.carla_client.connect():
            logger.error("Failed to connect to CARLA")
            return False
        
        logger.info("Loading map...")
        self.carla_client.load_map(config.carla['carla']['map_name'])
        
        logger.info("Setting up synchronous mode...")
        self.carla_client.setup_synchronous_mode(
            fixed_delta_seconds=config.carla['carla']['fixed_delta_seconds']
        )
        
        logger.info("Setting weather...")
        weather = config.carla['carla']['weather']
        self.carla_client.set_weather(
            cloudiness=weather['cloudiness'],
            precipitation=weather['precipitation'],
            sun_altitude_angle=weather['sun_altitude_angle']
        )
        
        logger.info("Spawning vehicles...")
        num_vehicles = config.carla['carla']['traffic']['num_vehicles']
        spawned = self.carla_client.spawn_vehicles(num_vehicles)
        logger.success(f"Spawned {spawned} vehicles")
        
        logger.info("Setting up cameras...")
        self.camera_manager = CameraManager(self.carla_client.world)
        for cam_config in config.intersection['intersection']['cameras']:
            self.camera_manager.create_intersection_camera(cam_config)
        
        logger.info("Setting up traffic light controller...")
        self.traffic_controller = TrafficLightController(self.carla_client.world)
        num_lights = self.traffic_controller.find_intersection_lights()
        logger.info(f"Found {num_lights} traffic lights")
        self.traffic_controller.freeze_lights()
        
        logger.info("Loading YOLO detector...")
        self.detector = VehicleDetector(
            model_path=config.yolo['yolo']['weights'],
            confidence_threshold=config.yolo['yolo']['detection']['confidence_threshold'],
            iou_threshold=config.yolo['yolo']['detection']['iou_threshold'],
            target_classes=config.yolo['yolo']['detection']['target_classes'],
            device=config.yolo['yolo']['device']
        )
        
        logger.info("Initializing ROI mapper...")
        lanes = config.intersection['intersection']['lanes']
        self.roi_mapper = ROIMapper(lanes)
        
        logger.info("Initializing sensing pipeline...")
        self.vehicle_counter = VehicleCounter(config.num_lanes)
        self.obs_builder = ObservationBuilder(config.num_lanes)
        self.state_manager = StateManager(config.num_lanes, config.num_phases)
        
        logger.success("All systems initialized!")
        return True
    
    def run_loop(self, num_iterations: int = 100):
        """Run main processing loop"""
        logger.info(f"Starting main loop for {num_iterations} iterations...")
        
        camera_name = config.intersection['intersection']['cameras'][0]['name']
        
        for i in range(num_iterations):
            self.carla_client.tick()
            
            image = self.camera_manager.get_latest_image(camera_name, timeout=2.0)
            
            if image is None:
                logger.warning(f"Frame {i}: No image received")
                continue
            
            detections, _ = self.detector.detect(image, visualize=False)
            
            raw_counts = self.roi_mapper.count_vehicles_per_lane(detections)
            
            smoothed_counts = self.vehicle_counter.update(raw_counts)
            
            obs_dict = self.obs_builder.build_observation(smoothed_counts)
            
            self.state_manager.update_state(smoothed_counts, self.state_manager.current_phase)
            
            if i % 20 == 0:
                logger.info(
                    f"Frame {i}: {len(detections)} vehicles detected, "
                    f"counts={raw_counts.tolist()}"
                )
            
            if i % 50 == 0 and i > 0:
                phase = (i // 50) % config.num_phases
                phases = config.intersection['intersection']['traffic_phases']
                self.traffic_controller.set_phase(phase, phases[phase])
        
        logger.success("Loop complete!")
    
    def cleanup(self):
        """Cleanup all resources"""
        logger.info("Cleaning up...")
        
        if self.camera_manager:
            self.camera_manager.cleanup()
        
        if self.carla_client:
            self.carla_client.cleanup()
        
        logger.success("Cleanup complete")


def run_standalone(iterations: int = 100):
    """Run system in standalone mode (no API)"""
    system = VisionSystem()
    
    try:
        if system.initialize():
            system.run_loop(num_iterations=iterations)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        system.cleanup()


def run_with_api():
    """Run system with API server"""
    logger.info("Starting with API server...")
    logger.info("Use: uvicorn api.server:app --host 0.0.0.0 --port 8000")
    
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Intelligent Traffic Light - Team B Vision System"
    )
    
    parser.add_argument(
        "--mode",
        choices=['api', 'standalone', 'test'],
        default='api',
        help="Run mode: api (with REST API), standalone (direct loop), test (run tests)"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of iterations for standalone mode"
    )
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        run_with_api()
    elif args.mode == 'standalone':
        run_standalone(iterations=args.iterations)
    elif args.mode == 'test':
        from tests.test_system import run_all_tests
        run_all_tests()


if __name__ == "__main__":
    main()
