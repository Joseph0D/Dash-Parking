"""
Pruebas del endpoint POST /api/v1/vehicles/entry — Sprint 0.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_vehicle_entry_returns_201_and_assigned_spot():
    response = client.post(
        "/api/v1/vehicles/entry",
        json={"plate": "TEST01", "vehicle_type": "car"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["plate"] == "TEST01"
    assert body["assigned_spot"].startswith("A-")


def test_register_vehicle_entry_duplicate_plate_returns_409():
    client.post("/api/v1/vehicles/entry", json={"plate": "TEST02", "vehicle_type": "car"})

    response = client.post(
        "/api/v1/vehicles/entry",
        json={"plate": "TEST02", "vehicle_type": "car"},
    )

    assert response.status_code == 409


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
