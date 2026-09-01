"""
Pydantic request/response schemas.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class CameraBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    stream_url: Optional[str] = None
    intersection_id: Optional[str] = None


class CameraCreate(CameraBase):
    pass


class CameraOut(CameraBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_active: bool
    created_at: datetime


class VehicleCountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    camera_id: str
    timestamp: datetime
    vehicle_class: str
    count: int
    avg_speed_kmh: Optional[float] = None


class VehicleCountIngest(BaseModel):
    camera_id: str
    vehicle_class: str = "car"
    count: int
    avg_speed_kmh: Optional[float] = None
    timestamp: Optional[datetime] = None


class CongestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    camera_id: str
    timestamp: datetime
    level: str
    density: float
    avg_speed_kmh: Optional[float] = None


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    camera_id: str
    generated_at: datetime
    target_timestamp: datetime
    predicted_count: float
    predicted_level: str
    confidence: float


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    camera_id: str
    incident_type: str
    detected_at: datetime
    confidence: float
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolved: bool


class IncidentCreate(BaseModel):
    camera_id: str
    incident_type: str
    confidence: float = 0.0
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata_json: Optional[dict[str, Any]] = None


class SignalTimingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    intersection_id: str
    generated_at: datetime
    phase_plan: dict
    reason: Optional[str] = None
    applied: bool


class MapStateOut(BaseModel):
    """Aggregated live state for the frontend map."""
    cameras: list[dict]
    incidents: list[dict]
    congestion: list[dict]
