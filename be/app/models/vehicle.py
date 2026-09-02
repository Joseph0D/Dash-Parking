"""
Módulo: vehicle.py (modelo)
Qué: Modelo ORM del vehículo registrado por un cliente.
Para qué: Sustento de RF-001 (ingreso) y RF-010/HU-010 (asociación cliente-vehículo).
Impacto: Si falla la normalización de placa, se rompe la regla RN-001 de unicidad por placa.

Nota de migración: en el Sprint 0 este archivo contenía una entidad de dominio en memoria
(dataclass, sin persistencia). Este entregable la reemplaza por el modelo ORM real sobre
PostgreSQL, cumpliendo RNF-004.3 (almacenamiento permanente).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import VehicleType
from app.models.guid import GUID


def normalize_plate(plate: str) -> str:
    """Normaliza una placa: mayúsculas, sin espacios (RN-001)."""
    return plate.strip().upper().replace(" ", "")


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (UniqueConstraint("plate", name="uq_vehicles_plate"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    plate: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, name="vehicle_type"), nullable=False)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner: Mapped["User"] = relationship(back_populates="vehicles")  # noqa: F821
