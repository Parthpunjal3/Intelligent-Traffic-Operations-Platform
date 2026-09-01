import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

from app.services.signal_optimizer import recommend_signal_timing

router = APIRouter(prefix="/signals", tags=["signals"])


@router.post("/{intersection_id}/recommend", response_model=schemas.SignalTimingOut)
def recommend(intersection_id: str, db: Session = Depends(get_db)):
    """
    Compute a recommended signal-phase plan for an intersection based on
    the latest congestion readings from its associated cameras.
    """
    intersection = db.query(models.Intersection).filter(models.Intersection.id == intersection_id).first()
    cameras = db.query(models.Camera).filter(models.Camera.intersection_id == intersection_id).all()

    approach_volumes = []
    for cam in cameras:
        latest = (
            db.query(models.CongestionSnapshot)
            .filter(models.CongestionSnapshot.camera_id == cam.id)
            .order_by(models.CongestionSnapshot.timestamp.desc())
            .first()
        )
        approach_volumes.append(latest.density if latest else 0.0)

    plan = recommend_signal_timing(approach_volumes or [10, 10])

    timing = models.SignalTiming(
        id=str(uuid.uuid4()),
        intersection_id=intersection_id,
        phase_plan=plan,
        reason="Auto-generated from live congestion readings",
    )
    db.add(timing)
    db.commit()
    db.refresh(timing)
    return timing


@router.get("/{intersection_id}/history", response_model=list[schemas.SignalTimingOut])
def history(intersection_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.SignalTiming)
        .filter(models.SignalTiming.intersection_id == intersection_id)
        .order_by(models.SignalTiming.generated_at.desc())
        .limit(50)
        .all()
    )
