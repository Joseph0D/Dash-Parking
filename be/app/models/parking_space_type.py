"""Catálogo de características físicas de un espacio de parqueo."""
from __future__ import annotations

import uuid

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.guid import GUID


class ParkingSpaceType(Base):
    __tablename__ = "parking_space_types"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
