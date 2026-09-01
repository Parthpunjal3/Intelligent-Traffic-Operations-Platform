# 🚦 Smart City Traffic Management Platform

AI-powered platform that ingests camera/video feeds and traffic data to
detect and count vehicles, measure congestion, forecast traffic 15–30
minutes ahead, flag accidents/abnormal events, and recommend traffic-signal
timing — all visualized on a live map.

**Stack:** Computer Vision (YOLOv8) + Time-Series Forecasting (Holt-Winters
baseline / LSTM upgrade) · FastAPI · React/Next.js · PostgreSQL · Docker

---

## Quick start (local, Docker)

```bash
git clone <your-repo-url> smart-city-traffic-ai
cd smart-city-traffic-ai
cp .env.example .env        # edit values as needed
docker compose up --build
```

- Frontend (live map): http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Postgres: localhost:5432 (credentials from `.env`)
- Everything behind Nginx: http://localhost (proxies `/api`, `/ws`, and `/`)

The backend auto-creates tables on startup for local dev. `docker/postgres/init.sql`
also seeds a sample intersection (`int-1`) and mirrors the schema for manual setup.

## Try it end-to-end

```bash
# 1. Register a camera
curl -X POST http://localhost:8000/api/v1/cameras \
  -H "Content-Type: application/json" \
  -d '{"name":"Main St & 5th Ave","latitude":22.3039,"longitude":70.8022}'

# 2. Ingest a vehicle count (normally done by the CV pipeline worker)
curl -X POST http://localhost:8000/api/v1/vehicles/ingest \
  -H "Content-Type: application/json" \
  -d '{"camera_id":"<id-from-step-1>","vehicle_class":"car","count":18,"avg_speed_kmh":32}'

# 3. Check congestion + generate a forecast
curl http://localhost:8000/api/v1/congestion/latest
curl -X POST http://localhost:8000/api/v1/predictions/<camera-id>/generate

# 4. Get a signal-timing recommendation
curl -X POST http://localhost:8000/api/v1/signals/int-1/recommend
```

Open http://localhost:3000 to see cameras/incidents on the live map.

## Repository layout

See the top of this file's original spec — matches 1:1:
`frontend/`, `backend/`, `ml/`, `computer-vision/`, `traffic-optimizer/`,
`data/`, `docker/`, `.github/workflows/`, `docs/`.

Key docs:
- [`docs/architecture.md`](docs/architecture.md) — system design & data flow
- [`docs/api.md`](docs/api.md) — REST/WebSocket API reference
- [`docs/ml.md`](docs/ml.md) — forecasting & CV model notes

## Running components individually (no Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat ../.env | xargs)   # or use pydantic-settings' .env loading
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Test a video file through the CV pipeline (no DB needed)**
```bash
cd computer-vision/detection
python run_detection.py --source ../../data/sample/your_video.mp4 --show
```

## Database — set up on GitHub / cloud

1. **GitHub itself doesn't host databases** — commit schema/migrations to
   the repo (`docker/postgres/init.sql`, and add Alembic under
   `backend/alembic/` for versioned migrations), but run Postgres via:
   - `docker compose up postgres` for local/dev, or
   - a managed Postgres (Supabase, Neon, AWS RDS, GCP Cloud SQL, Azure
     Database for PostgreSQL) for staging/production — point `POSTGRES_*`
     env vars at it.
2. Store real credentials only as **GitHub Actions secrets** / your cloud
   provider's secret manager — never commit `.env` (already gitignored).

## Deploying via GitHub

This repo ships two workflows:
- **`.github/workflows/ci.yml`** — runs backend tests (pytest) and a
  frontend build on every push/PR.
- **`.github/workflows/deploy.yml`** — on version tags (`v*`) or manual
  dispatch, builds and pushes `backend`/`frontend` images to GitHub
  Container Registry (`ghcr.io/<your-repo>/backend` and `.../frontend`).
  A commented-out SSH deploy step shows how to pull + `docker compose up -d`
  on a target server; uncomment and add `DEPLOY_HOST`/`DEPLOY_USER`/
  `DEPLOY_SSH_KEY` secrets, or swap in your cloud provider's deploy action
  (ECS, Cloud Run, Azure Container Apps, Fly.io, Render, etc.).

### Push this repo to GitHub
```bash
cd smart-city-traffic-ai
git init
git add .
git commit -m "Initial scaffold: smart city traffic AI platform"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Then in your GitHub repo settings, add any secrets needed by
`deploy.yml` (cloud credentials, `DEPLOY_HOST`, etc.) under
**Settings → Secrets and variables → Actions**.

## Notes on the ML/CV models

- Detection ships with stock YOLOv8n (COCO-pretrained) — works out of the
  box for common vehicle classes but benefits greatly from fine-tuning on
  your own traffic-camera footage. See `ml/training/`.
- Forecasting ships with a statsmodels baseline that needs no training —
  it fits per camera at request time from recent history. The optional
  LSTM path in `ml/` is for when you have enough historical data (weeks+)
  to justify it.
- Incident detection is rule-based (fast, explainable, no training data
  needed) — see `docs/ml.md` for the upgrade path to a learned model.

## License

MIT — see [LICENSE](LICENSE).
