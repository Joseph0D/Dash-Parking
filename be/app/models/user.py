"""
Módulo: user.py (modelo)
Qué: Modelo ORM de usuarios (clientes, operarios, administradores).
Para qué: Sustento de RF-012 (autenticación por rol) y RF-016 (autoregistro de clientes).
Impacto: Es la raíz de todo el control de acceso — un error aquí compromete la seguridad
         de tarifas, reportes y eliminación de registros (RNF-001).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.CLIENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
