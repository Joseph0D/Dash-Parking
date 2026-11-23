"""
Módulo: parking_spot.py (modelo)
Qué: Modelo ORM de un espacio físico del parqueadero.
Para qué: Sustento de RF-002 (asignación automática) y RF-003 (consulta de ocupación).
Impacto: Es la entidad que garantiza RN-004 (un espacio no puede tener dos vehículos a la vez).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import SpotStatus, VehicleType
from app.models.guid import GUID


class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    __table_args__ = (
        UniqueConstraint("legacy_id", name="uq_parking_spots_legacy_id"),
        UniqueConstraint("parking_lot_id", "code", name="uq_parking_spots_lot_code"),
        Index(
            "uq_parking_spots_unassigned_code",
            "code",
            unique=True,
            postgresql_where=text("parking_lot_id IS NULL"),
            sqlite_where=text("parking_lot_id IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), nullable=False)  # ej. "A-01"
    zone: Mapped[str] = mapped_column(String(100), nullable=False)  # ej. "Zona A"
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicle_type"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    parking_lot_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("parking_lots.id", name="fk_parking_spots_lot"), nullable=True
    )
    parking_zone_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("parking_zones.id", name="fk_parking_spots_zone"), nullable=True
    )
    vehicle_category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("vehicle_categories.id", name="fk_parking_spots_vehicle_category"),
        nullable=True,
    )
    space_type_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("parking_space_types.id", name="fk_parking_spots_space_type"),
        nullable=True,
    )
    legacy_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[SpotStatus] = mapped_column(
        Enum(SpotStatus, name="spot_status"), nullable=False, default=SpotStatus.AVAILABLE
    )

    parking_lot: Mapped["ParkingLot | None"] = relationship(
        back_populates="spots", foreign_keys=[parking_lot_id]
    )  # noqa: F821
    parking_zone: Mapped["ParkingZone | None"] = relationship(
        back_populates="spots", foreign_keys=[parking_zone_id]
    )  # noqa: F821
    vehicle_category: Mapped["VehicleCategory | None"] = relationship()  # noqa: F821
    space_type: Mapped["ParkingSpaceType | None"] = relationship()  # noqa: F821
