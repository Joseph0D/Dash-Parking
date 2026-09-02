"""
Módulo: seed.py
Qué: Crea datos iniciales: un administrador, tarifas por tipo de vehículo y espacios de ejemplo.
Para qué: Que el equipo pueda levantar el sistema por primera vez y tener con qué probar
          login de administrador, tarifas y flujo de ingreso sin cargar nada a mano.
Impacto: Si no corre, el sistema arranca sin tarifas (RF-005 fallaría con NoActiveRateError) y
         sin espacios (RF-002 fallaría con NoAvailableSpotError).

Uso: python -m app.scripts.seed   (ver GUIA-EJECUCION-LOCAL.md)
Es idempotente: se puede correr varias veces sin duplicar datos.
"""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import *  # noqa: F401,F403
from app.models.enums import SpotStatus, UserRole, VehicleType
from app.models.parking_spot import ParkingSpot
from app.models.rate import Rate
from app.models.user import User

DEFAULT_ADMIN_EMAIL = "admin@dashparking.dev"
DEFAULT_ADMIN_PASSWORD = "Admin123!"

DEFAULT_RATES = {
    VehicleType.CAR: Decimal("4000"),
    VehicleType.MOTORCYCLE: Decimal("2000"),
    VehicleType.BICYCLE: Decimal("1000"),
}

SPOTS_PER_TYPE = {
    VehicleType.CAR: 10,
    VehicleType.MOTORCYCLE: 8,
    VehicleType.BICYCLE: 6,
}

ZONE_BY_TYPE = {
    VehicleType.CAR: "Zona A",
    VehicleType.MOTORCYCLE: "Zona B",
    VehicleType.BICYCLE: "Zona C",
}

PREFIX_BY_TYPE = {
    VehicleType.CAR: "A",
    VehicleType.MOTORCYCLE: "B",
    VehicleType.BICYCLE: "C",
}


def seed_admin(db: Session) -> None:
    existing = db.execute(select(User).where(User.email == DEFAULT_ADMIN_EMAIL)).scalar_one_or_none()
    if existing is not None:
        print(f"[seed] Admin ya existe: {DEFAULT_ADMIN_EMAIL}")
        return
    admin = User(
        name="Administrador Dash Parking",
        email=DEFAULT_ADMIN_EMAIL,
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    print(f"[seed] Admin creado: {DEFAULT_ADMIN_EMAIL} / {DEFAULT_ADMIN_PASSWORD}")


def seed_rates(db: Session) -> None:
    for vehicle_type, price in DEFAULT_RATES.items():
        existing = db.execute(select(Rate).where(Rate.vehicle_type == vehicle_type)).scalar_one_or_none()
        if existing is None:
            db.add(Rate(vehicle_type=vehicle_type, price_per_hour=price))
            print(f"[seed] Tarifa creada: {vehicle_type.value} = ${price}/hora")


def seed_spots(db: Session) -> None:
    for vehicle_type, count in SPOTS_PER_TYPE.items():
        prefix = PREFIX_BY_TYPE[vehicle_type]
        zone = ZONE_BY_TYPE[vehicle_type]
        for i in range(1, count + 1):
            code = f"{prefix}-{i:02d}"
            existing = db.execute(select(ParkingSpot).where(ParkingSpot.code == code)).scalar_one_or_none()
            if existing is None:
                db.add(ParkingSpot(code=code, zone=zone, vehicle_type=vehicle_type, status=SpotStatus.AVAILABLE))
        print(f"[seed] {count} espacios asegurados en {zone} ({vehicle_type.value})")


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_rates(db)
        seed_spots(db)
        db.commit()
        print("[seed] Completado.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
