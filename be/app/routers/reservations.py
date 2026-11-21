"""
Router: reservations.py
Qué: Reservar y cancelar espacios de parqueo con tiempo de ocupación (RF-013).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.core.deps import require_staff
from app.database import get_db
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.reservation import ReservationCreateRequest, ReservationResponse
from app.services.reservation_service import (
    NoAvailableSpotForReservationError,
    ReservationInThePastError,
    ReservationCannotBeCancelledError,
    cancel_reservation,
    create_reservation,
)

router = APIRouter(prefix="/api/v1/reservations", tags=["reservations"])


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: ReservationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    vehicle = db.get(Vehicle, payload.vehicle_id)
    if vehicle is None or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    parking_lot = db.get(ParkingLot, payload.parking_lot_id)
    if parking_lot is None or not parking_lot.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parqueadero no encontrado")

    try:
        reservation = create_reservation(
            db, parking_lot, vehicle, payload.start_time, payload.end_time
        )
    except ReservationInThePastError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except NoAvailableSpotForReservationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ReservationResponse.model_validate(reservation)


@router.get("/me", response_model=list[ReservationResponse])
def my_reservations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ReservationResponse]:
    reservations = (
        db.execute(
            select(Reservation)
            .join(Vehicle, Vehicle.id == Reservation.vehicle_id)
            .where(Vehicle.owner_id == current_user.id)
            .options(
                selectinload(Reservation.parking_lot),
                selectinload(Reservation.spot).selectinload(ParkingSpot.parking_lot),
            )
            .order_by(Reservation.start_time.desc())
        )
        .scalars()
        .all()
    )
    return [ReservationResponse.model_validate(r) for r in reservations]


@router.delete("/{reservation_id}", response_model=ReservationResponse)
def cancel(
    reservation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    reservation = db.get(Reservation, reservation_id)
    if reservation is None or reservation.vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    try:
        return ReservationResponse.model_validate(cancel_reservation(db, reservation))
    except ReservationCannotBeCancelledError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("", response_model=list[ReservationResponse])
def list_reservations(_staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    reservations = db.execute(
        select(Reservation)
        .options(selectinload(Reservation.parking_lot))
        .order_by(Reservation.start_time.desc())
    ).scalars().all()
    return [ReservationResponse.model_validate(r) for r in reservations]
