"""
Módulo: reservation_service.py
Qué: Orquesta la creación y cancelación de reservas de espacio (RF-013).
Para qué: Centraliza la regla de no-solapamiento de reservas (RN-022).
Impacto: Si falla, dos clientes podrían reservar el mismo espacio en el mismo rango horario.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import ReservationStatus, SessionStatus
from app.models.parking_lot import ParkingLot
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.vehicle_category import VehicleCategory
from app.models.vehicle import Vehicle
from app.services.availability_service import (
    COLOMBIA_TZ,
    OutsideOperatingHoursError,
    ScheduleNotConfiguredError,
    ensure_schedule_covers,
)


class ReservationInThePastError(Exception):
    """La hora de inicio de la reserva ya pasó."""


class NoAvailableSpotForReservationError(Exception):
    """No hay ningún espacio de ese tipo libre para todo el rango solicitado (RN-022)."""


class ReservationCannotBeCancelledError(Exception):
    """La reserva ya empezó o ya no está activa."""


def create_reservation(
    db: Session,
    parking_lot: ParkingLot,
    vehicle: Vehicle,
    start_time: datetime,
    end_time: datetime,
) -> Reservation:
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=COLOMBIA_TZ)
    else:
        start_time = start_time.astimezone(COLOMBIA_TZ)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=COLOMBIA_TZ)
    else:
        end_time = end_time.astimezone(COLOMBIA_TZ)

    now = datetime.now(timezone.utc)
    if start_time.astimezone(timezone.utc) < now:
        raise ReservationInThePastError("La fecha/hora de la reserva debe ser futura")
    if end_time <= start_time:
        raise ReservationInThePastError("La hora de fin debe ser posterior a la hora de inicio")

    start_utc = start_time.astimezone(timezone.utc)
    end_utc = end_time.astimezone(timezone.utc)
    if not parking_lot.is_active:
        raise NoAvailableSpotForReservationError("El parqueadero no está activo")
    if vehicle.vehicle_category_id is None:
        raise NoAvailableSpotForReservationError(
            "El tipo de vehículo no está habilitado para reservas"
        )
    category = db.get(VehicleCategory, vehicle.vehicle_category_id)
    if category is None or not category.is_active:
        raise NoAvailableSpotForReservationError(
            "El tipo de vehículo no está habilitado para reservas"
        )
    try:
        ensure_schedule_covers(db, parking_lot.id, start_utc, end_utc)
    except (ScheduleNotConfiguredError, OutsideOperatingHoursError) as exc:
        raise NoAvailableSpotForReservationError(str(exc)) from exc

    vehicle_overlap = db.execute(
        select(Reservation).where(
            Reservation.vehicle_id == vehicle.id,
            Reservation.status == ReservationStatus.CONFIRMED,
            Reservation.start_time < end_utc,
            Reservation.end_time > start_utc,
        )
    ).scalar_one_or_none()
    if vehicle_overlap is not None:
        raise NoAvailableSpotForReservationError(
            "El vehículo ya tiene una reserva activa que se cruza con ese horario"
        )

    active_session = db.execute(
        select(ParkingSession.id).where(
            ParkingSession.vehicle_id == vehicle.id,
            ParkingSession.status == SessionStatus.ACTIVE,
            ParkingSession.entry_time < end_utc,
            or_(ParkingSession.exit_time.is_(None), ParkingSession.exit_time > start_utc),
        )
    ).first()
    if active_session is not None:
        raise NoAvailableSpotForReservationError(
            "El vehículo tiene una sesión activa que se cruza con ese horario"
        )

    candidate_ids = db.execute(
        select(ParkingSpot.id)
        .where(
            ParkingSpot.parking_lot_id == parking_lot.id,
            ParkingSpot.vehicle_category_id == category.id,
            ParkingSpot.is_active.is_(True),
        )
        .order_by(ParkingSpot.code)
    ).scalars().all()
    for spot_id in candidate_ids:
        spot = db.execute(
            select(ParkingSpot)
            .where(ParkingSpot.id == spot_id, ParkingSpot.is_active.is_(True))
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()
        if spot is None:
            continue

        overlapping_reservation = db.execute(
            select(Reservation.id).where(
                Reservation.spot_id == spot.id,
                Reservation.status == ReservationStatus.CONFIRMED,
                Reservation.start_time < end_utc,
                Reservation.end_time > start_utc,
            )
        ).first()
        if overlapping_reservation is not None:
            continue
        overlapping_session = db.execute(
            select(ParkingSession.id).where(
                ParkingSession.spot_id == spot.id,
                ParkingSession.status == SessionStatus.ACTIVE,
                ParkingSession.entry_time < end_utc,
                or_(ParkingSession.exit_time.is_(None), ParkingSession.exit_time > start_utc),
            )
        ).first()
        if overlapping_session is not None:
            continue

        reservation = Reservation(
            vehicle_id=vehicle.id,
            spot_id=spot.id,
            parking_lot_id=parking_lot.id,
            vehicle_type=vehicle.vehicle_type,
            start_time=start_utc,
            end_time=end_utc,
            status=ReservationStatus.CONFIRMED,
        )
        db.add(reservation)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            original = exc.orig
            sqlstate = getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
            if sqlstate == "23P01":
                raise NoAvailableSpotForReservationError(
                    "El espacio o el vehículo ya tiene una reserva que se cruza con ese horario"
                ) from exc
            raise
        db.refresh(reservation)
        return reservation

    raise NoAvailableSpotForReservationError(
        "No hay espacios disponibles de este tipo para el rango de tiempo solicitado"
    )


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    now = datetime.now(timezone.utc)
    locked_reservation = db.execute(
        select(Reservation)
        .where(Reservation.id == reservation.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).scalar_one()
    start_time = locked_reservation.start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if locked_reservation.status != ReservationStatus.CONFIRMED:
        raise ReservationCannotBeCancelledError("La reserva ya no está activa")
    if now >= start_time:
        raise ReservationCannotBeCancelledError(
            "No puedes cancelar una reserva después de su hora de inicio"
        )
    locked_reservation.status = ReservationStatus.CANCELLED
    db.commit()
    db.refresh(locked_reservation)
    return locked_reservation
