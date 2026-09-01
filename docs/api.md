# API Reference (v1)

Base URL: `/api/v1`

| Method | Path | Description |
|---|---|---|
| GET | `/cameras` | List all cameras |
| POST | `/cameras` | Register a new camera |
| GET | `/cameras/{id}` | Get camera details |
| POST | `/vehicles/ingest` | Ingest an aggregated vehicle count (CV pipeline → backend) |
| GET | `/vehicles?camera_id=&hours=` | Recent vehicle counts for a camera |
| GET | `/congestion/latest` | Latest congestion snapshot per camera (for the map) |
| GET | `/congestion/{camera_id}?hours=` | Congestion history for a camera |
| POST | `/predictions/{camera_id}/generate` | Generate a 15-30 min forecast |
| GET | `/incidents?resolved=` | List incidents |
| POST | `/incidents` | Report a new incident |
| POST | `/incidents/{id}/resolve` | Mark an incident resolved |
| POST | `/signals/{intersection_id}/recommend` | Compute a recommended signal-phase plan |
| GET | `/signals/{intersection_id}/history` | Past signal-timing recommendations |
| GET | `/map/state` | Aggregated live state for the map (cameras + congestion + incidents) |

WebSocket: `ws://<host>/ws/live` — pushes update notifications; the frontend
refetches `/map/state` on any message.

Interactive docs (Swagger UI) are auto-generated at `/docs` when the backend
is running.
