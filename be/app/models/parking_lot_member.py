"""Vínculo de un operario con los parqueaderos que puede operar."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.guid import GUID


class ParkingLotMember(Base):
    __tablename__ = "parking_lot_members"
    __table_args__ = (
        UniqueConstraint("parking_lot_id", "user_id", name="uq_parking_lot_member"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    parking_lot_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="memberships")  # noqa: F821
    user: Mapped["User"] = relationship(
        back_populates="parking_memberships", foreign_keys=[user_id]
    )  # noqa: F821
    created_by_user: Mapped["User"] = relationship(foreign_keys=[created_by])  # noqa: F821
