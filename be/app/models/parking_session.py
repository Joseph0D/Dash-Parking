"""
Módulo: parking_session.py (modelo)
Qué: Modelo ORM de una sesión de parqueo (desde el ingreso hasta la salida pagada).
Para qué: Sustento de RF-001, RF-004 y RF-005 — es la entidad central del flujo operativo.
Impacto: Si falla, se pierde la trazabilidad completa entre ingreso, salida, tiempo y cobro.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import SessionStatus
from app.models.guid import GUID


class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("vehicles.id"), nullable=False)
    spot_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("parking_spots.id"), nullable=False)
    reservation_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("reservations.id"), nullable=True
    )

    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"), nullable=False, default=SessionStatus.ACTIVE
    )
    amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    vehicle: Mapped["Vehicle"] = relationship()  # noqa: F821
    spot: Mapped["ParkingSpot"] = relationship()  # noqa: F821
    payments: Mapped[list["Payment"]] = relationship(back_populates="session")  # noqa: F821
