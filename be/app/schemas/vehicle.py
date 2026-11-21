"""Schemas de vehículos (RF-001, RF-010)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import VehicleType


class VehicleCreateRequest(BaseModel):
    plate: str | None = Field(default=None, min_length=1, max_length=10)
    vehicle_type: VehicleType
    brand: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    color: str | None = Field(default=None, max_length=60)

    @model_validator(mode="after")
    def validate_plate_and_required_fields(self) -> "VehicleCreateRequest":
        if self.vehicle_type not in {VehicleType.BICYCLE, VehicleType.SCOOTER}:
            if not self.plate:
                raise ValueError("La placa es obligatoria para este tipo de vehículo")
        return self


class VehicleUpdateRequest(BaseModel):
    plate: str | None = Field(default=None, min_length=1, max_length=10)
    vehicle_type: VehicleType
    brand: str = Field(..., min_length=1, max_length=120)
    model: str = Field(..., min_length=1, max_length=120)
    color: str = Field(..., min_length=1, max_length=60)


class VehicleResponse(BaseModel):
    id: uuid.UUID
    plate: str | None
    vehicle_type: VehicleType
    vehicle_category_id: uuid.UUID | None
    brand: str | None
    model: str | None
    color: str | None
    owner_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class VehicleQRPassResponse(BaseModel):
    token: str
    qr_image_base64: str
    vehicle_id: uuid.UUID
    plate: str | None
