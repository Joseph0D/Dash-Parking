"""Tarifa de un parqueadero por categoría y periodo de vigencia."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.guid import GUID


class ParkingRate(Base):
    __tablename__ = "parking_rates"
    __table_args__ = (
        CheckConstraint("price_per_minute > 0", name="ck_parking_rates_minute_positive"),
        CheckConstraint(
            "price_per_day IS NULL OR price_per_day > 0",
            name="ck_parking_rates_day_positive",
        ),
        CheckConstraint(
            "price_per_month IS NULL OR price_per_month > 0",
            name="ck_parking_rates_month_positive",
        ),
        CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="ck_parking_rates_valid_dates",
        ),
        UniqueConstraint(
            "parking_lot_id",
            "vehicle_category_id",
            "valid_from",
            name="uq_parking_rates_lot_category_start",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    parking_lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_category_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("vehicle_categories.id"), nullable=False, index=True
    )
    price_per_minute: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_day: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_per_month: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="rates")  # noqa: F821
    vehicle_category: Mapped["VehicleCategory"] = relationship()  # noqa: F821
