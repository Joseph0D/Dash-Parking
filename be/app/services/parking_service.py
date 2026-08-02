"""
Módulo: parking_service.py
Qué: Lógica de negocio para el registro de ingreso de vehículos y asignación de espacios.
Para qué: Centraliza las reglas del parqueadero (Necesidad 1 y 2) fuera del router HTTP,
          para que puedan probarse y reutilizarse sin depender de FastAPI.
Impacto: Si falla, un vehículo podría ingresar sin espacio asignado o duplicar un ingreso
         ya registrado, rompiendo la trazabilidad exigida por el informe de diseño.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.models.vehicle import ParkingSpot, Vehicle, VehicleType


class VehicleAlreadyInsideError(Exception):
    """Se lanza cuando se intenta registrar el ingreso de una placa ya presente (RF01)."""


class NoAvailableSpotError(Exception):
    """Se lanza cuando no hay espacios libres para asignar (Necesidad 2)."""


class ParkingService:
    """
    Orquesta el registro de ingreso de vehículos sobre un conjunto de espacios en memoria.

    Nota de alcance (Sprint 0): el almacenamiento es en memoria a propósito. La persistencia
    real en PostgreSQL se construye en el Sprint 1 (Semana 2), según la progresión del
    bootcamp — este servicio ya expone la interfaz que el router y las pruebas necesitan,
    de forma que migrar a un repositorio real no cambie su contrato público.
    """

    def __init__(self, spots: list[ParkingSpot]) -> None:
        self._spots = {spot.spot_number: spot for spot in spots}
        self._vehicles_inside: dict[str, Vehicle] = {}

    def register_entry(self, plate: str, vehicle_type: VehicleType) -> tuple[Vehicle, ParkingSpot]:
        """
        Registra el ingreso de un vehículo y le asigna el primer espacio disponible.

        Lanza VehicleAlreadyInsideError si la placa ya está registrada como dentro,
        y NoAvailableSpotError si no hay espacios libres (RF01, RF05).
        """
        vehicle = Vehicle(
            plate=plate,
            vehicle_type=vehicle_type,
            entry_time=datetime.now(timezone.utc),
        )

        if vehicle.plate in self._vehicles_inside:
            raise VehicleAlreadyInsideError(
                f"El vehículo {vehicle.plate} ya se encuentra dentro del parqueadero"
            )

        spot = self._first_available_spot()
        if spot is None:
            raise NoAvailableSpotError("No hay espacios disponibles en este momento")

        spot.assign(vehicle.plate)
        self._vehicles_inside[vehicle.plate] = vehicle
        return vehicle, spot

    def _first_available_spot(self) -> ParkingSpot | None:
        for spot in self._spots.values():
            if spot.is_available:
                return spot
        return None
