"""
FastAPI Server - REST API for Team B's sensing system
This is THE interface that Team A will use to communicate with your system
"""

import sys
import time
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from loguru import logger
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import carla
from config import config
from carla_integration import CarlaClient, CameraManager, TrafficLightController
from yolo_detection import VehicleDetector, ROIMapper
from sensing_pipeline import VehicleCounter, ObservationBuilder, StateManager
from api.schemas import (
    ObservationResponse, ActionRequest, StateResponse,
    HealthResponse, MetricsResponse, ConfigResponse,
    CameraPositionRequest
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
            port=config.carla['carla']['port'],
            timeout=config.carla['carla'].get('timeout', 10.0)
        )
        
        if not system.carla_client.connect():
            logger.error("Failed to connect to CARLA")
            return
        
        system.carla_client.load_map(config.carla['carla']['map_name'])
        if config.carla['carla'].get('synchronous_mode', True):
            system.carla_client.setup_synchronous_mode(
                config.carla['carla'].get('fixed_delta_seconds', 0.05)
            )
        
        weather = config.carla['carla']['weather']
        system.carla_client.set_weather(
            cloudiness=weather['cloudiness'],
            precipitation=weather['precipitation'],
            sun_altitude_angle=weather['sun_altitude_angle']
        )
        
        logger.info("Setting up traffic light controller...")
        system.traffic_controller = TrafficLightController(system.carla_client.world)
        num_lights = system.traffic_controller.find_intersection_lights()
        cam_position = None
        if num_lights == 0:
            center = system.traffic_controller.get_intersection_center(height=25.0)
            if center is not None:
                cam_position = (center[0], center[1], center[2])
                logger.info(f"Will spawn camera at intersection ({center[0]:.1f}, {center[1]:.1f})")
                system.traffic_controller.intersection_location = carla.Location(
                    center[0], center[1], center[2]
                )
                system.traffic_controller.find_intersection_lights(radius=50.0)
        
        logger.info("Setting up cameras...")
        system.camera_manager = CameraManager(system.carla_client.world)
        for cam_config in config.intersection['intersection']['cameras']:
            cfg = dict(cam_config)
            if cam_position is not None and cfg.get('name') == 'intersection_overhead':
                cfg = dict(cfg)
                cfg['position'] = {'x': cam_position[0], 'y': cam_position[1], 'z': cam_position[2]}
            system.camera_manager.create_intersection_camera(cfg)
        
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


@app.get("/camera/position", tags=["Visualization"])
async def get_camera_position():
    """Get current overhead camera position (x, y, z)."""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    pos = system.camera_manager.get_camera_position("intersection_overhead")
    if pos is None:
        raise HTTPException(status_code=500, detail="Camera not found")
    return {"x": pos[0], "y": pos[1], "z": pos[2]}


@app.patch("/camera/position", tags=["Visualization"])
async def set_camera_position(req: CameraPositionRequest):
    """Set overhead camera position (dynamic control)."""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    try:
        system.camera_manager.set_camera_position(
            "intersection_overhead", req.x, req.y, req.z
        )
        return {"status": "success", "x": req.x, "y": req.y, "z": req.z}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/camera/move-to-intersection", tags=["Visualization"])
async def move_camera_to_intersection():
    """Move overhead camera to center of traffic light intersection."""
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    center = system.traffic_controller.get_intersection_center(height=25.0)
    if center is None:
        raise HTTPException(
            status_code=404,
            detail="No traffic lights found - cannot determine intersection"
        )
    try:
        system.traffic_controller.intersection_location = carla.Location(
            center[0], center[1], center[2]
        )
        system.traffic_controller.find_intersection_lights(radius=50.0)
        system.camera_manager.set_camera_position(
            "intersection_overhead", center[0], center[1], center[2]
        )
        return {
            "status": "success",
            "x": center[0], "y": center[1], "z": center[2],
            "traffic_lights_found": len(system.traffic_controller.traffic_lights)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/camera", response_class=HTMLResponse, tags=["Visualization"])
async def camera_dashboard():
    """Camera dashboard with stream and controls."""
    return """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מצלמת צומת - Intelligent Traffic</title>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 16px; font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
        h1 { margin: 0 0 16px; font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 0 auto; }
        .stream-wrap { position: relative; background: #000; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }
        .stream-wrap img { display: block; width: 100%; max-height: 80vh; object-fit: contain; }
        .controls { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
        .btn {
            padding: 12px 24px; font-size: 1rem; font-weight: 600; border: none; border-radius: 8px;
            cursor: pointer; transition: all 0.2s;
        }
        .btn-primary { background: #4ade80; color: #0f172a; }
        .btn-primary:hover { background: #22c55e; transform: translateY(-1px); }
        .btn-primary:disabled { background: #64748b; cursor: not-allowed; transform: none; }
        .status { padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; }
        .status.ok { background: #166534; color: #bbf7d0; }
        .status.err { background: #991b1b; color: #fecaca; }
    </style>
</head>
<body>
    <div class="container">
        <h1>מצלמת צומת</h1>
        <div class="stream-wrap">
            <img src="/camera/stream" alt="Camera stream" id="stream">
        </div>
        <div class="controls">
            <button class="btn btn-primary" id="moveBtn" onclick="moveToIntersection()">
                הזז מצלמה לצומת מרומזר
            </button>
            <span class="status" id="status"></span>
        </div>
    </div>
    <script>
        const base = window.location.origin;
        async function moveToIntersection() {
            const btn = document.getElementById('moveBtn');
            const status = document.getElementById('status');
            btn.disabled = true;
            status.textContent = 'מעביר...';
            status.className = 'status';
            try {
                const r = await fetch(base + '/camera/move-to-intersection', { method: 'POST' });
                const j = await r.json();
                if (r.ok) {
                    status.textContent = 'המצלמה הוזזה לצומת';
                    status.className = 'status ok';
                } else {
                    status.textContent = j.detail || 'שגיאה';
                    status.className = 'status err';
                }
            } catch (e) {
                status.textContent = 'שגיאת רשת';
                status.className = 'status err';
            }
            btn.disabled = false;
        }
    </script>
</body>
</html>
"""


@app.get("/camera/stream", tags=["Visualization"])
async def camera_stream():
    """
    Stream camera feed with detections, ROIs, and camera position (x,y,z) overlay.
    Returns MJPEG stream.
    """
    if not system.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    async def generate():
        while True:
            try:
                system.carla_client.tick()
                image = system.camera_manager.get_latest_image("intersection_overhead", timeout=1.0)
                
                if image is not None:
                    # Lower confidence (0.2) for stream - overhead view needs lower threshold
                    detections, annotated = system.detector.detect(
                        image, visualize=True, conf_override=0.2
                    )
                    at_intersection = len(system.traffic_controller.traffic_lights) > 0
                    vis_image = system.roi_mapper.visualize_rois(
                        annotated, detections, show_rois=at_intersection
                    )
                    
                    # Overlay camera position (x, y, z) below YOLO label
                    pos = system.camera_manager.get_camera_position("intersection_overhead")
                    if pos is not None:
                        text = f"Camera: x={pos[0]:.1f}  y={pos[1]:.1f}  z={pos[2]:.1f}"
                        cv2.putText(
                            vis_image, text, (10, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2, cv2.LINE_AA
                        )
                    # Hint when not at intersection
                    if not at_intersection:
                        hint = "Open /camera -> Click 'Move to intersection'"
                        cv2.putText(
                            vis_image, hint, (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2, cv2.LINE_AA
                        )
                    
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
