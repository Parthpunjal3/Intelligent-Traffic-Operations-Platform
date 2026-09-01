"""
Vehicle detection using a YOLOv8 model (ultralytics).

Falls back gracefully if the model weights aren't available locally --
in that case call `.download_weights()` or point YOLO_MODEL_PATH at a
custom-trained checkpoint (e.g. fine-tuned on traffic-camera footage).
"""
from dataclasses import dataclass
from typing import List

import numpy as np

from app.core.config import settings

VEHICLE_CLASS_NAMES = {"car", "truck", "bus", "motorcycle", "bicycle"}


@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)


class VehicleDetector:
    def __init__(self, model_path: str | None = None, conf: float | None = None):
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.conf = conf or settings.DETECTION_CONFIDENCE
        self._model = None

    def _lazy_load(self):
        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_path)
        return self._model

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Run detection on a single BGR frame, return only vehicle classes."""
        model = self._lazy_load()
        results = model.predict(frame, conf=self.conf, verbose=False)[0]

        detections: List[Detection] = []
        names = results.names
        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = names.get(cls_id, str(cls_id))
            if cls_name not in VEHICLE_CLASS_NAMES:
                continue
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            conf = float(box.conf[0])
            detections.append(Detection(cls_name, conf, (x1, y1, x2, y2)))
        return detections
