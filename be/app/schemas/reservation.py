"""Schemas de reservas (RF-013)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, model_validator

from app.models.enums import ReservationStatus, VehicleType

COLOMBIA_TZ = timezone(timedelta(hours=-5))


class ReservationCreateRequest(BaseModel):
    vehicle_id: uuid.UUID
    parking_lot_id: uuid.UUID
    spot_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_time_window(self) -> "ReservationCreateRequest":
        start = self.start_time
        end = self.end_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=COLOMBIA_TZ)
        if end.tzinfo is None:
            end = end.replace(tzinfo=COLOMBIA_TZ)
        if end <= start:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return self


class ReservationResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    spot_id: uuid.UUID
    parking_lot_id: uuid.UUID | None
    parking_lot_name: str | None = None
    vehicle_type: VehicleType
    start_time: datetime
    end_time: datetime
    status: ReservationStatus

    model_config = {"from_attributes": True}
