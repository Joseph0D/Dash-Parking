"""
Módulo: vehicles.py (router)
Qué: Endpoint mínimo para registrar el ingreso de un vehículo.
Para qué: Es el primer código real de dominio del proyecto (Sprint 0), cerrando el
          requisito de la Semana 1 de tener "código real, no un hello world vacío".
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.vehicle import VehicleEntryRequest, VehicleEntryResponse
from app.services.parking_service import (
    NoAvailableSpotError,
    ParkingService,
    VehicleAlreadyInsideError,
)
from app.models.vehicle import ParkingSpot

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])

# Sprint 0: 5 espacios de ejemplo en memoria. Se reemplaza por datos reales de PostgreSQL
# a partir del Sprint 1 (ver docs/estandar-codigo-template.md, sección 6).
_parking_service = ParkingService(
    spots=[ParkingSpot(spot_number=f"A-{i}") for i in range(1, 6)]
)


@router.post(
    "/entry",
    response_model=VehicleEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_vehicle_entry(payload: VehicleEntryRequest) -> VehicleEntryResponse:
    """Registra el ingreso de un vehículo y le asigna un espacio disponible (RF01-RF05)."""
    try:
        vehicle, spot = _parking_service.register_entry(
            plate=payload.plate,
            vehicle_type=payload.vehicle_type,
        )
    except VehicleAlreadyInsideError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except NoAvailableSpotError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return VehicleEntryResponse(
        plate=vehicle.plate,
        vehicle_type=vehicle.vehicle_type,
        entry_time=vehicle.entry_time,
        assigned_spot=spot.spot_number,
    )
