from datetime import date, time
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.enums import UserRole, VehicleType
from app.models.parking_lot import ParkingLot
from app.models.parking_lot_member import ParkingLotMember
from app.models.parking_lot_schedule import ParkingLotSchedule
from app.models.parking_rate import ParkingRate
from app.models.parking_space_type import ParkingSpaceType
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.user import User
from app.models.vehicle_category import VehicleCategory
from app.scripts.migrate_parking_catalog import _vehicle_type


def test_uuid_parking_catalog_relations_and_scoped_operator(db_session):
    owner = User(
        name="Owner",
        email="owner@example.com",
        password_hash="hash",
        role=UserRole.OWNER,
    )
    operator = User(
        name="Operator",
        email="operator@example.com",
        password_hash="hash",
        role=UserRole.OPERATOR,
    )
    truck = db_session.query(VehicleCategory).filter_by(code="truck").one()
    lot = ParkingLot(
        owner=owner,
        name="Parqueadero Norte",
        identification="PARK-NORTH",
        address="Bogotá",
        total_capacity=4,
        latitude=4.7,
        longitude=-74.0,
    )
    zone = ParkingZone(
        parking_lot=lot,
        vehicle_category=truck,
        name="Camiones",
        capacity=4,
    )
    space_type = ParkingSpaceType(code="truck_standard", name="Camión estándar")
    spot = ParkingSpot(
        code="T-01",
        zone="Camiones",
        vehicle_type=VehicleType.TRUCK,
        parking_lot=lot,
        parking_zone=zone,
        vehicle_category=truck,
        space_type=space_type,
    )
    lot.schedules.append(
        ParkingLotSchedule(
            day_of_week=0,
            opens_at=time(8, 0),
            closes_at=time(18, 0),
        )
    )
    lot.rates.append(
        ParkingRate(
            vehicle_category=truck,
            price_per_minute=Decimal("1000.00"),
            price_per_day=Decimal("40000.00"),
            valid_from=date(2026, 1, 1),
        )
    )
    lot.memberships.append(ParkingLotMember(user=operator, created_by_user=owner))

    db_session.add_all([lot, space_type])
    db_session.commit()

    assert spot.parking_lot.owner.role is UserRole.OWNER
    assert spot.parking_zone.vehicle_category.code == "truck"
    assert lot.memberships[0].user.role is UserRole.OPERATOR
    assert lot.schedules[0].day_of_week == 0
    assert lot.rates[0].price_per_minute == Decimal("1000.00")


def test_parking_lot_and_schedule_constraints_are_enforced(db_session):
    lot = ParkingLot(
        name="Invalid",
        identification="INVALID",
        address="Bogotá",
        total_capacity=0,
    )
    db_session.add(lot)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    lot = ParkingLot(
        name="Valid",
        identification="VALID",
        address="Bogotá",
        total_capacity=1,
    )
    lot.schedules.append(ParkingLotSchedule(day_of_week=7, is_closed=True))
    db_session.add(lot)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_space_codes_can_repeat_in_different_parking_lots(db_session):
    category = db_session.query(VehicleCategory).filter_by(code="car").one()
    space_type = ParkingSpaceType(code="standard", name="Estándar")
    first_lot = ParkingLot(
        name="Norte",
        identification="LOT-NORTH",
        address="Bogotá",
        total_capacity=1,
    )
    second_lot = ParkingLot(
        name="Sur",
        identification="LOT-SOUTH",
        address="Bogotá",
        total_capacity=1,
    )
    first_zone = ParkingZone(
        parking_lot=first_lot,
        vehicle_category=category,
        name="Carros",
        capacity=1,
    )
    second_zone = ParkingZone(
        parking_lot=second_lot,
        vehicle_category=category,
        name="Carros",
        capacity=1,
    )
    db_session.add_all(
        [
            first_lot,
            second_lot,
            space_type,
            ParkingSpot(
                code="A-01",
                zone="Carros",
                vehicle_type=VehicleType.CAR,
                parking_lot=first_lot,
                parking_zone=first_zone,
                vehicle_category=category,
                space_type=space_type,
            ),
            ParkingSpot(
                code="A-01",
                zone="Carros",
                vehicle_type=VehicleType.CAR,
                parking_lot=second_lot,
                parking_zone=second_zone,
                vehicle_category=category,
                space_type=space_type,
            ),
        ]
    )
    db_session.commit()


@pytest.mark.parametrize(
    ("legacy_name", "expected"),
    [
        ("Carro", VehicleType.CAR),
        ("Moto electrica", VehicleType.ELECTRIC_MOTORCYCLE),
        ("Bicicleta", VehicleType.BICYCLE),
        ("Camión", VehicleType.TRUCK),
    ],
)
def test_legacy_vehicle_type_mapping(legacy_name, expected):
    assert _vehicle_type(legacy_name)[1] is expected


def test_unknown_legacy_vehicle_type_fails_explicitly():
    with pytest.raises(ValueError, match="no reconocido"):
        _vehicle_type("vehículo desconocido")
