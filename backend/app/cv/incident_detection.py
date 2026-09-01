"""
Heuristic abnormal-event / incident detector.

Approach (no extra model weights required, works on top of the
tracker output):
  * stalled_vehicle / abnormal_stop: a tracked object whose centroid
    barely moves for N consecutive seconds while surrounding traffic
    keeps flowing.
  * wrong_way: object's net displacement vector opposes the dominant
    flow direction for that camera/lane.
  * accident (proxy): sudden, sharp deceleration of one or more
    objects combined with a stall, often paired with nearby objects
    also stopping abruptly.

This module is intentionally rule-based and cheap to run in real time;
swap in a trained action-recognition model (e.g. on short video clips)
for higher precision in production.
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List
import time

from app.models.models import IncidentType


@dataclass
class ObjectHistory:
    positions: List[Tuple[float, float, float]] = field(default_factory=list)  # x, y, t


class IncidentDetector:
    def __init__(
        self,
        stall_seconds: float = 8.0,
        stall_pixel_radius: float = 6.0,
        flow_direction: Tuple[float, float] = (0.0, 1.0),
        wrong_way_dot_threshold: float = -0.5,
        history_window: int = 60,
    ):
        self.stall_seconds = stall_seconds
        self.stall_pixel_radius = stall_pixel_radius
        self.flow_direction = flow_direction
        self.wrong_way_dot_threshold = wrong_way_dot_threshold
        self.history_window = history_window
        self._history: Dict[int, ObjectHistory] = {}
        self._flagged_stall: set = set()
        self._flagged_wrong_way: set = set()

    def update(self, object_id: int, centroid: Tuple[float, float]) -> Optional[dict]:
        now = time.time()
        hist = self._history.setdefault(object_id, ObjectHistory())
        hist.positions.append((centroid[0], centroid[1], now))
        hist.positions = hist.positions[-self.history_window:]

        if len(hist.positions) < 2:
            return None

        # --- Stall / abnormal stop detection ---
        window = [p for p in hist.positions if now - p[2] <= self.stall_seconds]
        if len(window) >= 2:
            xs = [p[0] for p in window]
            ys = [p[1] for p in window]
            spread = max(xs) - min(xs) + max(ys) - min(ys)
            elapsed = window[-1][2] - window[0][2]
            if spread < self.stall_pixel_radius and elapsed >= self.stall_seconds * 0.8:
                if object_id not in self._flagged_stall:
                    self._flagged_stall.add(object_id)
                    return {
                        "incident_type": IncidentType.stalled_vehicle,
                        "confidence": 0.6,
                        "object_id": object_id,
                    }

        # --- Wrong-way detection ---
        x0, y0, t0 = hist.positions[0]
        x1, y1, t1 = hist.positions[-1]
        dx, dy = x1 - x0, y1 - y0
        norm = (dx ** 2 + dy ** 2) ** 0.5
        if norm > 15:  # ignore noise / near-stationary
            dot = (dx / norm) * self.flow_direction[0] + (dy / norm) * self.flow_direction[1]
            if dot < self.wrong_way_dot_threshold and object_id not in self._flagged_wrong_way:
                self._flagged_wrong_way.add(object_id)
                return {
                    "incident_type": IncidentType.wrong_way,
                    "confidence": 0.55,
                    "object_id": object_id,
                }

        return None
