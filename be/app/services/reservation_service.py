"""
Módulo: reservation_service.py
Qué: Orquesta la creación y cancelación de reservas de espacio (RF-013).
Para qué: Centraliza la regla de no-solapamiento de reservas (RN-022).
Impacto: Si falla, dos clientes podrían reservar el mismo espacio en el mismo rango horario.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.enums import ReservationStatus, SpotStatus
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.vehicle import Vehicle


class ReservationInThePastError(Exception):
    """La hora de inicio de la reserva ya pasó."""


class NoAvailableSpotForReservationError(Exception):
    """No hay ningún espacio de ese tipo libre para todo el rango solicitado (RN-022)."""


def create_reservation(
    db: Session,
    vehicle: Vehicle,
    start_time: datetime,
    duration_hours: float,
) -> Reservation:
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)

    if start_time < datetime.now(timezone.utc):
        raise ReservationInThePastError("La fecha/hora de la reserva debe ser futura")

    end_time = start_time + timedelta(hours=duration_hours)

    candidate_spots = db.execute(
        select(ParkingSpot).where(ParkingSpot.vehicle_type == vehicle.vehicle_type)
    ).scalars().all()

    for spot in candidate_spots:
        overlapping = db.execute(
            select(Reservation).where(
                Reservation.spot_id == spot.id,
                Reservation.status == ReservationStatus.CONFIRMED,
                and_(Reservation.start_time < end_time, Reservation.end_time > start_time),
            )
        ).scalar_one_or_none()
        if overlapping is None:
            reservation = Reservation(
                vehicle_id=vehicle.id,
                spot_id=spot.id,
                vehicle_type=vehicle.vehicle_type,
                start_time=start_time,
                end_time=end_time,
                status=ReservationStatus.CONFIRMED,
            )
            db.add(reservation)
            spot.status = SpotStatus.RESERVED
            db.commit()
            db.refresh(reservation)
            return reservation

    raise NoAvailableSpotForReservationError(
        "No hay espacios disponibles de este tipo para el rango de tiempo solicitado"
    )


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    reservation.status = ReservationStatus.CANCELLED
    # Solo se libera el espacio si no fue ya tomado por una sesión activa distinta.
    spot = reservation.spot
    if spot.status == SpotStatus.RESERVED:
        spot.status = SpotStatus.AVAILABLE
    db.commit()
    db.refresh(reservation)
    return reservation
