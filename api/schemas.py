"""
API Data Schemas - Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ObservationResponse(BaseModel):
    """Observation sent to RL agent"""
    observation: List[float] = Field(..., description="Vehicle counts per lane (normalized)")
    frame_id: int = Field(..., description="Frame number")
    timestamp: float = Field(..., description="Unix timestamp")
    num_lanes: int = Field(..., description="Number of lanes")
    raw_counts: List[int] = Field(..., description="Raw vehicle counts (non-normalized)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "observation": [0.15, 0.25, 0.10, 0.20, 0.05, 0.0, 0.15, 0.10],
                "frame_id": 1523,
                "timestamp": 1234567890.123,
                "num_lanes": 8,
                "raw_counts": [3, 5, 2, 4, 1, 0, 3, 2]
            }
        }


class ActionRequest(BaseModel):
    """Action received from RL agent"""
    action: int = Field(..., description="Traffic light phase to set", ge=0)
    duration: Optional[float] = Field(30.0, description="Duration to keep this phase (seconds)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": 2,
                "duration": 25.0
            }
        }


class StateResponse(BaseModel):
    """Complete intersection state"""
    vehicle_counts: List[int] = Field(..., description="Current vehicle counts per lane")
    current_phase: int = Field(..., description="Current traffic light phase")
    phase_elapsed_time: float = Field(..., description="Time in current phase (seconds)")
    phase_duration: float = Field(..., description="Total duration of current phase")
    step_count: int = Field(..., description="Number of steps in episode")
    total_vehicles: int = Field(..., description="Total vehicles across all lanes")
    episode_runtime: float = Field(..., description="Episode runtime in seconds")


class HealthResponse(BaseModel):
    """API health check response"""
    status: str = Field(..., description="Service status")
    carla_connected: bool = Field(..., description="CARLA connection status")
    yolo_loaded: bool = Field(..., description="YOLO model loaded status")
    num_lanes: int = Field(..., description="Number of lanes configured")
    num_phases: int = Field(..., description="Number of traffic phases")
    uptime: float = Field(..., description="API uptime in seconds")


class MetricsResponse(BaseModel):
    """Performance metrics"""
    total_vehicles_served: int
    total_waiting_time: float
    average_waiting_time: float
    steps: int
    runtime: float


class ConfigResponse(BaseModel):
    """Configuration information"""
    num_lanes: int
    num_phases: int
    observation_shape: List[int]
    action_space_size: int
    lanes: List[Dict]
    phases: List[Dict]
