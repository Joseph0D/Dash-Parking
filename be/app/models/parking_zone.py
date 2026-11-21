"""Zona física de un parqueadero, asociada a un tipo de vehículo."""
from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.guid import GUID


class ParkingZone(Base):
    __tablename__ = "parking_zones"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_parking_zones_capacity_positive"),
        UniqueConstraint("parking_lot_id", "name", name="uq_parking_zones_lot_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    parking_lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("parking_lots.id"), nullable=False, index=True
    )
    vehicle_category_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("vehicle_categories.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="zones")  # noqa: F821
    vehicle_category: Mapped["VehicleCategory"] = relationship()  # noqa: F821
    spots: Mapped[list["ParkingSpot"]] = relationship(
        back_populates="parking_zone", foreign_keys="ParkingSpot.parking_zone_id"
    )  # noqa: F821
