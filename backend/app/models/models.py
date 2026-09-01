"""
SQLAlchemy ORM models for the traffic platform.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, Boolean, JSON, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    intersection_id = Column(String, ForeignKey("intersections.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    stream_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle_counts = relationship("VehicleCount", back_populates="camera")
    incidents = relationship("Incident", back_populates="camera")


class Intersection(Base):
    __tablename__ = "intersections"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    num_approaches = Column(Integer, default=4)

    signal_timings = relationship("SignalTiming", back_populates="intersection")


class VehicleClass(str, enum.Enum):
    car = "car"
    truck = "truck"
    bus = "bus"
    motorcycle = "motorcycle"
    bicycle = "bicycle"


class VehicleCount(Base):
    """Aggregated vehicle counts per camera per time bucket (e.g. every 1 min)."""
    __tablename__ = "vehicle_counts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    camera_id = Column(UUID(as_uuid=False), ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    vehicle_class = Column(Enum(VehicleClass), default=VehicleClass.car)
    count = Column(Integer, default=0)
    avg_speed_kmh = Column(Float, nullable=True)

    camera = relationship("Camera", back_populates="vehicle_counts")


class CongestionLevel(str, enum.Enum):
    free_flow = "free_flow"
    moderate = "moderate"
    heavy = "heavy"
    gridlock = "gridlock"


class CongestionSnapshot(Base):
    """Point-in-time congestion estimate for a camera/road segment."""
    __tablename__ = "congestion_snapshots"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    camera_id = Column(UUID(as_uuid=False), ForeignKey("cameras.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(Enum(CongestionLevel), default=CongestionLevel.free_flow)
    density = Column(Float, default=0.0)  # vehicles per 100m of lane
    avg_speed_kmh = Column(Float, nullable=True)


class TrafficPrediction(Base):
    """15-30 minute ahead forecast for a camera/segment."""
    __tablename__ = "traffic_predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    camera_id = Column(UUID(as_uuid=False), ForeignKey("cameras.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    target_timestamp = Column(DateTime, nullable=False)
    predicted_count = Column(Float, nullable=False)
    predicted_level = Column(Enum(CongestionLevel), default=CongestionLevel.free_flow)
    confidence = Column(Float, default=0.0)


class IncidentType(str, enum.Enum):
    accident = "accident"
    stalled_vehicle = "stalled_vehicle"
    wrong_way = "wrong_way"
    pedestrian_hazard = "pedestrian_hazard"
    debris = "debris"
    abnormal_stop = "abnormal_stop"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    camera_id = Column(UUID(as_uuid=False), ForeignKey("cameras.id"), nullable=False)
    incident_type = Column(Enum(IncidentType), nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    confidence = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    camera = relationship("Camera", back_populates="incidents")


class SignalTiming(Base):
    """Recommended (or applied) signal-phase timing for an intersection."""
    __tablename__ = "signal_timings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    intersection_id = Column(String, ForeignKey("intersections.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    phase_plan = Column(JSON, nullable=False)  # e.g. {"NS_green": 35, "EW_green": 25, "cycle": 60}
    reason = Column(String, nullable=True)
    applied = Column(Boolean, default=False)

    intersection = relationship("Intersection", back_populates="signal_timings")
