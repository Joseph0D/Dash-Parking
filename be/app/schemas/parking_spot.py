"""Schemas de espacios de parqueo (RF-002, RF-003)."""
from __future__ import annotations

import uuid

from pydantic import BaseModel

from app.models.enums import SpotStatus, VehicleType


class ParkingSpotResponse(BaseModel):
    id: uuid.UUID
    code: str
    zone: str
    vehicle_type: VehicleType
    status: SpotStatus

    model_config = {"from_attributes": True}


class OccupancySummary(BaseModel):
    total_spots: int
    occupied_spots: int
    available_spots: int
    reserved_spots: int
    spots: list[ParkingSpotResponse]
