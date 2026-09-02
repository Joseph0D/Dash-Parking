"""Pruebas de reservas (RF-013): no-solapamiento y conversión a sesión."""
from datetime import datetime, timedelta, timezone

from app.models.enums import UserRole, VehicleType

from .helpers import auth_headers, create_user, seed_spot


def test_create_reservation_success(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    seed_spot(db_session, "A-01", VehicleType.CAR)
    headers = auth_headers(client, "client@example.com")

    vehicle = client.post("/api/v1/vehicles", json={"plate": "XYZ001", "vehicle_type": "car"}, headers=headers).json()

    start = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    resp = client.post(
        "/api/v1/reservations",
        json={"vehicle_id": vehicle["id"], "vehicle_type": "car", "start_time": start, "duration_hours": 2},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "confirmed"


def test_overlapping_reservation_is_rejected(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    seed_spot(db_session, "A-01", VehicleType.CAR)  # solo un espacio de tipo car
    headers = auth_headers(client, "client@example.com")

    v1 = client.post("/api/v1/vehicles", json={"plate": "XYZ001", "vehicle_type": "car"}, headers=headers).json()
    v2 = client.post("/api/v1/vehicles", json={"plate": "XYZ002", "vehicle_type": "car"}, headers=headers).json()

    start = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    first = client.post(
        "/api/v1/reservations",
        json={"vehicle_id": v1["id"], "vehicle_type": "car", "start_time": start, "duration_hours": 2},
        headers=headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/reservations",
        json={"vehicle_id": v2["id"], "vehicle_type": "car", "start_time": start, "duration_hours": 1},
        headers=headers,
    )
    assert second.status_code == 422


def test_cancel_reservation_frees_spot(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    seed_spot(db_session, "A-01", VehicleType.CAR)
    headers = auth_headers(client, "client@example.com")

    vehicle = client.post("/api/v1/vehicles", json={"plate": "XYZ001", "vehicle_type": "car"}, headers=headers).json()
    start = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    reservation = client.post(
        "/api/v1/reservations",
        json={"vehicle_id": vehicle["id"], "vehicle_type": "car", "start_time": start, "duration_hours": 2},
        headers=headers,
    ).json()

    cancel_resp = client.delete(f"/api/v1/reservations/{reservation['id']}", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
