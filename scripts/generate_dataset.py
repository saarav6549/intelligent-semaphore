"""
Generate YOLO training dataset from CARLA
Run this script to collect images with vehicle annotations
"""

import sys
import time
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import config
from carla_integration import CarlaClient, CameraManager
from yolo_detection import DatasetGenerator
from loguru import logger


def generate_dataset(
    num_frames: int = 1000,
    num_vehicles: int = 50,
    output_dir: str = "./datasets/carla_vehicles"
):
    """
    Generate dataset from CARLA
    
    Args:
        num_frames: Number of frames to collect
        num_vehicles: Number of vehicles to spawn
        output_dir: Output directory for dataset
    """
    logger.info(f"Starting dataset generation: {num_frames} frames")
    
    client = CarlaClient(
        host=config.carla['carla']['host'],
        port=config.carla['carla']['port']
    )
    
    if not client.connect():
        logger.error("Failed to connect to CARLA")
        return
    
    try:
        client.load_map(config.carla['carla']['map_name'])
        client.setup_synchronous_mode(fixed_delta_seconds=0.1)
        client.set_weather()
        
        camera_manager = CameraManager(client.world)
        cam_config = config.intersection['intersection']['cameras'][0]
        camera = camera_manager.create_intersection_camera(cam_config)
        
        logger.info(f"Spawning {num_vehicles} vehicles...")
        spawned = client.spawn_vehicles(num_vehicles, autopilot=True)
        logger.success(f"Spawned {spawned} vehicles")
        
        dataset_gen = DatasetGenerator(output_dir)
        
        logger.info("Collecting frames...")
        for frame_idx in range(num_frames):
            client.tick()
            
            image = camera_manager.get_latest_image(cam_config['name'], timeout=2.0)
            
            if image is not None:
                vehicles = [v for v in client.world.get_actors() if 'vehicle' in v.type_id]
                
                camera_transform = camera.get_transform()
                
                dataset_gen.save_frame(
                    image=image,
                    vehicles_in_view=vehicles,
                    camera_transform=camera_transform,
                    camera_fov=cam_config['fov'],
                    image_width=cam_config['resolution']['width'],
                    image_height=cam_config['resolution']['height']
                )
            
            if (frame_idx + 1) % 100 == 0:
                logger.info(f"Progress: {frame_idx + 1}/{num_frames} frames")
        
        dataset_gen.create_data_yaml()
        
        logger.success(f"Dataset generation complete! Saved to {output_dir}")
        logger.info("Next step: Run training with 'python yolo_detection/train_yolo.py'")
        
    except Exception as e:
        logger.error(f"Error during dataset generation: {e}")
        
    finally:
        camera_manager.cleanup()
        client.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate YOLO dataset from CARLA")
    parser.add_argument("--frames", type=int, default=1000, help="Number of frames to collect")
    parser.add_argument("--vehicles", type=int, default=50, help="Number of vehicles to spawn")
    parser.add_argument("--output", default="./datasets/carla_vehicles", help="Output directory")
    
    args = parser.parse_args()
    
    generate_dataset(
        num_frames=args.frames,
        num_vehicles=args.vehicles,
        output_dir=args.output
    )
