"""Modelo del parqueadero y su propietario dentro de la base UUID."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.guid import GUID


class ParkingLot(Base):
    __tablename__ = "parking_lots"
    __table_args__ = (
        CheckConstraint("total_capacity > 0", name="ck_parking_lots_capacity_positive"),
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_parking_lots_latitude_range",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_parking_lots_longitude_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    identification: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner: Mapped["User | None"] = relationship(back_populates="parking_lots")  # noqa: F821
    zones: Mapped[list["ParkingZone"]] = relationship(
        back_populates="parking_lot", cascade="all, delete-orphan"
    )  # noqa: F821
    spots: Mapped[list["ParkingSpot"]] = relationship(
        back_populates="parking_lot", foreign_keys="ParkingSpot.parking_lot_id"
    )  # noqa: F821
    schedules: Mapped[list["ParkingLotSchedule"]] = relationship(
        back_populates="parking_lot", cascade="all, delete-orphan"
    )  # noqa: F821
    rates: Mapped[list["ParkingRate"]] = relationship(
        back_populates="parking_lot", cascade="all, delete-orphan"
    )  # noqa: F821
    memberships: Mapped[list["ParkingLotMember"]] = relationship(
        back_populates="parking_lot", cascade="all, delete-orphan"
    )  # noqa: F821
