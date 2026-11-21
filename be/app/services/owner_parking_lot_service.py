"""Reglas de propiedad y mantenimiento de los parqueaderos administrados por un dueño."""
from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.enums import (
    PaymentStatus,
    ReservationStatus,
    SessionStatus,
    SpotStatus,
    VehicleType,
)
from app.models.parking_lot import ParkingLot
from app.models.parking_lot_schedule import ParkingLotSchedule
from app.models.parking_rate import ParkingRate
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.vehicle_category import VehicleCategory
from app.schemas.owner_parking_lot import (
    InventoryItem,
    OwnerParkingLotDashboardResponse,
    OwnerParkingLotDetailResponse,
    ParkingReservationSummary,
    ParkingInventoryResponse,
    ParkingLotCreateRequest,
    ParkingLotUpdateRequest,
    ParkingScheduleResponse,
    ScheduleUpdateRequest,
    VehicleTypeCount,
)
from app.services.availability_service import (
    COLOMBIA_TZ,
    OutsideOperatingHoursError,
    ScheduleNotConfiguredError,
    ensure_schedule_covers,
)


class ParkingLotNotFoundError(LookupError):
    """El parqueadero no existe o no pertenece al dueño autenticado."""


class DuplicateParkingLotIdentificationError(ValueError):
    """La identificación fiscal ya está asociada a otro parqueadero."""


class InvalidInventoryCategoryError(ValueError):
    """El dueño seleccionó una categoría no disponible."""


class InventoryConflictError(ValueError):
    """No se pueden retirar espacios con reservas o sesiones existentes."""


class ScheduleChangeConflictError(ValueError):
    """El nuevo horario dejaría fuera reservas ya confirmadas."""


def _owned_lot(db: Session, owner_id: uuid.UUID, lot_id: uuid.UUID) -> ParkingLot:
    lot = db.get(ParkingLot, lot_id)
    if lot is None or lot.owner_id != owner_id:
        raise ParkingLotNotFoundError("Parqueadero no encontrado")
    return lot


def _validate_categories(
    db: Session, inventory: list[InventoryItem]
) -> dict[uuid.UUID, VehicleCategory]:
    ids = {item.vehicle_category_id for item in inventory}
    categories = db.execute(
        select(VehicleCategory).where(
            VehicleCategory.id.in_(ids),
            VehicleCategory.is_active.is_(True),
        )
    ).scalars().all()
    result = {category.id: category for category in categories}
    if len(result) != len(ids):
        raise InvalidInventoryCategoryError("Uno o más tipos de vehículo no están disponibles")
    return result


def _code_prefix(category: VehicleCategory) -> str:
    return {
        "car": "CAR",
        "motorcycle": "MOT",
        "bicycle": "BIC",
        "electric_motorcycle": "EMO",
        "scooter": "SCO",
        "truck": "TRU",
    }.get(category.code, category.code[:3].upper())


def _is_identification_conflict(exc: IntegrityError) -> bool:
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    return bool(
        (constraint and "identification" in constraint)
        or "parking_lots.identification" in str(exc.orig)
    )


def _next_spot_code(prefix: str, existing_codes: set[str]) -> str:
    sequence = 1
    while True:
        candidate = f"{prefix}-{sequence:03d}"
        if candidate not in existing_codes:
            existing_codes.add(candidate)
            return candidate
        sequence += 1


def _today_colombia() -> date:
    return datetime.now(COLOMBIA_TZ).date()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _upsert_rate(
    db: Session,
    lot_id: uuid.UUID,
    category_id: uuid.UUID,
    item: InventoryItem,
    effective_date: date,
) -> None:
    current = db.execute(
        select(ParkingRate)
        .where(
            ParkingRate.parking_lot_id == lot_id,
            ParkingRate.vehicle_category_id == category_id,
            ParkingRate.valid_from <= effective_date,
            or_(ParkingRate.valid_to.is_(None), ParkingRate.valid_to >= effective_date),
        )
        .order_by(ParkingRate.valid_from.desc())
        .limit(1)
    ).scalar_one_or_none()

    if current is not None and current.valid_from == effective_date:
        current.price_per_minute = item.price_per_minute
        current.price_per_day = item.price_per_day
        current.price_per_month = item.price_per_month
        return
    if current is not None:
        current.valid_to = effective_date - timedelta(days=1)

    db.add(
        ParkingRate(
            parking_lot_id=lot_id,
            vehicle_category_id=category_id,
            price_per_minute=item.price_per_minute,
            price_per_day=item.price_per_day,
            price_per_month=item.price_per_month,
            valid_from=effective_date,
        )
    )


