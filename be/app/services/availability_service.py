"""Disponibilidad y horarios sobre el catálogo canónico de la base UUID."""
from __future__ import annotations

import math
import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.enums import ReservationStatus, SessionStatus
from app.models.parking_lot import ParkingLot
from app.models.parking_lot_schedule import ParkingLotSchedule
from app.models.parking_rate import ParkingRate
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.reservation import Reservation
from app.models.vehicle_category import VehicleCategory
from app.schemas.availability import (
    AvailabilityResponse,
    ParkingLotResponse,
    SpaceResponse,
    SpacesResponse,
    SpaceStatus,
    VehicleTypeResponse,
    ZoneAvailability,
)

COLOMBIA_TZ = timezone(timedelta(hours=-5))
PAST_TOLERANCE = timedelta(minutes=5)


class InvalidTimeWindowError(ValueError):
    """La franja pedida no es válida."""


class NotFoundError(LookupError):
    """El parqueadero o el tipo de vehículo no existe."""


class ScheduleNotConfiguredError(ValueError):
    """No se puede reservar hasta configurar los siete días del horario."""


class OutsideOperatingHoursError(ValueError):
    """La franja solicitada no está cubierta por el horario del parqueadero."""


def now_colombia() -> datetime:
    return datetime.now(COLOMBIA_TZ).replace(tzinfo=None)


def normalize_window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """Asume hora Colombia si no hay zona y devuelve instantes UTC conscientes."""

    def as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=COLOMBIA_TZ)
        return value.astimezone(timezone.utc)

    start_utc, end_utc = as_utc(start), as_utc(end)
    if end_utc <= start_utc:
        raise InvalidTimeWindowError("La hora de fin debe ser posterior a la de inicio")
    if start_utc < datetime.now(timezone.utc) - PAST_TOLERANCE:
        raise InvalidTimeWindowError("La hora de inicio no puede estar en el pasado")
    return start_utc, end_utc


def _require_parking_lot(db: Session, parking_lot_id: uuid.UUID) -> ParkingLot:
    lot = db.get(ParkingLot, parking_lot_id)
    if lot is None or not lot.is_active:
        raise NotFoundError("El parqueadero no existe o no está activo")
    return lot


def _schedule_rows(db: Session, parking_lot_id: uuid.UUID) -> list[ParkingLotSchedule]:
    return db.execute(
        select(ParkingLotSchedule).where(ParkingLotSchedule.parking_lot_id == parking_lot_id)
    ).scalars().all()


def schedule_is_configured(db: Session, parking_lot_id: uuid.UUID) -> bool:
    rows = _schedule_rows(db, parking_lot_id)
    return len(rows) == 7 and {row.day_of_week for row in rows} == set(range(7))


def ensure_schedule_covers(
    db: Session, parking_lot_id: uuid.UUID, start_utc: datetime, end_utc: datetime
) -> None:
    rows = _schedule_rows(db, parking_lot_id)
    if len(rows) != 7 or {row.day_of_week for row in rows} != set(range(7)):
        raise ScheduleNotConfiguredError(
            "Este parqueadero aún no tiene configurado su horario semanal"
        )

    schedules = {row.day_of_week: row for row in rows}
    start_local = start_utc.astimezone(COLOMBIA_TZ)
    end_local = end_utc.astimezone(COLOMBIA_TZ)
    first_day = start_local.date() - timedelta(days=1)
    last_day = end_local.date()
    intervals: list[tuple[datetime, datetime]] = []
    current_day = first_day

    while current_day <= last_day:
        schedule = schedules[current_day.weekday()]
        midnight = datetime.combine(current_day, time.min, tzinfo=COLOMBIA_TZ)
        if not schedule.is_closed:
            if schedule.is_24_hours:
                intervals.append((midnight, midnight + timedelta(days=1)))
            elif schedule.opens_at is not None and schedule.closes_at is not None:
                opens = datetime.combine(current_day, schedule.opens_at, tzinfo=COLOMBIA_TZ)
                close_day = current_day
                if schedule.closes_at <= schedule.opens_at:
                    close_day += timedelta(days=1)
                closes = datetime.combine(close_day, schedule.closes_at, tzinfo=COLOMBIA_TZ)
                intervals.append((opens, closes))
        current_day += timedelta(days=1)

    intervals.sort()
    cursor = start_local
    for opens, closes in intervals:
        if closes <= cursor:
            continue
        if opens > cursor:
            break
        cursor = max(cursor, closes)
        if cursor >= end_local:
            return
    raise OutsideOperatingHoursError(
        "La franja solicitada está fuera del horario de atención del parqueadero"
    )


