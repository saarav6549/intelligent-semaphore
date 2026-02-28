"""
Camera Manager - Sets up and manages cameras in CARLA
"""

import carla
import numpy as np
import queue
from typing import Optional, Callable, Dict
from loguru import logger


class CameraManager:
    """Manages camera sensors in CARLA"""
    
    def __init__(self, world: carla.World):
        """
        Initialize camera manager
        
        Args:
            world: CARLA world instance
        """
        self.world = world
        self.cameras: Dict[str, carla.Actor] = {}
        self.image_queues: Dict[str, queue.Queue] = {}
        self.latest_images: Dict[str, np.ndarray] = {}
        
    def create_camera(
        self,
        camera_id: str,
        position: tuple = (0.0, 0.0, 25.0),
        rotation: tuple = (-90.0, 0.0, 0.0),
        width: int = 1920,
        height: int = 1080,
        fov: float = 90.0,
        attach_to: Optional[carla.Actor] = None
    ) -> carla.Actor:
        """
        Create a camera sensor
        
        Args:
            camera_id: Unique identifier for this camera
            position: (x, y, z) position in meters
            rotation: (pitch, yaw, roll) in degrees
            width: Image width in pixels
            height: Image height in pixels
            fov: Field of view in degrees
            attach_to: Actor to attach camera to (None for world position)
            
        Returns:
            Camera actor
        """
        try:
            blueprint_library = self.world.get_blueprint_library()
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            
            camera_bp.set_attribute('image_size_x', str(width))
            camera_bp.set_attribute('image_size_y', str(height))
            camera_bp.set_attribute('fov', str(fov))
            
            transform = carla.Transform(
                carla.Location(x=position[0], y=position[1], z=position[2]),
                carla.Rotation(pitch=rotation[0], yaw=rotation[1], roll=rotation[2])
            )
            
            if attach_to:
                camera = self.world.spawn_actor(camera_bp, transform, attach_to=attach_to)
            else:
                camera = self.world.spawn_actor(camera_bp, transform)
            
            self.image_queues[camera_id] = queue.Queue()
            camera.listen(lambda image: self._on_image_received(camera_id, image))
            
            self.cameras[camera_id] = camera
            logger.success(f"Camera '{camera_id}' created at {position}")
            
            return camera
            
        except Exception as e:
            logger.error(f"Failed to create camera '{camera_id}': {e}")
            raise
    
    def _on_image_received(self, camera_id: str, carla_image: carla.Image):
        """
        Callback when camera receives new image
        
        Args:
            camera_id: Camera identifier
            carla_image: CARLA image data
        """
        image_array = np.frombuffer(carla_image.raw_data, dtype=np.uint8)
        image_array = image_array.reshape((carla_image.height, carla_image.width, 4))
        image_array = image_array[:, :, :3]  # Remove alpha channel (BGRA -> BGR)
        
        self.latest_images[camera_id] = image_array
        
        if self.image_queues[camera_id].qsize() < 2:
            self.image_queues[camera_id].put(image_array)
    
    def get_latest_image(self, camera_id: str, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get the latest image from a camera
        
        Args:
            camera_id: Camera identifier
            timeout: Timeout in seconds
            
        Returns:
            Image as numpy array (H, W, 3) or None if timeout
        """
        try:
            if camera_id in self.latest_images:
                return self.latest_images[camera_id]
            
            image = self.image_queues[camera_id].get(timeout=timeout)
            return image
        except queue.Empty:
            logger.warning(f"Timeout waiting for image from camera '{camera_id}'")
            return None
    
    def create_intersection_camera(self, camera_config: dict) -> carla.Actor:
        """
        Create camera from intersection config
        
        Args:
            camera_config: Camera configuration dictionary
            
        Returns:
            Camera actor
        """
        return self.create_camera(
            camera_id=camera_config['name'],
            position=(
                camera_config['position']['x'],
                camera_config['position']['y'],
                camera_config['position']['z']
            ),
            rotation=(
                camera_config['rotation']['pitch'],
                camera_config['rotation']['yaw'],
                camera_config['rotation']['roll']
            ),
            width=camera_config['resolution']['width'],
            height=camera_config['resolution']['height'],
            fov=camera_config['fov']
        )
    
    def destroy_camera(self, camera_id: str):
        """Destroy a specific camera"""
        if camera_id in self.cameras:
            if self.cameras[camera_id].is_alive:
                self.cameras[camera_id].destroy()
            del self.cameras[camera_id]
            del self.image_queues[camera_id]
            if camera_id in self.latest_images:
                del self.latest_images[camera_id]
            logger.info(f"Camera '{camera_id}' destroyed")
    
    def cleanup(self):
        """Destroy all cameras"""
        camera_ids = list(self.cameras.keys())
        for camera_id in camera_ids:
            self.destroy_camera(camera_id)
        logger.info("All cameras destroyed")


if __name__ == "__main__":
    # Test camera setup
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    
    camera_manager = CameraManager(world)
    
    camera = camera_manager.create_camera(
        camera_id="test_cam",
        position=(0, 0, 30),
        rotation=(-90, 0, 0)
    )
    
    print("Camera created. Getting 10 images...")
    world.tick()
    
    for i in range(10):
        world.tick()
        image = camera_manager.get_latest_image("test_cam")
        if image is not None:
            print(f"Frame {i}: Image shape {image.shape}")
    
    camera_manager.cleanup()
