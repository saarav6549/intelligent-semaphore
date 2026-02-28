"""
Scenario Loader - Load and manage traffic scenarios
"""

import carla
import random
from typing import List, Dict, Optional
from loguru import logger


class ScenarioLoader:
    """Loads and manages different traffic scenarios"""
    
    def __init__(self, world: carla.World, traffic_manager: carla.TrafficManager):
        """
        Initialize scenario loader
        
        Args:
            world: CARLA world instance
            traffic_manager: CARLA traffic manager
        """
        self.world = world
        self.traffic_manager = traffic_manager
        self.blueprint_library = world.get_blueprint_library()
        self.spawn_points = world.get_map().get_spawn_points()
        
    def load_scenario(self, scenario_name: str, **kwargs) -> List[carla.Actor]:
        """
        Load a predefined scenario
        
        Args:
            scenario_name: Name of scenario to load
            
        Returns:
            List of spawned actors
        """
        scenarios = {
            'light_traffic': self._light_traffic,
            'heavy_traffic': self._heavy_traffic,
            'rush_hour': self._rush_hour,
            'mixed_traffic': self._mixed_traffic,
            'custom': self._custom_scenario
        }
        
        if scenario_name not in scenarios:
            logger.error(f"Unknown scenario: {scenario_name}")
            return []
        
        logger.info(f"Loading scenario: {scenario_name}")
        return scenarios[scenario_name](**kwargs)
    
    def _light_traffic(self, num_vehicles: int = 20) -> List[carla.Actor]:
        """Light traffic scenario"""
        return self._spawn_vehicles(
            num_vehicles=num_vehicles,
            vehicle_types=['vehicle.tesla.model3', 'vehicle.audi.a2', 'vehicle.toyota.prius'],
            speed_limit=50
        )
    
    def _heavy_traffic(self, num_vehicles: int = 80) -> List[carla.Actor]:
        """Heavy traffic scenario"""
        return self._spawn_vehicles(
            num_vehicles=num_vehicles,
            vehicle_types=None,
            speed_limit=30
        )
    
    def _rush_hour(self, num_vehicles: int = 100) -> List[carla.Actor]:
        """Rush hour scenario with aggressive drivers"""
        actors = self._spawn_vehicles(
            num_vehicles=num_vehicles,
            vehicle_types=None,
            speed_limit=40
        )
        
        for vehicle in actors:
            self.traffic_manager.distance_to_leading_vehicle(vehicle, 1.0)
            self.traffic_manager.ignore_lights_percentage(vehicle, 10)
        
        return actors
    
    def _mixed_traffic(self, num_vehicles: int = 50) -> List[carla.Actor]:
        """Mixed traffic with different vehicle types"""
        small_cars = self._spawn_vehicles(
            num_vehicles=num_vehicles // 2,
            vehicle_types=['vehicle.tesla.model3', 'vehicle.audi.a2'],
            speed_limit=50
        )
        
        large_vehicles = self._spawn_vehicles(
            num_vehicles=num_vehicles // 4,
            vehicle_types=['vehicle.carlamotors.firetruck', 'vehicle.volkswagen.t2'],
            speed_limit=40
        )
        
        motorcycles = self._spawn_vehicles(
            num_vehicles=num_vehicles // 4,
            vehicle_types=['vehicle.yamaha.yzf', 'vehicle.kawasaki.ninja'],
            speed_limit=60
        )
        
        return small_cars + large_vehicles + motorcycles
    
    def _custom_scenario(self, **kwargs) -> List[carla.Actor]:
        """Custom scenario with user-defined parameters"""
        return self._spawn_vehicles(**kwargs)
    
    def _spawn_vehicles(
        self,
        num_vehicles: int,
        vehicle_types: Optional[List[str]] = None,
        speed_limit: Optional[float] = None
    ) -> List[carla.Actor]:
        """
        Spawn vehicles
        
        Args:
            num_vehicles: Number of vehicles to spawn
            vehicle_types: List of vehicle type IDs (None = all types)
            speed_limit: Speed limit percentage (None = default)
            
        Returns:
            List of spawned vehicle actors
        """
        if vehicle_types:
            blueprints = [self.blueprint_library.find(vt) for vt in vehicle_types]
        else:
            blueprints = self.blueprint_library.filter('vehicle.*')
        
        spawn_points = random.sample(self.spawn_points, min(num_vehicles, len(self.spawn_points)))
        
        vehicles = []
        for spawn_point in spawn_points:
            blueprint = random.choice(blueprints)
            
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            
            vehicle = self.world.try_spawn_actor(blueprint, spawn_point)
            
            if vehicle is not None:
                vehicle.set_autopilot(True, self.traffic_manager.get_port())
                
                if speed_limit is not None:
                    self.traffic_manager.vehicle_percentage_speed_difference(vehicle, 100 - speed_limit)
                
                vehicles.append(vehicle)
        
        logger.success(f"Spawned {len(vehicles)} vehicles")
        return vehicles


if __name__ == "__main__":
    from carla_integration import CarlaClient
    
    client = CarlaClient()
    if client.connect():
        client.load_map("Town05")
        
        loader = ScenarioLoader(client.world, client.traffic_manager)
        
        vehicles = loader.load_scenario('rush_hour', num_vehicles=80)
        
        print(f"Spawned {len(vehicles)} vehicles")
        print("Running simulation for 10 seconds...")
        
        for i in range(200):
            client.tick()
            if i % 20 == 0:
                print(f"Frame {i}")
        
        for vehicle in vehicles:
            if vehicle.is_alive:
                vehicle.destroy()
        
        print("Cleanup complete")
