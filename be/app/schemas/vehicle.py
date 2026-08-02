"""
Módulo: vehicle.py (schemas)
Qué: DTOs de entrada/salida del endpoint de ingreso de vehículos.
Para qué: Separa el contrato HTTP del modelo de dominio (app/models/vehicle.py) para poder
          evolucionar ambos de forma independiente.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.vehicle import VehicleType


class VehicleEntryRequest(BaseModel):
    """Datos que el operario ingresa para registrar el ingreso de un vehículo (RF01-RF04)."""

    plate: str = Field(..., min_length=1, max_length=10, examples=["ABC123"])
    vehicle_type: VehicleType


class VehicleEntryResponse(BaseModel):
    """Confirmación del ingreso registrado, incluyendo el espacio asignado (RF05)."""

    plate: str
    vehicle_type: VehicleType
    entry_time: datetime
    assigned_spot: str
