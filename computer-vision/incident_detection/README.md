# Incident Detection

Rule-based incident detection (stalls, wrong-way driving) lives in
`backend/app/cv/incident_detection.py` (`IncidentDetector`), built on
top of the shared tracker. Detected incidents are POSTed to
`/api/v1/incidents` so they show up immediately on the live map.

For higher-precision accident detection, consider fine-tuning an
action-recognition model (e.g. SlowFast/X3D) on short clips around
sudden-deceleration events flagged by this heuristic layer, and use it
as a second-pass classifier before auto-alerting.
