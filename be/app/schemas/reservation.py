"""Schemas de reservas (RF-013)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ReservationStatus, VehicleType


class ReservationCreateRequest(BaseModel):
    vehicle_id: uuid.UUID
    vehicle_type: VehicleType
    start_time: datetime
    duration_hours: float = Field(..., gt=0, le=24)

    @model_validator(mode="after")
    def validate_start_time(self) -> "ReservationCreateRequest":
        # Se compara en el service contra "ahora" (con tz), aquí solo garantizamos tipo correcto.
        return self


class ReservationResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    spot_id: uuid.UUID
    vehicle_type: VehicleType
    start_time: datetime
    end_time: datetime
    status: ReservationStatus

    model_config = {"from_attributes": True}