def list_parking_lots(db: Session) -> list[ParkingLotResponse]:
    lots = db.execute(
        select(ParkingLot).where(ParkingLot.is_active.is_(True)).order_by(ParkingLot.name)
    ).scalars().all()
    return [
        ParkingLotResponse(
            id=lot.id,
            name=lot.name,
            identification=lot.identification,
            address=lot.address,
            phone=lot.phone,
            total_capacity=lot.total_capacity,
            latitude=lot.latitude,
            longitude=lot.longitude,
            schedule_configured=schedule_is_configured(db, lot.id),
        )
        for lot in lots
    ]


def _active_rate(
    db: Session, parking_lot_id: uuid.UUID, category_id: uuid.UUID, on_date: date
) -> ParkingRate | None:
    return db.execute(
        select(ParkingRate)
        .where(
            ParkingRate.parking_lot_id == parking_lot_id,
            ParkingRate.vehicle_category_id == category_id,
            ParkingRate.valid_from <= on_date,
            or_(ParkingRate.valid_to.is_(None), ParkingRate.valid_to >= on_date),
        )
        .order_by(ParkingRate.valid_from.desc())
        .limit(1)
    ).scalar_one_or_none()


def list_vehicle_types(
    db: Session, parking_lot_id: uuid.UUID
) -> list[VehicleTypeResponse]:
    _require_parking_lot(db, parking_lot_id)
    categories = db.execute(
        select(VehicleCategory)
        .join(ParkingZone, ParkingZone.vehicle_category_id == VehicleCategory.id)
        .where(ParkingZone.parking_lot_id == parking_lot_id, VehicleCategory.is_active.is_(True))
        .distinct()
        .order_by(VehicleCategory.name)
    ).scalars().all()
    today = now_colombia().date()
    result = []
    for category in categories:
        rate = _active_rate(db, parking_lot_id, category.id, today)
        result.append(
            VehicleTypeResponse(
                id=category.id,
                code=category.code,
                name=category.name,
                description=category.description,
                price_per_hour=rate.price_per_minute * 60 if rate else None,
            )
        )
    return result


def _spaces_with_status(
    db: Session,
    parking_lot_id: uuid.UUID,
    start: datetime,
    end: datetime,
    category_id: uuid.UUID | None = None,
) -> list[tuple[ParkingSpot, SpaceStatus]]:
    conditions = [ParkingSpot.parking_lot_id == parking_lot_id]
    if category_id is not None:
        conditions.append(ParkingSpot.vehicle_category_id == category_id)
    spots = db.execute(
        select(ParkingSpot)
        .where(*conditions)
        .order_by(ParkingSpot.code)
    ).scalars().all()
    if not spots:
        return []

    spot_ids = [spot.id for spot in spots]
    reserved_ids = set(
        db.execute(
            select(Reservation.spot_id).where(
                Reservation.spot_id.in_(spot_ids),
                Reservation.status == ReservationStatus.CONFIRMED,
                Reservation.start_time < end,
                Reservation.end_time > start,
            )
        ).scalars()
    )
    occupied_ids = set(
        db.execute(
            select(ParkingSession.spot_id).where(
                ParkingSession.spot_id.in_(spot_ids),
                ParkingSession.status == SessionStatus.ACTIVE,
                ParkingSession.entry_time < end,
                or_(ParkingSession.exit_time.is_(None), ParkingSession.exit_time > start),
            )
        ).scalars()
    )
    states = []
    for spot in spots:
        if not spot.is_active:
            state = SpaceStatus.MAINTENANCE
        elif spot.id in occupied_ids:
            state = SpaceStatus.OCCUPIED
        elif spot.id in reserved_ids:
            state = SpaceStatus.RESERVED
        else:
            state = SpaceStatus.AVAILABLE
        states.append((spot, state))
    return states


