"""Disponibilidad pública desde el catálogo UUID y horarios semanales."""
from datetime import datetime, time, timedelta, timezone

import pytest

from app.models.enums import VehicleType
from app.models.parking_lot import ParkingLot
from app.models.parking_lot_schedule import ParkingLotSchedule
from app.models.parking_rate import ParkingRate
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.vehicle_category import VehicleCategory
from app.services import availability_service as service


def seed_lot(db_session, *, configured=True, all_day=True):
    category = db_session.query(VehicleCategory).filter_by(code="car").one()
    lot = ParkingLot(
        name="Parqueadero de prueba",
        identification="AVAILABILITY-LOT",
        address="Bogotá",
        total_capacity=1,
        latitude=4.65,
        longitude=-74.08,
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
        is_active=True,
        parking_lot=lot,
        parking_zone=zone,
        vehicle_category=category,
    )
    db_session.add_all([lot, zone, spot])
    if configured:
        db_session.add_all(
            [
                ParkingLotSchedule(
                    parking_lot=lot,
                    day_of_week=day,
                    opens_at=None if all_day else time(9),
                    closes_at=None if all_day else time(17),
                    is_24_hours=all_day,
                )
                for day in range(7)
            ]
        )
    db_session.add(
        ParkingRate(
            parking_lot=lot,
            vehicle_category=category,
            price_per_minute=500,
            valid_from=service.now_colombia().date(),
        )
    )
    db_session.commit()
    db_session.refresh(lot)
    return lot, category


def tomorrow_at(hour: int) -> datetime:
    return (service.now_colombia() + timedelta(days=1)).replace(
        hour=hour, minute=0, second=0, microsecond=0
    )


def window(start: datetime, end: datetime) -> dict[str, str]:
    return {"start": start.isoformat(), "end": end.isoformat()}


def test_normalize_window_rejects_end_before_start():
    with pytest.raises(service.InvalidTimeWindowError):
        service.normalize_window(tomorrow_at(11), tomorrow_at(10))


def test_normalize_window_rejects_past_start():
    past = service.now_colombia() - timedelta(hours=2)
    with pytest.raises(service.InvalidTimeWindowError):
        service.normalize_window(past, past + timedelta(hours=1))


def test_normalize_window_assumes_bogota_for_naive_values():
    start, end = service.normalize_window(tomorrow_at(10), tomorrow_at(11))
    assert start.hour == 15
    assert end.hour == 16
    assert start.tzinfo == timezone.utc


def test_lots_and_vehicle_types_come_from_uuid_catalog(client, db_session):
    lot, category = seed_lot(db_session)

    lots = client.get("/api/v1/parking-lots")
    assert lots.status_code == 200
    listed_lot = next(item for item in lots.json() if item["id"] == str(lot.id))
    assert listed_lot["schedule_configured"] is True
    assert listed_lot["latitude"] == 4.65

    types = client.get(f"/api/v1/parking-lots/{lot.id}/vehicle-types")
    assert types.status_code == 200
    car = next(item for item in types.json() if item["id"] == str(category.id))
    assert car["code"] == "car"
    assert float(car["price_per_hour"]) == 30000


def test_spaces_and_price_are_calculated_for_requested_window(client, db_session):
    lot, category = seed_lot(db_session)
    start, end = tomorrow_at(10), tomorrow_at(11)

    response = client.get(
        f"/api/v1/parking-lots/{lot.id}/spaces",
        params={"vehicle_type_id": str(category.id), **window(start, end)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["available_count"] == 1
    assert body["estimated_price"] == "30000.00"
    assert body["spaces"][0]["status"] == "available"


def test_incomplete_schedule_is_reported_but_availability_remains_readable(client, db_session):
    lot, category = seed_lot(db_session, configured=False)
    listed = client.get("/api/v1/parking-lots").json()
    assert next(item for item in listed if item["id"] == str(lot.id))["schedule_configured"] is False

    response = client.get(
        f"/api/v1/parking-lots/{lot.id}/spaces",
        params={
            "vehicle_type_id": str(category.id),
            **window(tomorrow_at(10), tomorrow_at(11)),
        },
    )

    assert response.status_code == 200
    assert response.json()["available_count"] == 1


def test_configured_opening_hours_limit_availability(client, db_session):
    lot, category = seed_lot(db_session, all_day=False)

    response = client.get(
        f"/api/v1/parking-lots/{lot.id}/spaces",
        params={
            "vehicle_type_id": str(category.id),
            **window(tomorrow_at(20), tomorrow_at(21)),
        },
    )

    assert response.status_code == 422
    assert "fuera del horario" in response.json()["detail"]
