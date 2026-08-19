"""Schemas de sesiones de parqueo: ingreso, salida y cálculo de cobro (RF-001, RF-004, RF-005)."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import SessionStatus, VehicleType


class SessionEntryRequest(BaseModel):
    plate: str
    vehicle_type: VehicleType


class SessionResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    spot_id: uuid.UUID
    entry_time: datetime
    exit_time: datetime | None
    status: SessionStatus
    amount: Decimal | None

    model_config = {"from_attributes": True}


class SessionDetailResponse(SessionResponse):
    plate: str
    vehicle_type: VehicleType
    spot_code: str
    elapsed_seconds: int
    estimated_amount: Decimal


class SessionExitResponse(BaseModel):
    session: SessionResponse
    elapsed_hours_billed: int
    amount: Decimal
