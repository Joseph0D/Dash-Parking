"""
Módulo: vehicle.py
Qué: Entidades de dominio del proceso de ingreso/salida de vehículos.
Para qué: Modelan las reglas del parqueadero (Necesidad 1 y 2 del informe de diseño) sin
          depender todavía de un motor de persistencia — eso se agrega en el Sprint 1
          (Semana 2 — Dominio y Persistencia), según docs/estandar-codigo-template.md.
Impacto: Si el modelo aquí es incorrecto, toda la lógica de negocio construida encima
         (cálculo de cobro, ocupación, reportes) hereda el error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VehicleType(str, Enum):
    """Tipos de vehículo soportados por el parqueadero (RF04)."""

    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"


@dataclass
class Vehicle:
    """Vehículo registrado en un ingreso (RF01-RF04)."""

    plate: str
    vehicle_type: VehicleType
    entry_time: datetime
    exit_time: datetime | None = None

    def __post_init__(self) -> None:
        # La placa es el identificador de negocio: se normaliza para evitar duplicados
        # por diferencias de mayúsculas/espacios (ej. "abc123" vs "ABC 123").
        self.plate = self.plate.strip().upper().replace(" ", "")
        if not self.plate:
            raise ValueError("La placa del vehículo no puede estar vacía")

    @property
    def is_inside(self) -> bool:
        """True si el vehículo aún no tiene registrada una salida."""
        return self.exit_time is None

    def register_exit(self, exit_time: datetime) -> None:
        """Registra la hora de salida del vehículo (RF07)."""
        if not self.is_inside:
            raise ValueError(f"El vehículo {self.plate} ya tiene una salida registrada")
        if exit_time < self.entry_time:
            raise ValueError("La hora de salida no puede ser anterior a la hora de ingreso")
        self.exit_time = exit_time


@dataclass
class ParkingSpot:
    """Espacio físico del parqueadero (Necesidad 2: control de disponibilidad)."""

    spot_number: str
    occupied_by: str | None = field(default=None)  # placa del vehículo que lo ocupa

    @property
    def is_available(self) -> bool:
        return self.occupied_by is None

    def assign(self, plate: str) -> None:
        """Asigna el espacio a un vehículo. Falla si ya está ocupado (RF05)."""
        if not self.is_available:
            raise ValueError(f"El espacio {self.spot_number} ya está ocupado")
        self.occupied_by = plate

    def release(self) -> None:
        """Libera el espacio cuando el vehículo sale (RF10)."""
        self.occupied_by = None