def get_zone_availability(
    db: Session, parking_lot_id: uuid.UUID, start: datetime, end: datetime
) -> AvailabilityResponse:
    _require_parking_lot(db, parking_lot_id)
    zones = db.execute(
        select(ParkingZone)
        .where(ParkingZone.parking_lot_id == parking_lot_id)
        .order_by(ParkingZone.name)
    ).scalars().all()
    if schedule_is_configured(db, parking_lot_id):
        ensure_schedule_covers(db, parking_lot_id, start, end)

    states_by_zone: dict[uuid.UUID | None, list[SpaceStatus]] = {}
    for spot, state in _spaces_with_status(db, parking_lot_id, start, end):
        states_by_zone.setdefault(spot.parking_zone_id, []).append(state)

    availability = []
    for zone in zones:
        states = states_by_zone.get(zone.id, [])
        availability.append(
            ZoneAvailability(
                zone_id=zone.id,
                zone_name=zone.name,
                vehicle_type_id=zone.vehicle_category_id,
                capacity=zone.capacity,
                available=sum(state == SpaceStatus.AVAILABLE for state in states),
                reserved=sum(state == SpaceStatus.RESERVED for state in states),
                occupied=sum(state == SpaceStatus.OCCUPIED for state in states),
            )
        )
    return AvailabilityResponse(
        parking_lot_id=parking_lot_id, start=start, end=end, zones=availability
    )


def get_spaces(
    db: Session,
    parking_lot_id: uuid.UUID,
    vehicle_type_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> SpacesResponse:
    _require_parking_lot(db, parking_lot_id)
    zone = db.execute(
        select(ParkingZone).where(
            ParkingZone.parking_lot_id == parking_lot_id,
            ParkingZone.vehicle_category_id == vehicle_type_id,
        )
    ).scalars().first()
    if zone is None:
        raise NotFoundError("Ese tipo de vehículo no tiene zona en este parqueadero")
    if schedule_is_configured(db, parking_lot_id):
        ensure_schedule_covers(db, parking_lot_id, start, end)

    states = _spaces_with_status(db, parking_lot_id, start, end, vehicle_type_id)
    spaces = [
        SpaceResponse(
            id=spot.id,
            code=spot.code,
            zone_id=spot.parking_zone_id or zone.id,
            zone_name=spot.zone,
            space_type_id=spot.space_type_id,
            status=state,
        )
        for spot, state in states
    ]

    rate = _active_rate(db, parking_lot_id, vehicle_type_id, start.astimezone(COLOMBIA_TZ).date())
    estimated_price: Decimal | None = None
    if rate is not None:
        minutes = math.ceil((end - start).total_seconds() / 60)
        if minutes >= 1440 and rate.price_per_day is not None:
            estimated_price = Decimal(math.ceil(minutes / 1440)) * rate.price_per_day
        else:
            estimated_price = Decimal(minutes) * rate.price_per_minute

    return SpacesResponse(
        parking_lot_id=parking_lot_id,
        vehicle_type_id=vehicle_type_id,
        start=start,
        end=end,
        estimated_price=estimated_price,
        available_count=sum(space.status == SpaceStatus.AVAILABLE for space in spaces),
        spaces=spaces,
    )
