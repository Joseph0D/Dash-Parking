"""Schemas de tarifas (RF-007)."""
from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import VehicleType


class RateUpsertRequest(BaseModel):
    vehicle_type: VehicleType
    price_per_hour: Decimal = Field(..., gt=0)


class RateResponse(BaseModel):
    id: uuid.UUID
    vehicle_type: VehicleType
    price_per_hour: Decimal

    model_config = {"from_attributes": True}
