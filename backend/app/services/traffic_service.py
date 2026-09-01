"""
Business logic tying together DB access, forecasting, and congestion
classification. Kept separate from API routes for testability.
"""
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models import models
from app.ml.forecasting import TrafficForecaster, classify_congestion


def record_vehicle_count(db: Session, camera_id: str, vehicle_class: str, count: int, avg_speed_kmh: float | None, timestamp: datetime | None):
    entry = models.VehicleCount(
        camera_id=camera_id,
        vehicle_class=vehicle_class,
        count=count,
        avg_speed_kmh=avg_speed_kmh,
        timestamp=timestamp or datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    _update_congestion(db, camera_id, entry.timestamp)
    return entry


def _update_congestion(db: Session, camera_id: str, timestamp: datetime):
    window_start = timestamp - timedelta(minutes=1)
    total = (
        db.query(func.sum(models.VehicleCount.count))
        .filter(
            models.VehicleCount.camera_id == camera_id,
            models.VehicleCount.timestamp >= window_start,
            models.VehicleCount.timestamp <= timestamp,
        )
        .scalar()
    ) or 0

    avg_speed = (
        db.query(func.avg(models.VehicleCount.avg_speed_kmh))
        .filter(
            models.VehicleCount.camera_id == camera_id,
            models.VehicleCount.timestamp >= window_start,
            models.VehicleCount.timestamp <= timestamp,
        )
        .scalar()
    )

    level_str = classify_congestion(
        total, settings.CONGESTION_MODERATE_THRESHOLD, settings.CONGESTION_HEAVY_THRESHOLD
    )

    snapshot = models.CongestionSnapshot(
        camera_id=camera_id,
        timestamp=timestamp,
        level=level_str,
        density=float(total),
        avg_speed_kmh=avg_speed,
    )
    db.add(snapshot)
    db.commit()
    return snapshot


def generate_forecast(db: Session, camera_id: str) -> List[models.TrafficPrediction]:
    lookback = datetime.utcnow() - timedelta(hours=6)
    rows = (
        db.query(models.VehicleCount.timestamp, func.sum(models.VehicleCount.count).label("count"))
        .filter(models.VehicleCount.camera_id == camera_id, models.VehicleCount.timestamp >= lookback)
        .group_by(models.VehicleCount.timestamp)
        .order_by(models.VehicleCount.timestamp)
        .all()
    )
    history = [(r.timestamp, float(r.count)) for r in rows]

    forecaster = TrafficForecaster()
    points = forecaster.forecast(history)

    predictions = []
    for p in points:
        level = classify_congestion(
            p.predicted_count, settings.CONGESTION_MODERATE_THRESHOLD, settings.CONGESTION_HEAVY_THRESHOLD
        )
        pred = models.TrafficPrediction(
            camera_id=camera_id,
            generated_at=datetime.utcnow(),
            target_timestamp=p.target_timestamp,
            predicted_count=p.predicted_count,
            predicted_level=level,
            confidence=p.confidence,
        )
        db.add(pred)
        predictions.append(pred)
    db.commit()
    for p in predictions:
        db.refresh(p)
    return predictions
