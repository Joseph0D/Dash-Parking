"""
Router: sessions.py
Qué: Registro de ingreso/salida y consulta de la sesión activa (RF-001, RF-002, RF-003, RF-004, RF-005).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_staff
from app.database import get_db
from app.models.enums import SessionStatus
from app.models.parking_session import ParkingSession
from app.models.rate import Rate
from app.models.user import User
from app.models.vehicle import Vehicle, normalize_plate
from app.schemas.session import SessionDetailResponse, SessionEntryRequest, SessionResponse
from app.services.fee_service import calculate_amount, elapsed_seconds
from app.services.parking_service import (
    NoAvailableSpotError,
    VehicleAlreadyInsideError,
    get_active_session_for_plate,
    register_entry,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def _to_detail(db: Session, session: ParkingSession) -> SessionDetailResponse:
    rate = db.execute(select(Rate).where(Rate.vehicle_type == session.vehicle.vehicle_type)).scalar_one_or_none()
    seconds = elapsed_seconds(session.entry_time)
    estimated = calculate_amount(session.entry_time, rate.price_per_hour) if rate else 0
    return SessionDetailResponse(
        **SessionResponse.model_validate(session).model_dump(),
        plate=session.vehicle.plate,
        vehicle_type=session.vehicle.vehicle_type,
        spot_code=session.spot.code,
        elapsed_seconds=seconds,
        estimated_amount=estimated,
    )


@router.post("/entry", response_model=SessionDetailResponse, status_code=status.HTTP_201_CREATED)
def entry(
    payload: SessionEntryRequest,
    _staff: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> SessionDetailResponse:
    """Registra el ingreso de un vehículo (RF-001). Reservado a operario/administrador."""
    plate = normalize_plate(payload.plate)
    vehicle = db.execute(select(Vehicle).where(Vehicle.plate == plate)).scalar_one_or_none()
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La placa no está registrada como vehículo")

    try:
        session = register_entry(db, vehicle)
    except VehicleAlreadyInsideError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except NoAvailableSpotError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _to_detail(db, session)


@router.get("/active", response_model=list[SessionDetailResponse])
def list_active_sessions(_staff: User = Depends(require_staff), db: Session = Depends(get_db)) -> list[SessionDetailResponse]:
    """Vehículos actualmente dentro del parqueadero (RF-003). Vista de administración."""
    sessions = db.execute(select(ParkingSession).where(ParkingSession.status == SessionStatus.ACTIVE)).scalars().all()
    return [_to_detail(db, s) for s in sessions]


@router.get("/me/active", response_model=SessionDetailResponse | None)
def my_active_session(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Sesión activa del cliente autenticado (para el panel de usuario)."""
    session = db.execute(
        select(ParkingSession)
        .join(Vehicle, Vehicle.id == ParkingSession.vehicle_id)
        .where(Vehicle.owner_id == current_user.id, ParkingSession.status == SessionStatus.ACTIVE)
    ).scalar_one_or_none()
    return _to_detail(db, session) if session else None


@router.get("/by-plate/{plate}", response_model=SessionDetailResponse)
def get_by_plate(plate: str, _staff: User = Depends(require_staff), db: Session = Depends(get_db)) -> SessionDetailResponse:
    """Búsqueda de la sesión activa por placa, para el flujo de salida (RF-004)."""
    session = get_active_session_for_plate(db, plate)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay una sesión activa con esa placa")
    return _to_detail(db, session)


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SessionDetailResponse:
    session = db.get(ParkingSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    if session.vehicle.owner_id != current_user.id and current_user.role.value == "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes ver esta sesión")
    return _to_detail(db, session)
