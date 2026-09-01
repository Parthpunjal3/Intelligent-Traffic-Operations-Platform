from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import schemas
from app.services import traffic_service

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/{camera_id}/generate", response_model=list[schemas.PredictionOut])
def generate(camera_id: str, db: Session = Depends(get_db)):
    """Generate a fresh 15-30 min ahead forecast for this camera."""
    return traffic_service.generate_forecast(db, camera_id)
