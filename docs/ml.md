# ML & CV Notes

## Forecasting
- Baseline: Holt-Winters exponential smoothing per camera
  (`backend/app/ml/forecasting.py`), falls back to naive persistence /
  linear trend when history is short.
- Upgrade path: `ml/forecasting/lstm_model.py` + `ml/training/train_forecaster.py`
  — a sliding-window LSTM trained on `ml/preprocessing/build_timeseries.py`
  output. Export weights to `ml/models/` and load them from a custom
  `TrafficForecaster` subclass in the backend.

## Computer Vision
- Detection: YOLOv8n by default (`ultralytics`), swappable for a
  fine-tuned checkpoint via `YOLO_MODEL_PATH`.
- Tracking: dependency-free centroid tracker; swap for ByteTrack/DeepSORT
  in production for crowded scenes.
- Counting: line-crossing logic, calibrated per camera
  (`data/schemas/camera_calibration.example.json`).
- Speed: pixel-to-meter calibration per camera.
- Incidents: rule-based (stall detection, wrong-way detection) on top of
  tracker output — cheap enough for real-time use. Consider a
  clip-based action-recognition model as a second-pass classifier for
  accident detection specifically.
