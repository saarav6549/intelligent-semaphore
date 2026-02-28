"""
Test API endpoints
"""

import sys
import requests
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


def test_api(base_url: str = "http://localhost:8000"):
    """Test all API endpoints"""
    logger.info(f"Testing API at {base_url}...")
    
    tests_passed = 0
    tests_total = 0
    
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.success("✓ Health endpoint works")
            tests_passed += 1
        else:
            logger.error(f"✗ Health endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Health endpoint failed: {e}")
    
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            logger.success(f"✓ Config endpoint works (lanes: {config['num_lanes']})")
            tests_passed += 1
        else:
            logger.error(f"✗ Config endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Config endpoint failed: {e}")
    
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/observation", timeout=10)
        if response.status_code == 200:
            obs = response.json()
            logger.success(f"✓ Observation endpoint works (vehicles: {sum(obs['raw_counts'])})")
            tests_passed += 1
        else:
            logger.error(f"✗ Observation endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Observation endpoint failed: {e}")
    
    tests_total += 1
    try:
        action = {"action": 2, "duration": 5.0}
        response = requests.post(f"{base_url}/action", json=action, timeout=5)
        if response.status_code == 200:
            result = response.json()
            logger.success(f"✓ Action endpoint works (phase: {result['phase_name']})")
            tests_passed += 1
        else:
            logger.error(f"✗ Action endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ Action endpoint failed: {e}")
    
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/state", timeout=5)
        if response.status_code == 200:
            logger.success("✓ State endpoint works")
            tests_passed += 1
        else:
            logger.error(f"✗ State endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"✗ State endpoint failed: {e}")
    
    logger.info(f"\nResults: {tests_passed}/{tests_total} tests passed")
    
    return tests_passed == tests_total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    
    success = test_api(args.url)
    sys.exit(0 if success else 1)
