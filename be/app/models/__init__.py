"""
Módulo: models/__init__.py
Qué: Reexporta todos los modelos ORM para que SQLAlchemy los registre contra `Base.metadata`.
Para qué: `Base.metadata.create_all()` (ver app/main.py) solo crea las tablas de los modelos
          que hayan sido importados al menos una vez en el proceso.
"""
from app.models.parking_lot import ParkingLot  # noqa: F401
from app.models.parking_lot_member import ParkingLotMember  # noqa: F401
from app.models.parking_lot_schedule import ParkingLotSchedule  # noqa: F401
from app.models.parking_rate import ParkingRate  # noqa: F401
from app.models.parking_session import ParkingSession  # noqa: F401
from app.models.parking_space_type import ParkingSpaceType  # noqa: F401
from app.models.parking_spot import ParkingSpot  # noqa: F401
from app.models.parking_zone import ParkingZone  # noqa: F401
from app.models.password_reset import PasswordResetAttempt, PasswordResetToken  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.qr_token import QRToken  # noqa: F401
from app.models.rate import Rate  # noqa: F401
from app.models.reservation import Reservation  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vehicle import Vehicle  # noqa: F401
from app.models.vehicle_category import VehicleCategory  # noqa: F401
from app.models.vehicle_qr_token import VehicleQRToken  # noqa: F401

__all__ = [
    "ParkingSession",
    "ParkingLot",
    "ParkingLotMember",
    "ParkingLotSchedule",
    "ParkingRate",
    "ParkingSpot",
    "ParkingSpaceType",
    "ParkingZone",
    "PasswordResetAttempt",
    "PasswordResetToken",
    "Payment",
    "QRToken",
    "Rate",
    "Reservation",
    "User",
    "VehicleCategory",
    "Vehicle",
    "VehicleQRToken",
]
