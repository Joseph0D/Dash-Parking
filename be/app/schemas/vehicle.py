"""Schemas de vehículos (RF-001, RF-010)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import VehicleType


class VehicleCreateRequest(BaseModel):
    plate: str = Field(..., min_length=1, max_length=10)
    vehicle_type: VehicleType
    model: str | None = Field(default=None, max_length=120)


class VehicleResponse(BaseModel):
    id: uuid.UUID
    plate: str
    vehicle_type: VehicleType
    model: str | None
    owner_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
