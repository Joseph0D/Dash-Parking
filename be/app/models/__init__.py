"""
Módulo: models/__init__.py
Qué: Reexporta todos los modelos ORM para que SQLAlchemy los registre contra `Base.metadata`.
Para qué: `Base.metadata.create_all()` (ver app/main.py) solo crea las tablas de los modelos
          que hayan sido importados al menos una vez en el proceso.
"""
from app.models.parking_session import ParkingSession  # noqa: F401
from app.models.parking_spot import ParkingSpot  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.qr_token import QRToken  # noqa: F401
from app.models.rate import Rate  # noqa: F401
from app.models.reservation import Reservation  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vehicle import Vehicle  # noqa: F401

__all__ = [
    "ParkingSession",
    "ParkingSpot",
    "Payment",
    "QRToken",
    "Rate",
    "Reservation",
    "User",
    "Vehicle",
]
