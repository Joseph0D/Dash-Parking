from __future__ import annotations

import uuid
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import select

from app.models.enums import SessionStatus, VehicleType
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.vehicle_category import VehicleCategory
from app.services.availability_service import COLOMBIA_TZ


def _register(client, email: str, account_type: str = "owner") -> tuple[dict, dict]:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Owner",
            "email": email,
            "password": "securepassword1",
            "account_type": account_type,
        },
    )
    assert response.status_code == 201
    data = response.json()
    return data, {"Authorization": f"Bearer {data['access_token']}"}


def _create_parking_lot(client, db_session, headers, identification: str = "NIT-101"):
    car = db_session.execute(
        select(VehicleCategory).where(VehicleCategory.code == VehicleType.CAR.value)
    ).scalar_one()
    response = client.post(
        "/api/v1/owner/parking-lots",
        headers=headers,
        json={
            "name": "Parqueadero Central",
            "identification": identification,
            "address": "Calle 10 # 5-20, Bogotá",
            "phone": "3001234567",
            "latitude": 4.65,
            "longitude": -74.08,
            "schedules": [
                {
                    "day_of_week": day,
                    "opens_at": None,
                    "closes_at": None,
                    "is_closed": False,
                    "is_24_hours": True,
                }
                for day in range(7)
            ],
            "inventory": [
                {
                    "vehicle_category_id": str(car.id),
                    "space_count": 2,
                    "price_per_minute": "120",
                    "price_per_day": "20000",
                    "price_per_month": None,
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json(), car


def test_owner_registration_and_parking_lot_access_are_isolated(client, db_session):
    first_owner, first_headers = _register(client, "first-owner@example.com")
    second_owner, second_headers = _register(client, "second-owner@example.com")
    assert first_owner["user"]["role"] == "owner"

    lot, _ = _create_parking_lot(client, db_session, first_headers)
    assert lot["schedule_configured"] is True
    assert lot["total_capacity"] == 2
    assert len(lot["schedules"]) == 7

    own_lots = client.get("/api/v1/owner/parking-lots", headers=first_headers)
    other_lots = client.get("/api/v1/owner/parking-lots", headers=second_headers)
    denied_detail = client.get(
        f"/api/v1/owner/parking-lots/{lot['id']}", headers=second_headers
    )
    client_user, client_headers = _register(
        client, "normal-client@example.com", account_type="client"
    )
    denied_by_role = client.get(
        "/api/v1/owner/parking-lots", headers=client_headers
    )

    assert own_lots.status_code == 200 and len(own_lots.json()) == 1
    assert other_lots.status_code == 200 and other_lots.json() == []
    assert denied_detail.status_code == 404
    assert denied_by_role.status_code == 403
    assert client_user["user"]["role"] == "client"
    assert client.post(
        "/api/v1/auth/register",
        json={
            "name": "Unsafe",
            "email": "unsafe-role@example.com",
            "password": "securepassword1",
            "account_type": "admin",
        },
    ).status_code == 422


def test_owner_cannot_reduce_inventory_below_active_sessions(client, db_session):
    owner_data, headers = _register(client, "inventory-owner@example.com")
    lot, category = _create_parking_lot(client, db_session, headers)
    user = db_session.get(User, uuid.UUID(owner_data["user"]["id"]))
    spots = db_session.execute(
        select(ParkingSpot).where(ParkingSpot.parking_lot_id == uuid.UUID(lot["id"]))
    ).scalars().all()
    for index, spot in enumerate(spots):
        vehicle = Vehicle(
            plate=f"TST{index:03d}",
            vehicle_type=VehicleType.CAR,
            vehicle_category_id=category.id,
            owner_id=user.id,
        )
        db_session.add(vehicle)
        db_session.flush()
        db_session.add(
            ParkingSession(
                vehicle_id=vehicle.id,
                spot_id=spot.id,
                entry_time=datetime.now(timezone.utc),
                status=SessionStatus.ACTIVE,
            )
        )
    db_session.commit()

    response = client.put(
        f"/api/v1/owner/parking-lots/{lot['id']}/inventory",
        headers=headers,
        json={
            "inventory": [
                {
                    "vehicle_category_id": str(category.id),
                    "space_count": 1,
                    "price_per_minute": "150",
                    "price_per_day": None,
                    "price_per_month": None,
                }
            ]
        },
    )

    assert response.status_code == 409
    assert len(db_session.execute(
        select(ParkingSpot).where(
            ParkingSpot.parking_lot_id == uuid.UUID(lot["id"]),
            ParkingSpot.is_active.is_(True),
        )
    ).scalars().all()) == 2


def test_schedule_update_cannot_exclude_a_confirmed_reservation(client, db_session):
    owner_data, headers = _register(client, "schedule-owner@example.com")
    lot, category = _create_parking_lot(client, db_session, headers, "NIT-202")
    owner = db_session.get(User, uuid.UUID(owner_data["user"]["id"]))
    vehicle = Vehicle(
        plate="SCH123",
        vehicle_type=VehicleType.CAR,
        vehicle_category_id=category.id,
        owner_id=owner.id,
    )
    db_session.add(vehicle)
    db_session.flush()
    spot = db_session.execute(
        select(ParkingSpot)
        .where(ParkingSpot.parking_lot_id == uuid.UUID(lot["id"]))
        .order_by(ParkingSpot.code)
    ).scalars().first()
    local_date = datetime.now(COLOMBIA_TZ).date() + timedelta(days=3)
    local_start = datetime.combine(local_date, time(10), tzinfo=COLOMBIA_TZ)
    start = local_start.astimezone(timezone.utc)
    end = start + timedelta(hours=1)
    db_session.add(
        Reservation(
            vehicle_id=vehicle.id,
            spot_id=spot.id,
            parking_lot_id=uuid.UUID(lot["id"]),
            vehicle_type=VehicleType.CAR,
            start_time=start,
            end_time=end,
        )
    )
    db_session.commit()

    schedules = [
        {
            "day_of_week": day,
            "opens_at": None,
            "closes_at": None,
            "is_closed": day == local_date.weekday(),
            "is_24_hours": day != local_date.weekday(),
        }
        for day in range(7)
    ]
    response = client.put(
        f"/api/v1/owner/parking-lots/{lot['id']}/schedule",
        headers=headers,
        json={"schedules": schedules},
    )
    dashboard = client.get(
        f"/api/v1/owner/parking-lots/{lot['id']}/dashboard"
        f"?report_date={local_date.isoformat()}",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"].startswith("No puedes reducir el horario")
    assert dashboard.status_code == 200
    assert dashboard.json()["reservation_count"] == 1
    assert dashboard.json()["daily_reservations"][0]["plate"] == "SCH123"
