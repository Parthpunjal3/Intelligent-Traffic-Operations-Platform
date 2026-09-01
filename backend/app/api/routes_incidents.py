import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[schemas.IncidentOut])
def list_incidents(resolved: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Incident)
    if resolved is not None:
        q = q.filter(models.Incident.resolved == resolved)
    return q.order_by(models.Incident.detected_at.desc()).limit(200).all()


@router.post("", response_model=schemas.IncidentOut, status_code=201)
def report_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db)):
    """Called by the CV incident-detection pipeline (or manually) to log an event."""
    incident = models.Incident(id=str(uuid.uuid4()), **payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/resolve", response_model=schemas.IncidentOut)
def resolve_incident(incident_id: str, db: Session = Depends(get_db)):
    from datetime import datetime
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    incident.resolved = True
    incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident
