"""
FastAPI Server - REST API for Team B's sensing system
This is THE interface that Team A will use to communicate with your system
"""

import sys
import time
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import config
from carla_integration import CarlaClient, CameraManager, TrafficLightController
from yolo_detection import VehicleDetector, ROIMapper
from sensing_pipeline import VehicleCounter, ObservationBuilder, StateManager
from api.schemas import (
    ObservationResponse, ActionRequest, StateResponse,
    HealthResponse, MetricsResponse, ConfigResponse
)


app = FastAPI(
    title="Intelligent Traffic Light - Team B API",
    description="Vision and sensing system for traffic light optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SystemState:
    """Global system state"""
    def __init__(self):
        self.carla_client: Optional[CarlaClient] = None
        self.camera_manager: Optional[CameraManager] = None
        self.traffic_controller: Optional[TrafficLightController] = None
        self.detector: Optional[VehicleDetector] = None
        self.roi_mapper: Optional[ROIMapper] = None
        self.vehicle_counter: Optional[VehicleCounter] = None
        self.obs_builder: Optional[ObservationBuilder] = None
        self.state_manager: Optional[StateManager] = None
        self.initialized = False
        self.start_time = time.time()


system = SystemState()


@app.on_event("startup")
async def startup_event():
    """Initialize all systems on startup"""
    logger.info("Starting API server...")
    
    try:
        logger.info("Initializing CARLA client...")
        system.carla_client = CarlaClient(
            host=config.carla['carla']['host'],
            port=config.carla['carla']['port']
        )
        
        if not system.carla_client.connect():
            logger.error("Failed to connect to CARLA")
            return
        
        system.carla_client.load_map(config.carla['carla']['map_name'])
        system.carla_client.setup_synchronous_mode(
            config.carla['carla']['synchronous_mode']
        )
        
        weather = config.carla['carla']['weather']
        system.carla_client.set_weather(
            cloudiness=weather['cloudiness'],
            precipitation=weather['precipitation'],
            sun_altitude_angle=weather['sun_altitude_angle']
        )
        
        logger.info("Setting up cameras...")
        system.camera_manager = CameraManager(system.carla_client.world)
        
        for cam_config in config.intersection['intersection']['cameras']:
            system.camera_manager.create_intersection_camera(cam_config)
        
        logger.info("Setting up traffic light controller...")
        system.traffic_controller = TrafficLightController(system.carla_client.world)
        system.traffic_controller.find_intersection_lights()
        system.traffic_controller.freeze_lights()
        
        logger.info("Spawning vehicles...")
        num_vehicles = config.carla['carla']['traffic']['num_vehicles']
        system.carla_client.spawn_vehicles(num_vehicles)
        
        logger.info("Initializing YOLO detector...")
        system.detector = VehicleDetector(
            model_path=config.yolo['yolo']['weights'],
            confidence_threshold=config.yolo['yolo']['detection']['confidence_threshold'],
            iou_threshold=config.yolo['yolo']['detection']['iou_threshold'],
            target_classes=config.yolo['yolo']['detection']['target_classes'],
            device=config.yolo['yolo']['device']
        )
        
        logger.info("Initializing ROI mapper...")
        lanes = config.intersection['intersection']['lanes']
        system.roi_mapper = ROIMapper(lanes)
        
        logger.info("Initializing sensing pipeline...")
        system.vehicle_counter = VehicleCounter(config.num_lanes)
        system.obs_builder = ObservationBuilder(config.num_lanes)
        system.state_manager = StateManager(config.num_lanes, config.num_phases)
        
        system.initialized = True
        logger.success("All systems initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize systems: {e}")
        system.initialized = False


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    
    if system.camera_manager:
        system.camera_manager.cleanup()
    
    if system.carla_client:
        system.carla_client.cleanup()


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "service": "Intelligent Traffic Light - Team B",
        "status": "running",
        "description": "Vision and sensing system",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if system.initialized else "initializing",
        carla_connected=system.carla_client is not None,
        yolo_loaded=system.detector is not None,
        num_lanes=config.num_lanes,
        num_phases=config.num_phases,
        uptime=time.time() - system.start_time
    )


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config():
    """Get intersection configuration"""
    return ConfigResponse(
        num_lanes=config.num_lanes,
        num_phases=config.num_phases,
        observation_shape=list(config.observation_shape),
        action_space_size=config.action_space_size,
        lanes=config.intersection['intersection']['lanes'],
        phases=config.intersection['intersection']['traffic_phases']
    )


