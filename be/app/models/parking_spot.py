"""
Módulo: parking_spot.py (modelo)
Qué: Modelo ORM de un espacio físico del parqueadero.
Para qué: Sustento de RF-002 (asignación automática) y RF-003 (consulta de ocupación).
Impacto: Es la entidad que garantiza RN-004 (un espacio no puede tener dos vehículos a la vez).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import SpotStatus, VehicleType


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # ej. "A-01"
    zone: Mapped[str] = mapped_column(String(20), nullable=False)  # ej. "Zona A"
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, name="vehicle_type"), nullable=False)
    status: Mapped[SpotStatus] = mapped_column(
        Enum(SpotStatus, name="spot_status"), nullable=False, default=SpotStatus.AVAILABLE
    )
