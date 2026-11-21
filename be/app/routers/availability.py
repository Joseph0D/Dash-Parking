"""
Router: availability.py
Qué: Disponibilidad de espacios por parqueadero y franja horaria (elegir parqueadero, tipo de
     vehículo, fecha y hora).
Para qué: Alimentar la pantalla pública "Disponibilidad"; la creación de reservas exige sesión.
Impacto: Si falla, el cliente no puede ver qué horarios tienen espacio antes de reservar.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.availability import (
    AvailabilityResponse,
    ParkingLotResponse,
    SpacesResponse,
    VehicleTypeResponse,
)
from app.services import availability_service as service

router = APIRouter(prefix="/api/v1/parking-lots", tags=["availability"])


@contextmanager
def _translate_errors() -> Iterator[None]:
    """Traduce errores del servicio a HTTP: 404 si no existe, 422 si la franja es inválida,
    503 si la base de datos no responde."""
    try:
        yield
    except service.NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except service.InvalidTimeWindowError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except service.OutsideOperatingHoursError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except OperationalError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "La base de datos no está disponible",
        ) from exc


def _window(
    start: datetime = Query(..., description="Inicio de la franja (hora Colombia o ISO con zona)"),
    end: datetime = Query(..., description="Fin de la franja"),
) -> tuple[datetime, datetime]:
    with _translate_errors():
        return service.normalize_window(start, end)


@router.get("", response_model=list[ParkingLotResponse])
def list_parking_lots(db: Session = Depends(get_db)) -> list[ParkingLotResponse]:
    with _translate_errors():
        return service.list_parking_lots(db)


@router.get("/{parking_lot_id}/vehicle-types", response_model=list[VehicleTypeResponse])
def list_vehicle_types(
    parking_lot_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[VehicleTypeResponse]:
    with _translate_errors():
        return service.list_vehicle_types(db, parking_lot_id)


@router.get("/{parking_lot_id}/availability", response_model=AvailabilityResponse)
def get_availability(
    parking_lot_id: uuid.UUID,
    window: tuple[datetime, datetime] = Depends(_window),
    db: Session = Depends(get_db),
) -> AvailabilityResponse:
    with _translate_errors():
        return service.get_zone_availability(db, parking_lot_id, *window)


@router.get("/{parking_lot_id}/spaces", response_model=SpacesResponse)
def get_spaces(
    parking_lot_id: uuid.UUID,
    vehicle_type_id: uuid.UUID = Query(..., description="Tipo de vehículo (ver /vehicle-types)"),
    window: tuple[datetime, datetime] = Depends(_window),
    db: Session = Depends(get_db),
) -> SpacesResponse:
    with _translate_errors():
        return service.get_spaces(db, parking_lot_id, vehicle_type_id, *window)
