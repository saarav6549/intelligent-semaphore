"""
CARLA Integration Module
Handles connection to CARLA simulator, camera setup, and traffic control
"""

from .carla_client import CarlaClient
from .camera_setup import CameraManager
from .traffic_light_controller import TrafficLightController

__all__ = ['CarlaClient', 'CameraManager', 'TrafficLightController']
