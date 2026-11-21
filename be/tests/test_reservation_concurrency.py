"""PostgreSQL integration test for simultaneous reservations of a single space."""
from __future__ import annotations

import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.models.enums import ReservationStatus, UserRole, VehicleType
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.vehicle_category import VehicleCategory


DATABASE_URL = os.getenv("RESERVATION_TEST_DATABASE_URL")
requires_postgres = pytest.mark.skipif(
    not DATABASE_URL,
    reason="Define RESERVATION_TEST_DATABASE_URL for PostgreSQL exclusion tests",
)


@requires_postgres
def test_concurrent_overlapping_reservations_cannot_claim_same_spot():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    test_id = uuid.uuid4().hex[:8].upper()
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    category_id = None
    lot_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    spot_id = uuid.uuid4()
    user_id = uuid.uuid4()
    vehicle_ids = [uuid.uuid4(), uuid.uuid4()]

    try:
        with session_factory() as setup:
            category = setup.query(VehicleCategory).filter_by(code=VehicleType.CAR.value).one()
            category_id = category.id
            setup.add(
                User(
                    id=user_id,
                    name="Concurrency test",
                    email=f"reservation-{test_id}@example.invalid",
                    password_hash="not-a-real-password-hash",
                    role=UserRole.CLIENT,
                )
            )
            lot = ParkingLot(
                id=lot_id,
                name="Concurrency test lot",
                identification=f"CONC-{test_id}",
                address="Bogota",
                total_capacity=1,
                is_active=True,
            )
            zone = ParkingZone(
                id=zone_id,
                parking_lot=lot,
                vehicle_category=category,
                name="Concurrency test zone",
                capacity=1,
            )
            spot = ParkingSpot(
                id=spot_id,
                code="C-01",
                zone=zone.name,
                vehicle_type=VehicleType.CAR,
                parking_lot=lot,
                parking_zone=zone,
                vehicle_category=category,
                is_active=True,
            )
            setup.add_all(
                [
                    lot,
                    zone,
                    spot,
                    *[
                        Vehicle(
                            id=vehicle_id,
                            plate=f"C{test_id}{index}",
                            vehicle_type=VehicleType.CAR,
                            vehicle_category_id=category_id,
                            owner_id=user_id,
                        )
                        for index, vehicle_id in enumerate(vehicle_ids)
                    ],
                ]
            )
            setup.commit()

        barrier = threading.Barrier(2)
        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(hours=2)

        def reserve(vehicle_id: uuid.UUID) -> str:
            with session_factory() as db:
                db.add(
                    Reservation(
                        vehicle_id=vehicle_id,
                        spot_id=spot_id,
                        parking_lot_id=lot_id,
                        vehicle_type=VehicleType.CAR,
                        start_time=start,
                        end_time=end,
                        status=ReservationStatus.CONFIRMED,
                    )
                )
                barrier.wait(timeout=10)
                try:
                    db.commit()
                    return "created"
                except IntegrityError as exc:
                    db.rollback()
                    original = exc.orig
                    return getattr(original, "sqlstate", None) or getattr(original, "pgcode", "unknown")

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(reserve, vehicle_ids))

        assert sorted(outcomes) == ["23P01", "created"]
    finally:
        with Session(engine) as cleanup:
            cleanup.execute(delete(Reservation).where(Reservation.spot_id == spot_id))
            cleanup.execute(delete(ParkingSpot).where(ParkingSpot.id == spot_id))
            cleanup.execute(delete(ParkingZone).where(ParkingZone.id == zone_id))
            cleanup.execute(delete(Vehicle).where(Vehicle.id.in_(vehicle_ids)))
            cleanup.execute(delete(ParkingLot).where(ParkingLot.id == lot_id))
            cleanup.execute(delete(User).where(User.id == user_id))
            cleanup.commit()
        engine.dispose()
