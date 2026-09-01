"""
Approximate speed estimation from tracked centroids using a
pixel-to-meter calibration factor (obtained by measuring a known
real-world distance, e.g. lane width, in the camera's field of view).
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
import time


@dataclass
class SpeedEstimator:
    pixels_per_meter: float
    fps: float = 15.0
    history: Dict[int, Tuple[float, float, float]] = field(default_factory=dict)  # id -> (x, y, t)

    def update(self, object_id: int, centroid: Tuple[float, float]) -> Optional[float]:
        now = time.time()
        prev = self.history.get(object_id)
        self.history[object_id] = (centroid[0], centroid[1], now)
        if prev is None:
            return None
        dx = centroid[0] - prev[0]
        dy = centroid[1] - prev[1]
        dt = now - prev[2]
        if dt <= 0:
            return None
        pixel_dist = (dx ** 2 + dy ** 2) ** 0.5
        meters = pixel_dist / self.pixels_per_meter
        speed_mps = meters / dt
        return speed_mps * 3.6  # km/h
