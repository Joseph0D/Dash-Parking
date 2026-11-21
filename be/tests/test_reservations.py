"""Pruebas de reservas por parqueadero y rango horario."""
from datetime import datetime, timedelta, timezone

from app.models.enums import UserRole, VehicleType
from app.models.parking_lot import ParkingLot
from app.models.parking_lot_schedule import ParkingLotSchedule
from app.models.parking_rate import ParkingRate
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.vehicle_category import VehicleCategory

from .helpers import auth_headers, create_user


def seed_lot(db_session, *, configure_schedule=True):
    category = db_session.query(VehicleCategory).filter_by(code="car").one()
    lot = ParkingLot(
        name="Parqueadero de prueba",
        identification="TEST-LOT",
        address="Bogotá",
        total_capacity=1,
        is_active=True,
    )
    zone = ParkingZone(
        parking_lot=lot,
        vehicle_category=category,
        name="Carros",
        capacity=1,
    )
    spot = ParkingSpot(
        code="A-01",
        zone="Carros",
        vehicle_type=VehicleType.CAR,
        parking_lot=lot,
        parking_zone=zone,
        vehicle_category=category,
        is_active=True,
    )
    db_session.add_all([lot, zone, spot])
    if configure_schedule:
        db_session.add_all(
            [
                ParkingLotSchedule(
                    parking_lot=lot,
                    day_of_week=day,
                    is_24_hours=True,
                )
                for day in range(7)
            ]
        )
    db_session.add(
        ParkingRate(
            parking_lot=lot,
            vehicle_category=category,
            price_per_minute=10,
            valid_from=datetime.now(timezone.utc).date(),
        )
    )
    db_session.commit()
    db_session.refresh(lot)
    return lot


def create_vehicle(client, headers, plate):
    return client.post(
        "/api/v1/vehicles",
        json={"plate": plate, "vehicle_type": "car"},
        headers=headers,
    ).json()


def reservation_payload(lot_id, vehicle_id, start, end):
    return {
        "parking_lot_id": str(lot_id),
        "vehicle_id": vehicle_id,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }


def test_create_reservation_success(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session)
    headers = auth_headers(client, "client@example.com")
    vehicle = create_vehicle(client, headers, "XYZ001")
    start = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
    resp = client.post(
        "/api/v1/reservations",
        json={
            "parking_lot_id": str(lot.id),
            "vehicle_id": vehicle["id"],
            "start_time": start,
            "end_time": end,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "confirmed"
    assert resp.json()["parking_lot_id"] == str(lot.id)
    assert resp.json()["parking_lot_name"] == lot.name


def test_overlapping_reservation_is_rejected(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session)
    headers = auth_headers(client, "client@example.com")

    v1 = create_vehicle(client, headers, "XYZ001")
    v2 = create_vehicle(client, headers, "XYZ002")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)
    first = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, v1["id"], start, end),
        headers=headers,
    )
    assert first.status_code == 201

    same_vehicle = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, v1["id"], start, end),
        headers=headers,
    )
    assert same_vehicle.status_code == 409

    second = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, v2["id"], start, start + timedelta(hours=1)),
        headers=headers,
    )
    assert second.status_code == 409


def test_availability_is_reserved_only_for_the_matching_window(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session)
    headers = auth_headers(client, "client@example.com")
    vehicle = create_vehicle(client, headers, "XYZ001")
    start = datetime.now(timezone.utc) + timedelta(hours=2)
    end = start + timedelta(hours=1)

    created = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, vehicle["id"], start, end),
        headers=headers,
    )
    assert created.status_code == 201

    reserved_window = client.get(
        f"/api/v1/parking-lots/{lot.id}/spaces",
        params={
            "vehicle_type_id": vehicle["vehicle_category_id"],
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
    )
    next_day = client.get(
        f"/api/v1/parking-lots/{lot.id}/spaces",
        params={
            "vehicle_type_id": vehicle["vehicle_category_id"],
            "start": (start + timedelta(days=1)).isoformat(),
            "end": (end + timedelta(days=1)).isoformat(),
        },
    )

    assert reserved_window.json()["spaces"][0]["status"] == "reserved"
    assert next_day.json()["spaces"][0]["status"] == "available"


def test_adjacent_and_different_day_reservations_are_allowed(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session)
    headers = auth_headers(client, "client@example.com")
    first_vehicle = create_vehicle(client, headers, "XYZ001")
    second_vehicle = create_vehicle(client, headers, "XYZ002")
    start = datetime.now(timezone.utc) + timedelta(hours=1)

    first = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, first_vehicle["id"], start, start + timedelta(hours=2)),
        headers=headers,
    )
    adjacent = client.post(
        "/api/v1/reservations",
        json=reservation_payload(
            lot.id,
            second_vehicle["id"],
            start + timedelta(hours=2),
            start + timedelta(hours=3),
        ),
        headers=headers,
    )
    next_day = client.post(
        "/api/v1/reservations",
        json=reservation_payload(
            lot.id,
            second_vehicle["id"],
            start + timedelta(days=1),
            start + timedelta(days=3),
        ),
        headers=headers,
    )
    assert first.status_code == adjacent.status_code == next_day.status_code == 201


def test_cancel_reservation_frees_spot(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session)
    headers = auth_headers(client, "client@example.com")

    vehicle = create_vehicle(client, headers, "XYZ001")
    second_vehicle = create_vehicle(client, headers, "XYZ002")
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    reservation = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, vehicle["id"], start, start + timedelta(hours=2)),
        headers=headers,
    ).json()

    cancel_resp = client.delete(f"/api/v1/reservations/{reservation['id']}", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
    after_cancel = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, second_vehicle["id"], start, start + timedelta(hours=2)),
        headers=headers,
    )
    assert after_cancel.status_code == 201


def test_unconfigured_schedule_blocks_reservations(client, db_session):
    create_user(db_session, "client@example.com", role=UserRole.CLIENT)
    lot = seed_lot(db_session, configure_schedule=False)
    headers = auth_headers(client, "client@example.com")
    vehicle = create_vehicle(client, headers, "XYZ001")
    start = datetime.now(timezone.utc) + timedelta(hours=1)

    response = client.post(
        "/api/v1/reservations",
        json=reservation_payload(lot.id, vehicle["id"], start, start + timedelta(days=2)),
        headers=headers,
    )

    assert response.status_code == 409
    assert "horario semanal" in response.json()["detail"]
