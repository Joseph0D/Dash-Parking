"""
Módulo: reservation.py (modelo)
Qué: Modelo ORM de una reserva de espacio (RF-013).
Para qué: Permitir a un cliente asegurar un espacio antes de llegar, por un rango de tiempo.
Impacto: Si el rango se calcula mal, se pueden generar dobles reservas (RN-022).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ReservationStatus, VehicleType
from app.models.guid import GUID


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_reservations_time_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("vehicles.id"), nullable=False)
    spot_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("parking_spots.id"), nullable=False)
    parking_lot_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("parking_lots.id", name="fk_reservations_parking_lot"), nullable=True
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, name="vehicle_type"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status"), nullable=False, default=ReservationStatus.CONFIRMED
    )

    vehicle: Mapped["Vehicle"] = relationship()  # noqa: F821
    spot: Mapped["ParkingSpot"] = relationship()  # noqa: F821
    parking_lot: Mapped["ParkingLot | None"] = relationship()  # noqa: F821

    @property
    def parking_lot_name(self) -> str | None:
        if self.parking_lot is not None:
            return self.parking_lot.name
        if self.spot is not None and self.spot.parking_lot is not None:
            return self.spot.parking_lot.name
        return None
