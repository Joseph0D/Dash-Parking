"""
Módulo: availability_service.py
Qué: Lógica de consulta de disponibilidad de espacios por parqueadero y franja horaria.
Para qué: Que un cliente elija parqueadero, tipo de vehículo y horario, y vea qué espacios
          están libres SOLO en esa franja (un espacio reservado de 10:00 a 11:00 sigue libre
          a las 9:00 y a las 11:00).
Impacto: La regla de disponibilidad y de precio vive en PostgreSQL (db/migrations/002_*.sql).
         Este módulo solo valida la franja y traduce resultados; si la valida mal, el cliente
         vería horarios imposibles o pasados.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.availability import (
    AvailabilityResponse,
    ParkingLotResponse,
    SpaceResponse,
    SpacesResponse,
    SpaceStatus,
    VehicleTypeResponse,
    ZoneAvailability,
)

# Colombia no tiene horario de verano: UTC-5 fijo. Se evita zoneinfo para no depender de tzdata
# en imágenes Docker "slim". Las fechas de la base son hora Colombia sin zona.
COLOMBIA_TZ = timezone(timedelta(hours=-5))

# Mismo margen que fn_crear_reserva: tolera el desfase de reloj entre cliente y servidor.
PAST_TOLERANCE = timedelta(minutes=5)

_STATUS_FROM_DB = {
    "Disponible": SpaceStatus.AVAILABLE,
    "Reservado": SpaceStatus.RESERVED,
    "Ocupado": SpaceStatus.OCCUPIED,
    "Mantenimiento": SpaceStatus.MAINTENANCE,
}


class InvalidTimeWindowError(ValueError):
    """La franja pedida no es válida (fin <= inicio, o inicio en el pasado)."""


class NotFoundError(LookupError):
    """El parqueadero o el tipo de vehículo no existe (o no aplica en ese parqueadero)."""


def now_colombia() -> datetime:
    """Hora actual de Colombia, sin zona (el formato que usa la base)."""
    return datetime.now(COLOMBIA_TZ).replace(tzinfo=None)


def normalize_window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """
    Convierte la franja a hora Colombia sin zona y la valida.

    Si el cliente envía zona horaria (ej. ISO con "Z"), se convierte; si no la trae, se asume que
    ya es hora Colombia. Falla con InvalidTimeWindowError si fin <= inicio o el inicio ya pasó.
    """

    def to_local(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(COLOMBIA_TZ).replace(tzinfo=None)

    start, end = to_local(start), to_local(end)
    if end <= start:
        raise InvalidTimeWindowError("La hora de fin debe ser posterior a la de inicio")
    if start < now_colombia() - PAST_TOLERANCE:
        raise InvalidTimeWindowError("La hora de inicio no puede estar en el pasado")
    return start, end


def list_parking_lots(db: Session) -> list[ParkingLotResponse]:
    rows = db.execute(
        text(
            """
            SELECT id_estacionamiento AS id, nombre_parqueadero AS name,
                   identificacion AS identification, direccion AS address,
                   telefono AS phone, capacidad_total AS total_capacity
            FROM estacionamiento ORDER BY id_estacionamiento
            """
        )
    ).mappings()
    return [ParkingLotResponse(**row) for row in rows]


def _require_parking_lot(db: Session, parking_lot_id: int) -> None:
    exists = db.execute(
        text("SELECT 1 FROM estacionamiento WHERE id_estacionamiento = :id"),
        {"id": parking_lot_id},
    ).first()
    if exists is None:
        raise NotFoundError("El parqueadero no existe")


def list_vehicle_types(db: Session, parking_lot_id: int) -> list[VehicleTypeResponse]:
    """Tipos de vehículo que tienen zona en el parqueadero, con su precio por hora vigente."""
    _require_parking_lot(db, parking_lot_id)
    rows = db.execute(
        text(
            """
            SELECT tv.id_tipo_vehiculo AS id, tv.nombre_tipo AS name,
                   tv.descripcion AS description, r.valor_minuto * 60 AS price_per_hour
            FROM tipo_vehiculo tv
            LEFT JOIN LATERAL (
                SELECT ta.valor_minuto FROM tarifa ta
                WHERE ta.id_tipo_vehiculo = tv.id_tipo_vehiculo
                  AND ta.id_estacionamiento = :pid
                  AND ta.fecha_vigencia_inicio <= CURRENT_DATE
                  AND (ta.fecha_vigencia_fin IS NULL OR ta.fecha_vigencia_fin >= CURRENT_DATE)
                ORDER BY ta.fecha_vigencia_inicio DESC LIMIT 1
            ) r ON TRUE
            WHERE EXISTS (SELECT 1 FROM zona z
                          WHERE z.id_estacionamiento = :pid
                            AND z.id_tipo_vehiculo = tv.id_tipo_vehiculo)
            ORDER BY tv.id_tipo_vehiculo
            """
        ),
        {"pid": parking_lot_id},
    ).mappings()
    return [VehicleTypeResponse(**row) for row in rows]


def get_zone_availability(
    db: Session, parking_lot_id: int, start: datetime, end: datetime
) -> AvailabilityResponse:
    """Resumen por zona (libres/reservados/ocupados) del parqueadero en la franja."""
    _require_parking_lot(db, parking_lot_id)
    rows = db.execute(
        text(
            """
            SELECT id_zona AS zone_id, nombre_zona AS zone_name,
                   id_tipo_vehiculo AS vehicle_type_id, capacidad AS capacity,
                   libres AS available, reservados AS reserved, ocupados AS occupied
            FROM fn_disponibilidad_franja(:pid, CAST(:start AS timestamp), CAST(:end AS timestamp))
            """
        ),
        {"pid": parking_lot_id, "start": start, "end": end},
    ).mappings()
    return AvailabilityResponse(
        parking_lot_id=parking_lot_id,
        start=start,
        end=end,
        zones=[ZoneAvailability(**row) for row in rows],
    )


def get_spaces(
    db: Session, parking_lot_id: int, vehicle_type_id: int, start: datetime, end: datetime
) -> SpacesResponse:
    """Cuadrícula de espacios del tipo de vehículo, con su estado en la franja y el precio."""
    _require_parking_lot(db, parking_lot_id)
    if vehicle_type_id not in {t.id for t in list_vehicle_types(db, parking_lot_id)}:
        raise NotFoundError("Ese tipo de vehículo no tiene zona en este parqueadero")

    params = {"pid": parking_lot_id, "vt": vehicle_type_id, "start": start, "end": end}
    rows = db.execute(
        text(
            """
            SELECT id_espacio AS id, numero_de_espacio AS code, id_zona AS zone_id,
                   nombre_zona AS zone_name, id_tipo_espacio AS space_type_id, estado
            FROM fn_estado_espacios(:pid, :vt, CAST(:start AS timestamp), CAST(:end AS timestamp))
            """
        ),
        params,
    ).mappings()
    spaces = [
        SpaceResponse(
            **{k: v for k, v in row.items() if k != "estado"}, status=_STATUS_FROM_DB[row["estado"]]
        )
        for row in rows
    ]
    price = db.execute(
        text(
            """
            SELECT fn_precio_estimado(
                :pid, :vt, CAST(:start AS timestamp), CAST(:end AS timestamp))
            """
        ),
        params,
    ).scalar_one()
    return SpacesResponse(
        parking_lot_id=parking_lot_id,
        vehicle_type_id=vehicle_type_id,
        start=start,
        end=end,
        estimated_price=price,
        available_count=sum(1 for s in spaces if s.status == SpaceStatus.AVAILABLE),
        spaces=spaces,
    )