def _add_inventory(
    db: Session,
    lot: ParkingLot,
    inventory: list[InventoryItem],
    categories: dict[uuid.UUID, VehicleCategory],
    *,
    initial_codes: set[str] | None = None,
) -> None:
    existing_codes = initial_codes if initial_codes is not None else set()
    today = _today_colombia()
    for item in inventory:
        category = categories[item.vehicle_category_id]
        zone = ParkingZone(
            parking_lot_id=lot.id,
            vehicle_category_id=category.id,
            name=category.name,
            capacity=item.space_count,
        )
        db.add(zone)
        db.flush()
        for _ in range(item.space_count):
            db.add(
                ParkingSpot(
                    code=_next_spot_code(_code_prefix(category), existing_codes),
                    zone=zone.name,
                    vehicle_type=VehicleType(category.code),
                    is_active=True,
                    status=SpotStatus.AVAILABLE,
                    parking_lot_id=lot.id,
                    parking_zone_id=zone.id,
                    vehicle_category_id=category.id,
                )
            )
        _upsert_rate(db, lot.id, category.id, item, today)


def create_parking_lot(
    db: Session, owner: User, payload: ParkingLotCreateRequest
) -> OwnerParkingLotDetailResponse:
    categories = _validate_categories(db, payload.inventory)
    total_capacity = sum(item.space_count for item in payload.inventory)
    lot = ParkingLot(
        owner_id=owner.id,
        name=payload.name,
        identification=payload.identification.strip(),
        address=payload.address,
        phone=payload.phone,
        total_capacity=total_capacity,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_active=True,
    )
    db.add(lot)
    try:
        db.flush()
        db.add_all(
            [
                ParkingLotSchedule(
                    parking_lot_id=lot.id,
                    day_of_week=entry.day_of_week,
                    opens_at=entry.opens_at,
                    closes_at=entry.closes_at,
                    is_closed=entry.is_closed,
                    is_24_hours=entry.is_24_hours,
                )
                for entry in payload.schedules
            ]
        )
        _add_inventory(db, lot, payload.inventory, categories)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_identification_conflict(exc):
            raise DuplicateParkingLotIdentificationError(
                "Esa identificación ya está registrada"
            ) from exc
        raise
    return get_parking_lot_detail(db, owner.id, lot.id)


def list_parking_lots(
    db: Session, owner_id: uuid.UUID
) -> list[OwnerParkingLotDetailResponse]:
    lots = db.execute(
        select(ParkingLot)
        .where(ParkingLot.owner_id == owner_id)
        .order_by(ParkingLot.name)
    ).scalars().all()
    return [get_parking_lot_detail(db, owner_id, lot.id) for lot in lots]


