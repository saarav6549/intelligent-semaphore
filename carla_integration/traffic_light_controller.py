"""
Traffic Light Controller - Controls traffic light phases in CARLA
"""

import carla
from typing import List, Dict, Optional
from loguru import logger


class TrafficLightController:
    """Controls traffic lights at an intersection"""
    
    def __init__(self, world: carla.World, intersection_location: carla.Location = None):
        """
        Initialize traffic light controller
        
        Args:
            world: CARLA world instance
            intersection_location: Center of intersection (optional, will find closest)
        """
        self.world = world
        self.intersection_location = intersection_location or carla.Location(0, 0, 0)
        self.traffic_lights: List[carla.TrafficLight] = []
        self.current_phase: int = 0
        
    def find_intersection_lights(self, radius: float = 50.0) -> int:
        """
        Find all traffic lights near the intersection
        
        Args:
            radius: Search radius in meters
            
        Returns:
            Number of traffic lights found
        """
        all_actors = self.world.get_actors()
        traffic_lights = all_actors.filter('traffic.traffic_light*')
        
        self.traffic_lights = []
        for light in traffic_lights:
            distance = light.get_location().distance(self.intersection_location)
            if distance <= radius:
                self.traffic_lights.append(light)
        
        logger.info(f"Found {len(self.traffic_lights)} traffic lights near intersection")
        return len(self.traffic_lights)
    
    def set_phase(self, phase_id: int, phase_config: Dict):
        """
        Set traffic light phase based on configuration
        
        Args:
            phase_id: Phase identifier
            phase_config: Phase configuration with green_lanes
        """
        if not self.traffic_lights:
            logger.warning("No traffic lights found. Call find_intersection_lights() first.")
            return
        
        self.current_phase = phase_id
        green_lanes = phase_config.get('green_lanes', [])
        
        logger.info(f"Setting phase {phase_id}: {phase_config['name']}")
        
        for idx, light in enumerate(self.traffic_lights):
            if idx in green_lanes:
                light.set_state(carla.TrafficLightState.Green)
            else:
                light.set_state(carla.TrafficLightState.Red)
        
        duration = phase_config.get('duration', 30)
        light.set_green_time(duration)
    
    def set_all_red(self):
        """Set all traffic lights to red"""
        for light in self.traffic_lights:
            light.set_state(carla.TrafficLightState.Red)
        logger.info("All lights set to RED")
    
    def set_all_green(self):
        """Set all traffic lights to green"""
        for light in self.traffic_lights:
            light.set_state(carla.TrafficLightState.Green)
        logger.info("All lights set to GREEN")
    
    def freeze_lights(self):
        """Freeze traffic lights (prevent automatic cycling)"""
        for light in self.traffic_lights:
            light.freeze(True)
        logger.info("Traffic lights frozen")
    
    def unfreeze_lights(self):
        """Unfreeze traffic lights"""
        for light in self.traffic_lights:
            light.freeze(False)
        logger.info("Traffic lights unfrozen")
    
    def get_light_states(self) -> List[str]:
        """
        Get current state of all lights
        
        Returns:
            List of states as strings
        """
        states = []
        for light in self.traffic_lights:
            state = light.get_state()
            if state == carla.TrafficLightState.Red:
                states.append("Red")
            elif state == carla.TrafficLightState.Yellow:
                states.append("Yellow")
            elif state == carla.TrafficLightState.Green:
                states.append("Green")
            else:
                states.append("Unknown")
        return states


if __name__ == "__main__":
    # Test traffic light control
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    
    controller = TrafficLightController(world)
    num_lights = controller.find_intersection_lights()
    
    if num_lights > 0:
        print(f"Found {num_lights} traffic lights")
        controller.freeze_lights()
        controller.set_all_red()
        print("All lights are now RED")
        
        import time
        time.sleep(2)
        
        controller.set_all_green()
        print("All lights are now GREEN")
