# Speed Estimation

See `backend/app/cv/speed.py` (`SpeedEstimator`). Requires a
`pixels_per_meter` calibration constant per camera -- measure a known
real-world distance (e.g. lane width ~3.5m, or distance between two
lane markings) in a reference frame and divide by the pixel distance.

Store per-camera calibration values in `data/schemas/camera_calibration.json`.
