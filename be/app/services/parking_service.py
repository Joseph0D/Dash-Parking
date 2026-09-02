"""
Módulo: parking_service.py
Qué: Orquesta el registro de ingreso y salida de vehículos sobre la base de datos real.
Para qué: Sustento de RF-001, RF-002, RF-004. Centraliza las reglas de negocio del flujo
          operativo fuera de los routers HTTP, para que puedan probarse de forma aislada.
Impacto: Si falla, un vehículo podría ingresar sin espacio asignado, duplicar un ingreso ya
         registrado, o salir sin liberar su espacio — rompiendo la trazabilidad exigida por
         el informe de diseño.

Nota de migración: reemplaza la versión en memoria del Sprint 0. La interfaz pública
(register_entry / register_exit) se mantuvo conceptualmente igual a propósito.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ReservationStatus, SessionStatus, SpotStatus
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.rate import Rate
from app.models.reservation import Reservation
from app.models.vehicle import Vehicle, normalize_plate
from app.services.fee_service import calculate_amount


class VehicleAlreadyInsideError(Exception):
    """Se lanza cuando se intenta registrar el ingreso de una placa ya presente (RF-001, RN-002)."""


class NoAvailableSpotError(Exception):
    """Se lanza cuando no hay espacios libres para asignar (RF-002)."""


class SessionNotFoundError(Exception):
    """Se lanza cuando no hay una sesión activa para la placa/id consultado (RF-004)."""


class NoActiveRateError(Exception):
    """Se lanza cuando no existe tarifa vigente para el tipo de vehículo (RF-005, CA-005.4)."""


def register_entry(db: Session, vehicle: Vehicle) -> ParkingSession:
    """Registra el ingreso de un vehículo y le asigna un espacio disponible (RF-001, RF-002)."""
    active_session = db.execute(
        select(ParkingSession).where(
            ParkingSession.vehicle_id == vehicle.id,
            ParkingSession.status == SessionStatus.ACTIVE,
        )
    ).scalar_one_or_none()
    if active_session is not None:
        raise VehicleAlreadyInsideError(f"El vehículo {vehicle.plate} ya se encuentra dentro del parqueadero")

    now = datetime.now(timezone.utc)

    # RN-023: si hay una reserva vigente para esta placa que cubre "ahora", se vincula la sesión
    # a esa reserva y se usa el mismo espacio reservado.
    reservation = db.execute(
        select(Reservation).where(
            Reservation.vehicle_id == vehicle.id,
            Reservation.status == ReservationStatus.CONFIRMED,
            Reservation.start_time <= now,
            Reservation.end_time >= now,
        )
    ).scalar_one_or_none()

    if reservation is not None:
        spot = db.get(ParkingSpot, reservation.spot_id)
        reservation.status = ReservationStatus.COMPLETED
    else:
        spot = db.execute(
            select(ParkingSpot).where(
                ParkingSpot.vehicle_type == vehicle.vehicle_type,
                ParkingSpot.status == SpotStatus.AVAILABLE,
            )
        ).scalars().first()

    if spot is None:
        raise NoAvailableSpotError("No hay espacios disponibles en este momento para este tipo de vehículo")

    spot.status = SpotStatus.OCCUPIED

    session = ParkingSession(
        vehicle_id=vehicle.id,
        spot_id=spot.id,
        reservation_id=reservation.id if reservation else None,
        entry_time=now,
        status=SessionStatus.ACTIVE,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_active_session_for_plate(db: Session, plate: str) -> ParkingSession | None:
    normalized = normalize_plate(plate)
    return db.execute(
        select(ParkingSession)
        .join(Vehicle, Vehicle.id == ParkingSession.vehicle_id)
        .where(Vehicle.plate == normalized, ParkingSession.status == SessionStatus.ACTIVE)
    ).scalar_one_or_none()


def close_session(db: Session, session: ParkingSession) -> ParkingSession:
    """
    Registra la salida definitiva de una sesión: marca hora de salida, calcula el monto final
    y libera el espacio (RF-004, RF-005, RF-010 liberación).

    Se invoca únicamente después de que el pago quedó confirmado (RF-006/RF-014), para que una
    sesión nunca se cierre sin trazabilidad de cobro (RN-011).
    """
    now = datetime.now(timezone.utc)
    rate = db.execute(
        select(Rate).where(Rate.vehicle_type == session.vehicle.vehicle_type)
    ).scalar_one_or_none()
    if rate is None:
        raise NoActiveRateError("No hay una tarifa configurada para este tipo de vehículo")

    session.exit_time = now
    session.amount = calculate_amount(session.entry_time, rate.price_per_hour, now)
    session.status = SessionStatus.COMPLETED
    session.spot.status = SpotStatus.AVAILABLE

    db.commit()
    db.refresh(session)
    return session
