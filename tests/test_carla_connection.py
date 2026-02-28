"""
Test CARLA connection
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from carla_integration import CarlaClient
from loguru import logger


def test_connection():
    """Test basic CARLA connection"""
    logger.info("Testing CARLA connection...")
    
    client = CarlaClient()
    
    if not client.connect():
        logger.error("Failed to connect")
        return False
    
    logger.success("Connected successfully")
    
    version = client.client.get_server_version()
    logger.info(f"CARLA version: {version}")
    
    available_maps = client.client.get_available_maps()
    logger.info(f"Available maps: {len(available_maps)}")
    
    client.cleanup()
    
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
