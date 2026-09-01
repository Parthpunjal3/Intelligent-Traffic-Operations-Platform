# Architecture

## Overview

```
Cameras/Streams --> CV Pipeline (detection+tracking+counting+incident) --> Backend API --> PostgreSQL
                                                                              |
                                                                              v
                                                              Forecasting + Signal Optimizer
                                                                              |
                                                                              v
                                                                  Frontend (live map + dashboard)
```

## Components

- **computer-vision/** & **backend/app/cv/** — YOLOv8-based vehicle detection, a
  centroid tracker for stable IDs, line-crossing counting, speed estimation via
  pixel-to-meter calibration, and rule-based incident detection (stalls, wrong-way).
  Shared modules live under `backend/app/cv/` so the same logic runs in
  production and in offline test scripts under `computer-vision/`.

- **ml/** & **backend/app/ml/** — Forecasting. The backend ships a fast
  statsmodels (Holt-Winters) baseline (`backend/app/ml/forecasting.py`) that
  works with limited historical data. `ml/` contains a reference PyTorch LSTM
  pipeline (preprocessing → training → evaluation) for higher accuracy once
  you have weeks of historical vehicle-count data per camera.

- **backend/** — FastAPI service exposing REST endpoints for cameras, vehicle
  counts, congestion, predictions, incidents, and signal-timing
  recommendations, plus a `/ws/live` WebSocket for pushing updates to the
  frontend. PostgreSQL via SQLAlchemy.

- **traffic-optimizer/** — Webster's-formula-based signal-timing optimizer
  (`optimizer.py`) plus a delay simulator (`simulator.py`) for offline
  what-if testing of candidate signal plans.

- **frontend/** — Next.js app with a live Leaflet map (color-coded congestion
  markers + incident markers) and a dashboard sidebar, polling
  `/api/v1/map/state` and subscribing to `/ws/live` for push updates.

## Data flow (typical camera pipeline)

1. A worker process reads frames from a camera/RTSP stream.
2. `VehicleDetector` runs YOLOv8 inference per frame.
3. `CentroidTracker` assigns stable IDs across frames.
4. `LineCounter` / `SpeedEstimator` aggregate counts and speed per window (e.g. 60s).
5. The worker POSTs the aggregate to `/api/v1/vehicles/ingest`, which also
   updates the rolling congestion snapshot.
6. `IncidentDetector` runs alongside the tracker; any flagged event is POSTed
   to `/api/v1/incidents`.
7. A scheduler periodically calls `/api/v1/predictions/{camera_id}/generate`
   and `/api/v1/signals/{intersection_id}/recommend`.
8. The frontend polls/subscribes and renders everything on the map.