def get_parking_lot_detail(
    db: Session, owner_id: uuid.UUID, lot_id: uuid.UUID
) -> OwnerParkingLotDetailResponse:
    lot = _owned_lot(db, owner_id, lot_id)
    schedules = db.execute(
        select(ParkingLotSchedule)
        .where(ParkingLotSchedule.parking_lot_id == lot.id)
        .order_by(ParkingLotSchedule.day_of_week)
    ).scalars().all()
    zones = db.execute(
        select(ParkingZone)
        .options(selectinload(ParkingZone.vehicle_category))
        .where(ParkingZone.parking_lot_id == lot.id)
        .order_by(ParkingZone.name)
    ).scalars().all()

    inventory_by_category: dict[uuid.UUID, tuple[VehicleCategory, int]] = {}
    for zone in zones:
        category = zone.vehicle_category
        count = db.execute(
            select(func.count(ParkingSpot.id)).where(
                ParkingSpot.parking_zone_id == zone.id,
                ParkingSpot.is_active.is_(True),
            )
        ).scalar_one()
        previous_category, previous_count = inventory_by_category.get(
            category.id, (category, 0)
        )
        inventory_by_category[category.id] = (previous_category, previous_count + count)

    today = _today_colombia()
    inventory = []
    for category_id, (category, space_count) in inventory_by_category.items():
        rate = db.execute(
            select(ParkingRate)
            .where(
                ParkingRate.parking_lot_id == lot.id,
                ParkingRate.vehicle_category_id == category_id,
                ParkingRate.valid_from <= today,
                or_(ParkingRate.valid_to.is_(None), ParkingRate.valid_to >= today),
            )
            .order_by(ParkingRate.valid_from.desc())
            .limit(1)
        ).scalar_one_or_none()
        inventory.append(
            ParkingInventoryResponse(
                vehicle_category_id=category_id,
                code=category.code,
                name=category.name,
                space_count=space_count,
                price_per_minute=rate.price_per_minute if rate else None,
                price_per_day=rate.price_per_day if rate else None,
                price_per_month=rate.price_per_month if rate else None,
            )
        )

    return OwnerParkingLotDetailResponse(
        id=lot.id,
        name=lot.name,
        identification=lot.identification,
        address=lot.address,
        phone=lot.phone,
        total_capacity=lot.total_capacity,
        latitude=lot.latitude,
        longitude=lot.longitude,
        is_active=lot.is_active,
        schedule_configured=len(schedules) == 7
        and {entry.day_of_week for entry in schedules} == set(range(7)),
        schedules=[ParkingScheduleResponse.model_validate(row) for row in schedules],
        inventory=inventory,
    )


def update_parking_lot(
    db: Session,
    owner_id: uuid.UUID,
    lot_id: uuid.UUID,
    payload: ParkingLotUpdateRequest,
) -> OwnerParkingLotDetailResponse:
    lot = _owned_lot(db, owner_id, lot_id)
    lot.name = payload.name
    lot.identification = payload.identification.strip()
    lot.address = payload.address
    lot.phone = payload.phone
    lot.latitude = payload.latitude
    lot.longitude = payload.longitude
    lot.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_identification_conflict(exc):
            raise DuplicateParkingLotIdentificationError(
                "Esa identificación ya está registrada"
            ) from exc
        raise
    return get_parking_lot_detail(db, owner_id, lot_id)


def update_schedule(
    db: Session,
    owner_id: uuid.UUID,
    lot_id: uuid.UUID,
    payload: ScheduleUpdateRequest,
) -> OwnerParkingLotDetailResponse:
    lot = _owned_lot(db, owner_id, lot_id)
    current = {
        row.day_of_week: row
        for row in db.execute(
            select(ParkingLotSchedule).where(ParkingLotSchedule.parking_lot_id == lot.id)
        ).scalars()
    }
    for entry in payload.schedules:
        schedule = current.get(entry.day_of_week)
        if schedule is None:
            schedule = ParkingLotSchedule(
                parking_lot_id=lot.id,
                day_of_week=entry.day_of_week,
            )
            db.add(schedule)
        schedule.opens_at = entry.opens_at
        schedule.closes_at = entry.closes_at
        schedule.is_closed = entry.is_closed
        schedule.is_24_hours = entry.is_24_hours

    try:
        db.flush()
        now = datetime.now(timezone.utc)
        future_reservations = db.execute(
            select(Reservation).where(
                Reservation.parking_lot_id == lot.id,
                Reservation.status == ReservationStatus.CONFIRMED,
                Reservation.end_time > now,
            )
        ).scalars()
        for reservation in future_reservations:
            try:
                ensure_schedule_covers(
                    db,
                    lot.id,
                    _as_utc(reservation.start_time),
                    _as_utc(reservation.end_time),
                )
            except (ScheduleNotConfiguredError, OutsideOperatingHoursError) as exc:
                raise ScheduleChangeConflictError(
                    "No puedes reducir el horario porque dejaría una reserva confirmada fuera de atención"
                ) from exc
        db.commit()
    except ScheduleChangeConflictError:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise
    return get_parking_lot_detail(db, owner_id, lot_id)