@app.get("/observation", response_model=ObservationResponse, tags=["RL Interface"])
async def get_observation():
    """
    Get current observation (vehicle counts per lane)
    This is the main endpoint Team A's PPO agent will call
    """
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        system.carla_client.tick()
        
        image = system.camera_manager.get_latest_image("intersection_overhead", timeout=2.0)
        
        if image is None:
            raise HTTPException(status_code=500, detail="Failed to get camera image")
        
        detections, _ = system.detector.detect(image, visualize=False)
        
        raw_counts = system.roi_mapper.count_vehicles_per_lane(detections)
        
        smoothed_counts = system.vehicle_counter.update(raw_counts)
        
        obs_dict = system.obs_builder.build_observation(smoothed_counts)
        
        system.state_manager.update_state(smoothed_counts, system.state_manager.current_phase)
        
        return ObservationResponse(**obs_dict)
        
    except Exception as e:
        logger.error(f"Error getting observation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/action", tags=["RL Interface"])
async def set_action(action_request: ActionRequest):
    """
    Set traffic light action (called by Team A's PPO agent)
    
    Args:
        action_request: Action to take
    """
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    phase_id = action_request.action
    duration = action_request.duration
    
    if not 0 <= phase_id < config.num_phases:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action {phase_id}, must be 0-{config.num_phases-1}"
        )
    
    try:
        phases = config.intersection['intersection']['traffic_phases']
        phase_config = phases[phase_id]
        
        system.traffic_controller.set_phase(phase_id, phase_config)
        system.state_manager.set_phase(phase_id, duration or phase_config['duration'])
        
        logger.info(f"Action executed: Phase {phase_id}")
        
        return {
            "status": "success",
            "phase_set": phase_id,
            "phase_name": phase_config['name'],
            "duration": duration or phase_config['duration']
        }
        
    except Exception as e:
        logger.error(f"Error setting action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state", response_model=StateResponse, tags=["Monitoring"])
async def get_state():
    """Get complete intersection state"""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    state_dict = system.state_manager.get_state_dict()
    return StateResponse(**state_dict)


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """Get performance metrics"""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    metrics = system.state_manager.get_metrics()
    return MetricsResponse(**metrics)


@app.get("/camera/stream", tags=["Visualization"])
async def camera_stream():
    """
    Stream camera feed with detections and ROIs
    Returns MJPEG stream
    """
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    async def generate():
        while True:
            try:
                system.carla_client.tick()
                image = system.camera_manager.get_latest_image("intersection_overhead", timeout=1.0)
                
                if image is not None:
                    detections, annotated = system.detector.detect(image, visualize=True)
                    
                    if annotated is not None:
                        vis_image = system.roi_mapper.visualize_rois(annotated, detections)
                    else:
                        vis_image = system.roi_mapper.visualize_rois(image)
                    
                    _, buffer = cv2.imencode('.jpg', vis_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Error in camera stream: {e}")
                break
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/reset", tags=["Control"])
async def reset_episode():
    """Reset episode (for training)"""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        system.vehicle_counter.reset()
        system.obs_builder.reset()
        system.state_manager.reset()
        
        system.traffic_controller.set_all_red()
        
        logger.info("Episode reset")
        
        return {"status": "success", "message": "Episode reset"}
        
    except Exception as e:
        logger.error(f"Error resetting episode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
