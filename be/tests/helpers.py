"""Utilidades compartidas entre tests para reducir repetición de setup."""
from __future__ import annotations

from app.core.security import hash_password
from app.models.enums import UserRole, VehicleType
from app.models.rate import Rate
from app.models.user import User


def create_user(db_session, email: str, role: UserRole = UserRole.CLIENT, password: str = "supersecret1") -> User:
    user = User(name="Test User", email=email, password_hash=hash_password(password), role=role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def auth_headers(client, email: str, password: str = "supersecret1") -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_rate(db_session, vehicle_type: VehicleType = VehicleType.CAR, price: str = "4000") -> Rate:
    from decimal import Decimal

    rate = Rate(vehicle_type=vehicle_type, price_per_hour=Decimal(price))
    db_session.add(rate)
    db_session.commit()
    return rate


def seed_spot(db_session, code: str = "A-01", vehicle_type: VehicleType = VehicleType.CAR):
    from app.models.parking_spot import ParkingSpot

    spot = ParkingSpot(code=code, zone="Zona A", vehicle_type=vehicle_type)
    db_session.add(spot)
    db_session.commit()
    return spot
