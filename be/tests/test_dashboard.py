"""Pruebas del dashboard administrativo filtrable (RF-017)."""
from app.models.enums import UserRole, VehicleType

from .helpers import auth_headers, create_user, seed_rate, seed_spot


def test_dashboard_requires_admin_role(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    headers = auth_headers(client, "client@example.com")
    resp = client.get("/api/v1/reports/dashboard", headers=headers)
    assert resp.status_code == 403


def test_dashboard_totals_after_a_paid_session(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    create_user(db_session, "staff@example.com", role=UserRole.OPERATOR)
    create_user(db_session, "admin@example.com", role=UserRole.ADMIN)
    seed_rate(db_session, VehicleType.CAR, "4000")
    seed_spot(db_session, "A-01", VehicleType.CAR)

    client_headers = auth_headers(client, "client@example.com")
    staff_headers = auth_headers(client, "staff@example.com")
    admin_headers = auth_headers(client, "admin@example.com")

    client.post("/api/v1/vehicles", json={"plate": "ABC123", "vehicle_type": "car"}, headers=client_headers)
    entry = client.post(
        "/api/v1/sessions/entry", json={"plate": "ABC123", "vehicle_type": "car"}, headers=staff_headers
    ).json()
    client.post("/api/v1/payments/cash", json={"session_id": entry["id"]}, headers=staff_headers)

    dashboard = client.get("/api/v1/reports/dashboard", headers=admin_headers).json()
    assert dashboard["total_sessions"] == 1
    assert float(dashboard["total_revenue"]) > 0

    filtered = client.get(
        "/api/v1/reports/dashboard?vehicle_type=motorcycle", headers=admin_headers
    ).json()
    assert filtered["total_sessions"] == 0
