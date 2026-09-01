from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[schemas.CameraOut])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()


@router.post("", response_model=schemas.CameraOut, status_code=201)
def create_camera(payload: schemas.CameraCreate, db: Session = Depends(get_db)):
    camera = models.Camera(id=str(uuid.uuid4()), **payload.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("/{camera_id}", response_model=schemas.CameraOut)
def get_camera(camera_id: str, db: Session = Depends(get_db)):
    camera = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(404, "Camera not found")
    return camera
