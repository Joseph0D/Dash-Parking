"""
Pruebas del modelo de dominio (Vehicle, ParkingSpot) — Sprint 0.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.models.vehicle import ParkingSpot, Vehicle, VehicleType


def test_vehicle_plate_is_normalized():
    vehicle = Vehicle(
        plate=" abc 123 ",
        vehicle_type=VehicleType.CAR,
        entry_time=datetime.now(timezone.utc),
    )
    assert vehicle.plate == "ABC123"


def test_vehicle_starts_inside():
    vehicle = Vehicle(
        plate="ABC123", vehicle_type=VehicleType.CAR, entry_time=datetime.now(timezone.utc)
    )
    assert vehicle.is_inside is True


def test_register_exit_marks_vehicle_as_outside():
    entry = datetime.now(timezone.utc)
    vehicle = Vehicle(plate="ABC123", vehicle_type=VehicleType.CAR, entry_time=entry)

    vehicle.register_exit(entry + timedelta(hours=1))

    assert vehicle.is_inside is False


def test_register_exit_before_entry_raises_error():
    entry = datetime.now(timezone.utc)
    vehicle = Vehicle(plate="ABC123", vehicle_type=VehicleType.CAR, entry_time=entry)

    with pytest.raises(ValueError):
        vehicle.register_exit(entry - timedelta(hours=1))


def test_parking_spot_assign_and_release():
    spot = ParkingSpot(spot_number="A-1")
    assert spot.is_available is True

    spot.assign("ABC123")
    assert spot.is_available is False
    assert spot.occupied_by == "ABC123"

    spot.release()
    assert spot.is_available is True


def test_parking_spot_cannot_be_double_assigned():
    spot = ParkingSpot(spot_number="A-1")
    spot.assign("ABC123")

    with pytest.raises(ValueError):
        spot.assign("XYZ789")