def update_inventory(
    db: Session,
    owner_id: uuid.UUID,
    lot_id: uuid.UUID,
    inventory: list[InventoryItem],
) -> OwnerParkingLotDetailResponse:
    lot = _owned_lot(db, owner_id, lot_id)
    categories = _validate_categories(db, inventory)
    today = _today_colombia()
    now = datetime.now(timezone.utc)
    try:
        existing_codes = set(
            db.execute(
                select(ParkingSpot.code).where(ParkingSpot.parking_lot_id == lot.id)
            ).scalars()
        )
        for item in inventory:
            category = categories[item.vehicle_category_id]
            zone = db.execute(
                select(ParkingZone).where(
                    ParkingZone.parking_lot_id == lot.id,
                    ParkingZone.vehicle_category_id == category.id,
                )
            ).scalars().first()
            if zone is None:
                zone = ParkingZone(
                    parking_lot_id=lot.id,
                    vehicle_category_id=category.id,
                    name=category.name,
                    capacity=item.space_count,
                )
                db.add(zone)
                db.flush()
                for _ in range(item.space_count):
                    db.add(
                        ParkingSpot(
                            code=_next_spot_code(_code_prefix(category), existing_codes),
                            zone=zone.name,
                            vehicle_type=VehicleType(category.code),
                            is_active=True,
                            status=SpotStatus.AVAILABLE,
                            parking_lot_id=lot.id,
                            parking_zone_id=zone.id,
                            vehicle_category_id=category.id,
                        )
                    )
                _upsert_rate(db, lot.id, category.id, item, today)
                continue

            active_spots = db.execute(
                select(ParkingSpot)
                .where(
                    ParkingSpot.parking_zone_id == zone.id,
                    ParkingSpot.is_active.is_(True),
                )
                .order_by(ParkingSpot.code)
                .with_for_update()
            ).scalars().all()
            delta = item.space_count - len(active_spots)
            if delta < 0:
                inactive_reservations = set(
                    db.execute(
                        select(Reservation.spot_id).where(
                            Reservation.spot_id.in_([spot.id for spot in active_spots]),
                            Reservation.status == ReservationStatus.CONFIRMED,
                            Reservation.end_time > now,
                        )
                    ).scalars()
                )
                active_sessions = set(
                    db.execute(
                        select(ParkingSession.spot_id).where(
                            ParkingSession.spot_id.in_([spot.id for spot in active_spots]),
                            ParkingSession.status == SessionStatus.ACTIVE,
                        )
                    ).scalars()
                )
                removable = [
                    spot
                    for spot in reversed(active_spots)
                    if spot.id not in inactive_reservations
                    and spot.id not in active_sessions
                ]
                if len(removable) < -delta:
                    raise InventoryConflictError(
                        "No puedes retirar espacios que tengan reservas o vehículos dentro"
                    )
                for spot in removable[: -delta]:
                    spot.is_active = False
                    spot.status = SpotStatus.AVAILABLE
            elif delta > 0:
                inactive_spots = db.execute(
                    select(ParkingSpot)
                    .where(
                        ParkingSpot.parking_zone_id == zone.id,
                        ParkingSpot.is_active.is_(False),
                    )
                    .order_by(ParkingSpot.code)
                    .with_for_update()
                ).scalars().all()
                reactivated = inactive_spots[:delta]
                for spot in reactivated:
                    spot.is_active = True
                    spot.status = SpotStatus.AVAILABLE
                for _ in range(delta - len(reactivated)):
                    db.add(
                        ParkingSpot(
                            code=_next_spot_code(_code_prefix(category), existing_codes),
                            zone=zone.name,
                            vehicle_type=VehicleType(category.code),
                            is_active=True,
                            status=SpotStatus.AVAILABLE,
                            parking_lot_id=lot.id,
                            parking_zone_id=zone.id,
                            vehicle_category_id=category.id,
                        )
                    )
            zone.capacity = item.space_count
            _upsert_rate(db, lot.id, category.id, item, today)

        db.flush()
        lot.total_capacity = db.execute(
            select(func.coalesce(func.sum(ParkingZone.capacity), 0)).where(
                ParkingZone.parking_lot_id == lot.id
            )
        ).scalar_one()
        db.commit()
    except (InventoryConflictError, InvalidInventoryCategoryError):
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        if _is_identification_conflict(exc):
            raise DuplicateParkingLotIdentificationError(
                "Esa identificación ya está registrada"
            ) from exc
        raise
    return get_parking_lot_detail(db, owner_id, lot_id)


