def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_list_camera(client):
    payload = {"name": "Main St & 5th Ave", "latitude": 12.34, "longitude": 56.78}
    r = client.post("/api/v1/cameras", json=payload)
    assert r.status_code == 201
    camera = r.json()
    assert camera["name"] == payload["name"]

    r2 = client.get("/api/v1/cameras")
    assert r2.status_code == 200
    assert len(r2.json()) == 1


def test_ingest_vehicle_count_updates_congestion(client):
    cam = client.post("/api/v1/cameras", json={"name": "Cam A", "latitude": 1.0, "longitude": 1.0}).json()
    r = client.post(
        "/api/v1/vehicles/ingest",
        json={"camera_id": cam["id"], "vehicle_class": "car", "count": 5, "avg_speed_kmh": 40.0},
    )
    assert r.status_code == 201

    latest = client.get("/api/v1/congestion/latest").json()
    assert len(latest) == 1
    assert latest[0]["camera_id"] == cam["id"]


def test_signal_recommendation(client):
    intersection_payload_camera = {"name": "Cam B", "latitude": 2.0, "longitude": 2.0}
    client.post("/api/v1/cameras", json=intersection_payload_camera)
    r = client.post("/api/v1/signals/int-1/recommend")
    assert r.status_code == 200
    body = r.json()
    assert "cycle" in body["phase_plan"]
