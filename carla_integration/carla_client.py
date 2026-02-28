"""
CARLA Client - Manages connection to CARLA simulator
"""

import carla
import random
import time
from typing import Optional, List
from loguru import logger


class CarlaClient:
    """Manages connection and basic operations with CARLA simulator"""
    
    def __init__(self, host: str = 'localhost', port: int = 2000, timeout: float = 10.0):
        """
        Initialize CARLA client
        
        Args:
            host: CARLA server host
            port: CARLA server port
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client: Optional[carla.Client] = None
        self.world: Optional[carla.World] = None
        self.traffic_manager: Optional[carla.TrafficManager] = None
        self.vehicles: List[carla.Actor] = []
        self.sensors: List[carla.Actor] = []
        
    def connect(self) -> bool:
        """
        Connect to CARLA server
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to CARLA at {self.host}:{self.port}...")
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(self.timeout)
            
            # Test connection
            version = self.client.get_server_version()
            logger.success(f"Connected to CARLA {version}")
            
            self.world = self.client.get_world()
            self.traffic_manager = self.client.get_trafficmanager()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to CARLA: {e}")
            return False
    
    def load_map(self, map_name: str = "Town05") -> bool:
        """
        Load a specific CARLA map
        
        Args:
            map_name: Name of the map to load
            
        Returns:
            True if map loaded successfully
        """
        try:
            logger.info(f"Loading map: {map_name}")
            self.world = self.client.load_world(map_name)
            logger.success(f"Map {map_name} loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load map {map_name}: {e}")
            return False
    
    def setup_synchronous_mode(self, fixed_delta_seconds: float = 0.05):
        """
        Enable synchronous mode for deterministic simulation
        
        Args:
            fixed_delta_seconds: Fixed time step (0.05 = 20 FPS)
        """
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = fixed_delta_seconds
        self.world.apply_settings(settings)
        self.traffic_manager.set_synchronous_mode(True)
        logger.info(f"Synchronous mode enabled: {1/fixed_delta_seconds:.0f} FPS")
    
    def spawn_vehicles(self, num_vehicles: int = 50, autopilot: bool = True) -> int:
        """
        Spawn vehicles in the world
        
        Args:
            num_vehicles: Number of vehicles to spawn
            autopilot: Enable autopilot for vehicles
            
        Returns:
            Number of successfully spawned vehicles
        """
        try:
            blueprint_library = self.world.get_blueprint_library()
            vehicle_blueprints = blueprint_library.filter('vehicle.*')
            
            spawn_points = self.world.get_map().get_spawn_points()
            random.shuffle(spawn_points)
            
            spawned = 0
            for i in range(min(num_vehicles, len(spawn_points))):
                blueprint = random.choice(vehicle_blueprints)
                
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                
                vehicle = self.world.try_spawn_actor(blueprint, spawn_points[i])
                
                if vehicle is not None:
                    if autopilot:
                        vehicle.set_autopilot(True, self.traffic_manager.get_port())
                    self.vehicles.append(vehicle)
                    spawned += 1
            
            logger.success(f"Spawned {spawned} vehicles")
            return spawned
            
        except Exception as e:
            logger.error(f"Error spawning vehicles: {e}")
            return 0
    
    def tick(self, timeout: float = 2.0) -> int:
        """
        Advance simulation by one tick (synchronous mode)
        
        Args:
            timeout: Timeout for tick
            
        Returns:
            Frame ID
        """
        if self.world:
            return self.world.tick(timeout)
        return -1
    
    def get_traffic_lights(self) -> List[carla.TrafficLight]:
        """
        Get all traffic lights in the world
        
        Returns:
            List of traffic light actors
        """
        return [actor for actor in self.world.get_actors() if 'traffic.traffic_light' in actor.type_id]
    
    def set_weather(self, cloudiness: float = 10.0, precipitation: float = 0.0, 
                    sun_altitude_angle: float = 45.0):
        """
        Set weather conditions
        
        Args:
            cloudiness: Cloud coverage (0-100)
            precipitation: Rain intensity (0-100)
            sun_altitude_angle: Sun angle (-90 to 90)
        """
        weather = carla.WeatherParameters(
            cloudiness=cloudiness,
            precipitation=precipitation,
            sun_altitude_angle=sun_altitude_angle
        )
        self.world.set_weather(weather)
        logger.info("Weather updated")
    
    def cleanup(self):
        """Clean up all spawned actors"""
        logger.info("Cleaning up CARLA actors...")
        
        for sensor in self.sensors:
            if sensor.is_alive:
                sensor.destroy()
        
        for vehicle in self.vehicles:
            if vehicle.is_alive:
                vehicle.destroy()
        
        self.sensors.clear()
        self.vehicles.clear()
        
        logger.success("Cleanup complete")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


if __name__ == "__main__":
    # Test connection
    client = CarlaClient()
    if client.connect():
        client.load_map("Town05")
        client.setup_synchronous_mode()
        client.set_weather()
        client.spawn_vehicles(30)
        
        print("Running for 100 frames...")
        for i in range(100):
            frame = client.tick()
            if i % 20 == 0:
                print(f"Frame {frame}")
        
        client.cleanup()
