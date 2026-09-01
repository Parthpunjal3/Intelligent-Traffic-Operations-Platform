from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/state", response_model=schemas.MapStateOut)
def map_state(db: Session = Depends(get_db)):
    """Single aggregated endpoint the frontend polls (or subscribes to via WS) to draw the live map."""
    cameras = db.query(models.Camera).filter(models.Camera.is_active == True).all()  # noqa: E712

    congestion_rows = (
        db.query(models.CongestionSnapshot)
        .order_by(models.CongestionSnapshot.camera_id, models.CongestionSnapshot.timestamp.desc())
        .distinct(models.CongestionSnapshot.camera_id)
        .all()
    )

    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.resolved == False)  # noqa: E712
        .order_by(models.Incident.detected_at.desc())
        .limit(100)
        .all()
    )

    return schemas.MapStateOut(
        cameras=[
            {"id": c.id, "name": c.name, "lat": c.latitude, "lng": c.longitude}
            for c in cameras
        ],
        incidents=[
            {
                "id": i.id, "type": i.incident_type, "lat": i.latitude, "lng": i.longitude,
                "detected_at": i.detected_at.isoformat(), "confidence": i.confidence,
            }
            for i in incidents
        ],
        congestion=[
            {"camera_id": c.camera_id, "level": c.level, "density": c.density, "timestamp": c.timestamp.isoformat()}
            for c in congestion_rows
        ],
    )
