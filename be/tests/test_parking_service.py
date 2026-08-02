"""
Pruebas del servicio de negocio ParkingService — Sprint 0.
"""
import pytest

from app.models.vehicle import ParkingSpot, VehicleType
from app.services.parking_service import (
    NoAvailableSpotError,
    ParkingService,
    VehicleAlreadyInsideError,
)


def make_service(num_spots: int = 2) -> ParkingService:
    spots = [ParkingSpot(spot_number=f"A-{i}") for i in range(1, num_spots + 1)]
    return ParkingService(spots=spots)


def test_register_entry_assigns_first_available_spot():
    service = make_service(num_spots=2)

    vehicle, spot = service.register_entry(plate="ABC123", vehicle_type=VehicleType.CAR)

    assert vehicle.plate == "ABC123"
    assert spot.occupied_by == "ABC123"


def test_register_entry_twice_same_plate_raises_error():
    service = make_service(num_spots=2)
    service.register_entry(plate="ABC123", vehicle_type=VehicleType.CAR)

    with pytest.raises(VehicleAlreadyInsideError):
        service.register_entry(plate="ABC123", vehicle_type=VehicleType.CAR)


def test_register_entry_without_available_spots_raises_error():
    service = make_service(num_spots=1)
    service.register_entry(plate="ABC123", vehicle_type=VehicleType.CAR)

    with pytest.raises(NoAvailableSpotError):
        service.register_entry(plate="XYZ789", vehicle_type=VehicleType.MOTORCYCLE)
