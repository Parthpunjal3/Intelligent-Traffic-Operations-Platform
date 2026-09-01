from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/congestion", tags=["congestion"])


@router.get("/latest", response_model=list[schemas.CongestionOut])
def latest_congestion(db: Session = Depends(get_db)):
    """Latest congestion snapshot per camera -- used to populate the live map."""
    subq = (
        db.query(
            models.CongestionSnapshot.camera_id,
            models.CongestionSnapshot.timestamp,
        )
        .order_by(models.CongestionSnapshot.camera_id, models.CongestionSnapshot.timestamp.desc())
        .distinct(models.CongestionSnapshot.camera_id)
        .subquery()
    )
    return (
        db.query(models.CongestionSnapshot)
        .join(
            subq,
            (models.CongestionSnapshot.camera_id == subq.c.camera_id)
            & (models.CongestionSnapshot.timestamp == subq.c.timestamp),
        )
        .all()
    )


@router.get("/{camera_id}", response_model=list[schemas.CongestionOut])
def congestion_history(camera_id: str, hours: int = Query(1, ge=1, le=48), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(models.CongestionSnapshot)
        .filter(models.CongestionSnapshot.camera_id == camera_id, models.CongestionSnapshot.timestamp >= since)
        .order_by(models.CongestionSnapshot.timestamp)
        .all()
    )
