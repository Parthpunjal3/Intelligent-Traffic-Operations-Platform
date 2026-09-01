-- Initial schema bootstrap for local/dev use.
-- In staging/production, prefer Alembic migrations (backend/alembic/)
-- generated from the SQLAlchemy models in backend/app/models/models.py.
-- This file mirrors that schema for reference / manual DB setup.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS intersections (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    num_approaches INTEGER DEFAULT 4
);

CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    intersection_id VARCHAR REFERENCES intersections(id),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    stream_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_counts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    vehicle_class VARCHAR NOT NULL DEFAULT 'car',
    count INTEGER DEFAULT 0,
    avg_speed_kmh DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_vehicle_counts_camera_ts ON vehicle_counts(camera_id, timestamp);

CREATE TABLE IF NOT EXISTS congestion_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    level VARCHAR NOT NULL DEFAULT 'free_flow',
    density DOUBLE PRECISION DEFAULT 0.0,
    avg_speed_kmh DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_congestion_camera_ts ON congestion_snapshots(camera_id, timestamp);

CREATE TABLE IF NOT EXISTS traffic_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    generated_at TIMESTAMP DEFAULT NOW(),
    target_timestamp TIMESTAMP NOT NULL,
    predicted_count DOUBLE PRECISION NOT NULL,
    predicted_level VARCHAR DEFAULT 'free_flow',
    confidence DOUBLE PRECISION DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    incident_type VARCHAR NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    confidence DOUBLE PRECISION DEFAULT 0.0,
    description VARCHAR,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    metadata_json JSONB
);
CREATE INDEX IF NOT EXISTS idx_incidents_detected_at ON incidents(detected_at);

CREATE TABLE IF NOT EXISTS signal_timings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intersection_id VARCHAR NOT NULL REFERENCES intersections(id),
    generated_at TIMESTAMP DEFAULT NOW(),
    phase_plan JSONB NOT NULL,
    reason VARCHAR,
    applied BOOLEAN DEFAULT FALSE
);

-- Sample seed data for local development
INSERT INTO intersections (id, name, latitude, longitude, num_approaches)
VALUES ('int-1', 'Main St & 5th Ave', 22.3039, 70.8022, 4)
ON CONFLICT (id) DO NOTHING;
