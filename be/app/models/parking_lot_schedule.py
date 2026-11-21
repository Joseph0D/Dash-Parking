"""Horario semanal del parqueadero; puede marcar días cerrados o de operación 24/7."""
from __future__ import annotations

import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    SmallInteger,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.guid import GUID


class ParkingLotSchedule(Base):
    __tablename__ = "parking_lot_schedules"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_parking_schedule_day"),
        CheckConstraint(
            "(is_closed AND opens_at IS NULL AND closes_at IS NULL AND NOT is_24_hours) OR "
            "(NOT is_closed AND ((is_24_hours AND opens_at IS NULL AND closes_at IS NULL) OR "
            "(NOT is_24_hours AND opens_at IS NOT NULL AND closes_at IS NOT NULL "
            "AND opens_at <> closes_at)))",
            name="ck_parking_schedule_hours",
        ),
        UniqueConstraint("parking_lot_id", "day_of_week", name="uq_parking_schedule_day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    parking_lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    opens_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    closes_at: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_24_hours: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="schedules")  # noqa: F821
