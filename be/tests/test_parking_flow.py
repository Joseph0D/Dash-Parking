"""
Pruebas del flujo operativo completo: vehículo -> ingreso -> cobro -> pago (RF-001, RF-002,
RF-004, RF-005, RF-006, RF-014).
"""
from app.models.enums import UserRole, VehicleType

from .helpers import auth_headers, create_user, seed_rate, seed_spot


def _register_vehicle(client, headers, plate="ABC123"):
    return client.post(
        "/api/v1/vehicles",
        json={"plate": plate, "vehicle_type": "car"},
        headers=headers,
    )


def test_full_entry_to_cash_payment_flow(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    create_user(db_session, "staff@example.com", role=UserRole.OPERATOR)
    seed_rate(db_session, VehicleType.CAR, "4000")
    seed_spot(db_session, "A-01", VehicleType.CAR)

    client_headers = auth_headers(client, "client@example.com")
    staff_headers = auth_headers(client, "staff@example.com")

    vehicle_resp = _register_vehicle(client, client_headers)
    assert vehicle_resp.status_code == 201

    entry_resp = client.post(
        "/api/v1/sessions/entry", json={"plate": "ABC123", "vehicle_type": "car"}, headers=staff_headers
    )
    assert entry_resp.status_code == 201
    session_id = entry_resp.json()["id"]
    assert entry_resp.json()["spot_code"] == "A-01"

    pay_resp = client.post("/api/v1/payments/cash", json={"session_id": session_id}, headers=staff_headers)
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "paid"

    occupancy = client.get("/api/v1/parking/occupancy").json()
    assert occupancy["available_spots"] == 1  # el espacio se liberó tras el pago


def test_entry_without_available_spot_returns_422(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    create_user(db_session, "staff@example.com", role=UserRole.OPERATOR)
    seed_rate(db_session, VehicleType.CAR, "4000")
    # sin seed_spot: no hay espacios

    client_headers = auth_headers(client, "client@example.com")
    staff_headers = auth_headers(client, "staff@example.com")
    _register_vehicle(client, client_headers)

    entry_resp = client.post(
        "/api/v1/sessions/entry", json={"plate": "ABC123", "vehicle_type": "car"}, headers=staff_headers
    )
    assert entry_resp.status_code == 422


def test_client_cannot_register_entry(client, db_session):
    """RF-001 solo lo pueden ejecutar operator/admin (require_staff)."""
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    seed_rate(db_session, VehicleType.CAR, "4000")
    seed_spot(db_session)

    client_headers = auth_headers(client, "client@example.com")
    _register_vehicle(client, client_headers)

    entry_resp = client.post(
        "/api/v1/sessions/entry", json={"plate": "ABC123", "vehicle_type": "car"}, headers=client_headers
    )
    assert entry_resp.status_code == 403
