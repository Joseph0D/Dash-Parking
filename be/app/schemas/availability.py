"""Schemas de disponibilidad por franja horaria (parqueaderos, zonas y espacios)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class SpaceStatus(StrEnum):
    """Estado de un espacio PARA UNA FRANJA (no es un estado fijo del espacio)."""

    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


class ParkingLotResponse(BaseModel):
    id: int
    name: str
    identification: str
    address: str
    phone: str
    total_capacity: int


class VehicleTypeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price_per_hour: Decimal | None  # None si el parqueadero no tiene tarifa vigente para el tipo


class ZoneAvailability(BaseModel):
    zone_id: int
    zone_name: str
    vehicle_type_id: int
    capacity: int
    available: int
    reserved: int
    occupied: int


class AvailabilityResponse(BaseModel):
    parking_lot_id: int
    start: datetime
    end: datetime
    zones: list[ZoneAvailability]


class SpaceResponse(BaseModel):
    id: int
    code: str
    zone_id: int
    zone_name: str
    space_type_id: int
    status: SpaceStatus


class SpacesResponse(BaseModel):
    parking_lot_id: int
    vehicle_type_id: int
    start: datetime
    end: datetime
    estimated_price: Decimal | None
    available_count: int
    spaces: list[SpaceResponse]
