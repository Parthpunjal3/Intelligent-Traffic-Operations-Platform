from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.services import traffic_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/ingest", response_model=schemas.VehicleCountOut, status_code=201)
def ingest_vehicle_count(payload: schemas.VehicleCountIngest, db: Session = Depends(get_db)):
    """
    Ingest an aggregated vehicle count for a camera/time-bucket.
    In production this is called by the CV pipeline worker after
    processing each aggregation window (e.g. every 60s per camera).
    """
    return traffic_service.record_vehicle_count(
        db,
        camera_id=payload.camera_id,
        vehicle_class=payload.vehicle_class,
        count=payload.count,
        avg_speed_kmh=payload.avg_speed_kmh,
        timestamp=payload.timestamp,
    )


@router.get("", response_model=list[schemas.VehicleCountOut])
def list_vehicle_counts(
    camera_id: str = Query(...),
    hours: int = Query(1, ge=1, le=48),
    db: Session = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(models.VehicleCount)
        .filter(models.VehicleCount.camera_id == camera_id, models.VehicleCount.timestamp >= since)
        .order_by(models.VehicleCount.timestamp)
        .all()
    )