def get_dashboard(
    db: Session, owner_id: uuid.UUID, lot_id: uuid.UUID, report_date: date
) -> OwnerParkingLotDashboardResponse:
    lot = _owned_lot(db, owner_id, lot_id)
    local_start = datetime.combine(report_date, time.min, tzinfo=COLOMBIA_TZ)
    local_end = local_start + timedelta(days=1)
    start_utc = local_start.astimezone(timezone.utc)
    end_utc = local_end.astimezone(timezone.utc)

    reservation_rows = db.execute(
        select(Reservation.vehicle_type, func.count(Reservation.id))
        .where(
            Reservation.parking_lot_id == lot.id,
            Reservation.status.in_(
                [ReservationStatus.CONFIRMED, ReservationStatus.COMPLETED]
            ),
            Reservation.start_time < end_utc,
            Reservation.end_time > start_utc,
        )
        .group_by(Reservation.vehicle_type)
    ).all()
    daily_reservations = db.execute(
        select(Reservation, Vehicle, ParkingSpot)
        .join(Vehicle, Vehicle.id == Reservation.vehicle_id)
        .join(ParkingSpot, ParkingSpot.id == Reservation.spot_id)
        .where(
            Reservation.parking_lot_id == lot.id,
            Reservation.status.in_(
                [ReservationStatus.CONFIRMED, ReservationStatus.COMPLETED]
            ),
            Reservation.start_time < end_utc,
            Reservation.end_time > start_utc,
        )
        .order_by(Reservation.start_time)
    ).all()
    occupancy_rows = db.execute(
        select(ParkingSpot.vehicle_type, func.count(ParkingSession.id))
        .join(ParkingSpot, ParkingSpot.id == ParkingSession.spot_id)
        .where(
            ParkingSpot.parking_lot_id == lot.id,
            ParkingSession.status == SessionStatus.ACTIVE,
        )
        .group_by(ParkingSpot.vehicle_type)
    ).all()
    income_today = db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .join(ParkingSession, ParkingSession.id == Payment.session_id)
        .join(ParkingSpot, ParkingSpot.id == ParkingSession.spot_id)
        .where(
            ParkingSpot.parking_lot_id == lot.id,
            Payment.status == PaymentStatus.PAID,
            Payment.created_at >= start_utc,
            Payment.created_at < end_utc,
        )
    ).scalar_one()

    return OwnerParkingLotDashboardResponse(
        report_date=report_date,
        reservation_count=sum(count for _, count in reservation_rows),
        daily_reservations=[
            ParkingReservationSummary(
                id=reservation.id,
                plate=vehicle.plate,
                vehicle_type=reservation.vehicle_type,
                start_time=reservation.start_time,
                end_time=reservation.end_time,
                status=reservation.status,
                spot_code=spot.code,
            )
            for reservation, vehicle, spot in daily_reservations
        ],
        reservations_by_vehicle_type=[
            VehicleTypeCount(vehicle_type=vehicle_type, count=count)
            for vehicle_type, count in reservation_rows
        ],
        occupancy_by_vehicle_type=[
            VehicleTypeCount(vehicle_type=vehicle_type, count=count)
            for vehicle_type, count in occupancy_rows
        ],
        income_today=Decimal(income_today),
    )
