"""
Módulo: rate.py (modelo)
Qué: Modelo ORM de la tarifa vigente por tipo de vehículo.
Para qué: Sustento de RF-007 (administración de tarifas) y RF-005 (cálculo de cobro).
Impacto: Fuente de verdad del valor cobrado — un error aquí afecta a todos los cobros (RN-009).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import VehicleType
from app.models.guid import GUID


class Rate(Base):
    __tablename__ = "rates"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicle_type"), unique=True, nullable=False
    )
    price_per_hour: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
