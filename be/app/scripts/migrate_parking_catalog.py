"""Copia el catálogo de dash_parking_v2 a los modelos UUID sin modificar el origen."""
from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter
from typing import Any

from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app.database import engine
from app.models.enums import SpotStatus, VehicleType
from app.models.parking_lot import ParkingLot
from app.models.parking_rate import ParkingRate
from app.models.parking_space_type import ParkingSpaceType
from app.models.parking_spot import ParkingSpot
from app.models.parking_zone import ParkingZone
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.vehicle_category import VehicleCategory
from app.parking_database import parking_engine

_VEHICLE_TYPES: dict[str, tuple[str, VehicleType]] = {
    "carro": ("car", VehicleType.CAR),
    "car": ("car", VehicleType.CAR),
    "moto": ("motorcycle", VehicleType.MOTORCYCLE),
    "motocicleta": ("motorcycle", VehicleType.MOTORCYCLE),
    "bicicleta": ("bicycle", VehicleType.BICYCLE),
    "moto electrica": ("electric_motorcycle", VehicleType.ELECTRIC_MOTORCYCLE),
    "motocicleta electrica": ("electric_motorcycle", VehicleType.ELECTRIC_MOTORCYCLE),
    "patineta": ("scooter", VehicleType.SCOOTER),
    "scooter": ("scooter", VehicleType.SCOOTER),
    "camion": ("truck", VehicleType.TRUCK),
    "truck": ("truck", VehicleType.TRUCK),
}

def _normalized_name(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char)).strip()


def _slug(name: str) -> str:
    normalized = _normalized_name(name)
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def _vehicle_type(name: str) -> tuple[str, VehicleType]:
    normalized = _normalized_name(name)
    try:
        return _VEHICLE_TYPES[normalized]
    except KeyError as exc:
        raise ValueError(f"Tipo de vehículo heredado no reconocido: {name!r}") from exc


def _require_schema(source: Engine, target: Engine) -> None:
    source_inspector = inspect(source)
    required_source = {
        "estacionamiento": {
            "id_estacionamiento",
            "nombre_parqueadero",
            "identificacion",
            "direccion",
            "telefono",
            "capacidad_total",
            "latitud",
            "longitud",
        },
        "tipo_vehiculo": {"id_tipo_vehiculo", "nombre_tipo", "descripcion"},
        "tipo_espacio": {"id_tipo_espacio", "nombre_tipo", "descripcion"},
        "zona": {"id_zona", "id_estacionamiento", "id_tipo_vehiculo", "nombre_zona", "capacidad"},
        "espacios": {
            "id_espacio",
            "id_zona",
            "id_estacionamiento",
            "id_tipo_espacio",
            "numero_de_espacio",
            "estado",
        },
        "tarifa": {"id_tarifa", "id_tipo_vehiculo", "id_estacionamiento", "valor_minuto",
                   "valor_dia", "valor_mensualidad", "fecha_vigencia_inicio", "fecha_vigencia_fin"},
    }
    for table, expected_columns in required_source.items():
        if not source_inspector.has_table(table):
            raise RuntimeError(f"Falta la tabla heredada {table!r} en dash_parking_v2")
        actual_columns = {column["name"] for column in source_inspector.get_columns(table)}
        missing = expected_columns - actual_columns
        if missing:
            raise RuntimeError(
                f"Faltan columnas en {table!r}: {', '.join(sorted(missing))}; "
                "aplica primero las migraciones de db/migrations."
            )

    target_inspector = inspect(target)
    required_target = {
        "parking_lots": {"legacy_id", "owner_id"},
        "vehicle_categories": {"legacy_id", "code"},
        "parking_space_types": {"legacy_id", "code"},
        "parking_zones": {"legacy_id", "parking_lot_id", "vehicle_category_id"},
        "parking_spots": {
            "legacy_id", "parking_lot_id", "parking_zone_id", "vehicle_category_id", "space_type_id"
        },
        "parking_rates": {"legacy_id", "parking_lot_id", "vehicle_category_id"},
    }
    for table, expected_columns in required_target.items():
        if not target_inspector.has_table(table):
            raise RuntimeError(
                f"Falta la tabla UUID {table!r}; ejecuta 004_uuid_parking_schema.sql primero."
            )
        actual_columns = {column["name"] for column in target_inspector.get_columns(table)}
        missing = expected_columns - actual_columns
        if missing:
            raise RuntimeError(
                f"Faltan columnas en {table!r}: {', '.join(sorted(missing))}; "
                "ejecuta 004_uuid_parking_schema.sql primero."
            )


def _fetch(connection: Connection, query: str) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(text(query)).mappings()]


def _read_catalog(connection: Connection) -> dict[str, list[dict[str, Any]]]:
    catalog = {
        "lots": _fetch(
            connection,
            "SELECT id_estacionamiento AS legacy_id, nombre_parqueadero AS name, "
            "identificacion AS identification, direccion AS address, telefono AS phone, "
            "capacidad_total AS total_capacity, latitud AS latitude, longitud AS longitude "
            "FROM estacionamiento ORDER BY id_estacionamiento",
        ),
        "vehicle_categories": _fetch(
            connection,
            "SELECT id_tipo_vehiculo AS legacy_id, nombre_tipo AS name, descripcion AS description "
            "FROM tipo_vehiculo ORDER BY id_tipo_vehiculo",
        ),
        "space_types": _fetch(
            connection,
            "SELECT id_tipo_espacio AS legacy_id, nombre_tipo AS name, descripcion AS description "
            "FROM tipo_espacio ORDER BY id_tipo_espacio",
        ),
        "zones": _fetch(
            connection,
            "SELECT id_zona AS legacy_id, id_estacionamiento AS lot_id, "
            "id_tipo_vehiculo AS vehicle_category_id, nombre_zona AS name, capacidad AS capacity "
            "FROM zona ORDER BY id_zona",
        ),
        "spots": _fetch(
            connection,
            "SELECT id_espacio AS legacy_id, id_zona AS zone_id, "
            "id_estacionamiento AS lot_id, id_tipo_espacio AS space_type_id, "
            "numero_de_espacio AS code, estado FROM espacios ORDER BY id_espacio",
        ),
        "rates": _fetch(
            connection,
            "SELECT id_tarifa AS legacy_id, id_tipo_vehiculo AS vehicle_category_id, "
            "id_estacionamiento AS lot_id, valor_minuto AS price_per_minute, "
            "valor_dia AS price_per_day, valor_mensualidad AS price_per_month, "
            "fecha_vigencia_inicio AS valid_from, fecha_vigencia_fin AS valid_to "
            "FROM tarifa ORDER BY id_tarifa",
        ),
    }

    category_codes: dict[int, tuple[str, VehicleType]] = {}
    for row in catalog["vehicle_categories"]:
        code, vehicle_type = _vehicle_type(row["name"])
        if code in {entry[0] for entry in category_codes.values()}:
            raise ValueError(
                f"Hay tipos heredados duplicados que se asignan al mismo código: {code}"
            )
        category_codes[row["legacy_id"]] = (code, vehicle_type)

    lot_ids = {row["legacy_id"] for row in catalog["lots"]}
    category_ids = set(category_codes)
    space_type_ids = {row["legacy_id"] for row in catalog["space_types"]}
    zone_ids = {row["legacy_id"] for row in catalog["zones"]}
    for row in catalog["zones"]:
        if row["lot_id"] not in lot_ids or row["vehicle_category_id"] not in category_ids:
            raise ValueError(f"La zona heredada {row['legacy_id']} tiene relaciones incompletas")
    for row in catalog["spots"]:
        if (
            row["zone_id"] not in zone_ids
            or row["lot_id"] not in lot_ids
            or row["space_type_id"] not in space_type_ids
        ):
            raise ValueError(f"El espacio heredado {row['legacy_id']} tiene relaciones incompletas")
    for row in catalog["rates"]:
        if row["lot_id"] not in lot_ids or row["vehicle_category_id"] not in category_ids:
            raise ValueError(f"La tarifa heredada {row['legacy_id']} tiene relaciones incompletas")

    return catalog


def _by_legacy_id(db: Session, model: type[Any], legacy_id: int) -> Any | None:
    return db.execute(select(model).where(model.legacy_id == legacy_id)).scalar_one_or_none()


def _import_catalog(db: Session, catalog: dict[str, list[dict[str, Any]]]) -> Counter[str]:
    imported: Counter[str] = Counter()
    lots: dict[int, ParkingLot] = {}
    categories: dict[int, VehicleCategory] = {}
    space_types: dict[int, ParkingSpaceType] = {}
    zones: dict[int, ParkingZone] = {}
    vehicle_types_by_legacy = {
        row["legacy_id"]: _vehicle_type(row["name"])[1]
        for row in catalog["vehicle_categories"]
    }
    zone_categories_by_legacy = {
        row["legacy_id"]: row["vehicle_category_id"] for row in catalog["zones"]
    }

    for row in catalog["vehicle_categories"]:
        code, _ = _vehicle_type(row["name"])
        category = _by_legacy_id(db, VehicleCategory, row["legacy_id"])
        if category is None:
            category = db.execute(
                select(VehicleCategory).where(VehicleCategory.code == code)
            ).scalar_one_or_none()
            if category is not None and category.legacy_id not in (None, row["legacy_id"]):
                raise ValueError(f"Conflicto de código de categoría heredada: {code}")
            if category is None:
                category = VehicleCategory(
                    code=code,
                    name=row["name"],
                    description=row["description"],
                )
                db.add(category)
                imported["vehicle_categories"] += 1
            category.legacy_id = row["legacy_id"]
        categories[row["legacy_id"]] = category
    truck_category = db.execute(
        select(VehicleCategory).where(VehicleCategory.code == "truck")
    ).scalar_one_or_none()
    if truck_category is None:
        db.add(
            VehicleCategory(
                code="truck",
                name="Camión",
                description=(
                    "Vehículo de carga; cada parqueadero define si dispone de espacios "
                    "compatibles."
                ),
            )
        )
        imported["vehicle_categories"] += 1
    db.flush()

    for row in catalog["lots"]:
        lot = _by_legacy_id(db, ParkingLot, row["legacy_id"])
        if lot is None:
            if db.execute(
                select(ParkingLot).where(ParkingLot.identification == row["identification"])
            ).scalar_one_or_none() is not None:
                raise ValueError(
                    f"La identificación heredada {row['identification']!r} ya pertenece "
                    "a un parqueadero UUID distinto"
                )
            lot = ParkingLot(**row, owner_id=None, is_active=True)
            db.add(lot)
            imported["parking_lots"] += 1
        lots[row["legacy_id"]] = lot
    db.flush()

    for row in catalog["space_types"]:
        space_type = _by_legacy_id(db, ParkingSpaceType, row["legacy_id"])
        if space_type is None:
            code = _slug(row["name"])
            space_type = db.execute(
                select(ParkingSpaceType).where(ParkingSpaceType.code == code)
            ).scalar_one_or_none()
            if space_type is not None and space_type.legacy_id not in (None, row["legacy_id"]):
                raise ValueError(f"Conflicto de código de tipo de espacio heredado: {code}")
            if space_type is None:
                space_type = ParkingSpaceType(
                    legacy_id=row["legacy_id"],
                    code=code,
                    name=row["name"],
                    description=row["description"],
                )
                db.add(space_type)
                imported["parking_space_types"] += 1
            else:
                space_type.legacy_id = row["legacy_id"]
        space_types[row["legacy_id"]] = space_type
    db.flush()

    for row in catalog["zones"]:
        zone = _by_legacy_id(db, ParkingZone, row["legacy_id"])
        if zone is None:
            zone = ParkingZone(
                legacy_id=row["legacy_id"],
                parking_lot=lots[row["lot_id"]],
                vehicle_category=categories[row["vehicle_category_id"]],
                name=row["name"],
                capacity=row["capacity"],
            )
            db.add(zone)
            imported["parking_zones"] += 1
        zones[row["legacy_id"]] = zone
    db.flush()

    for row in catalog["spots"]:
        spot = _by_legacy_id(db, ParkingSpot, row["legacy_id"])
        if spot is None:
            if db.execute(
                select(ParkingSpot).where(
                    ParkingSpot.code == row["code"],
                    ParkingSpot.parking_lot_id == lots[row["lot_id"]].id,
                )
            ).scalar_one_or_none():
                raise ValueError(
                    f"El código de espacio heredado {row['code']!r} ya existe "
                    f"en el parqueadero legado {row['lot_id']}"
                )
            category_legacy_id = zone_categories_by_legacy[row["zone_id"]]
            spot = ParkingSpot(
                legacy_id=row["legacy_id"],
                code=row["code"],
                zone=zones[row["zone_id"]].name,
                vehicle_type=vehicle_types_by_legacy[category_legacy_id],
                is_active=row["estado"] == "activo",
                status=SpotStatus.AVAILABLE,
                parking_lot=lots[row["lot_id"]],
                parking_zone=zones[row["zone_id"]],
                vehicle_category=categories[category_legacy_id],
                space_type=space_types[row["space_type_id"]],
            )
            db.add(spot)
            imported["parking_spots"] += 1
    db.flush()

    for row in catalog["rates"]:
        rate = _by_legacy_id(db, ParkingRate, row["legacy_id"])
        if rate is None:
            rate = ParkingRate(
                legacy_id=row["legacy_id"],
                parking_lot=lots[row["lot_id"]],
                vehicle_category=categories[row["vehicle_category_id"]],
                price_per_minute=row["price_per_minute"],
                price_per_day=row["price_per_day"],
                price_per_month=row["price_per_month"],
                valid_from=row["valid_from"],
                valid_to=row["valid_to"],
            )
            db.add(rate)
            imported["parking_rates"] += 1
    db.flush()

    categories_by_code = {
        category.code: category
        for category in db.execute(select(VehicleCategory)).scalars()
    }
    unlinked_vehicles = db.execute(
        select(Vehicle).where(Vehicle.vehicle_category_id.is_(None))
    ).scalars()
    for vehicle in unlinked_vehicles:
        category = categories_by_code.get(vehicle.vehicle_type.value)
        if category is not None:
            vehicle.vehicle_category = category
    unlinked_spots = db.execute(
        select(ParkingSpot).where(ParkingSpot.vehicle_category_id.is_(None))
    ).scalars()
    for spot in unlinked_spots:
        category = categories_by_code.get(spot.vehicle_type.value)
        if category is not None:
            spot.vehicle_category = category

    db.flush()
    return imported


def migrate_catalog(source: Engine, target: Engine, apply: bool) -> Counter[str]:
    _require_schema(source, target)
    with source.connect() as connection:
        catalog = _read_catalog(connection)

    counts = Counter({name: len(rows) for name, rows in catalog.items()})
    print(
        "Registros heredados validados:",
        ", ".join(f"{key}={value}" for key, value in counts.items()),
    )

    with Session(target) as db:
        transaction = db.begin()
        imported = _import_catalog(db, catalog)
        if apply:
            transaction.commit()
        else:
            transaction.rollback()

    action = "importados" if apply else "se importarían"
    result = (
        ", ".join(f"{key}={value}" for key, value in sorted(imported.items())) or "ninguno"
    )
    print(f"Registros {action}: {result}")
    if not apply:
        print(
            "Simulación completada; usa --apply para guardar. "
            "dash_parking_v2 permanece intacta."
        )
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="confirma la importación; sin esta opción solo simula y revierte",
    )
    args = parser.parse_args()
    migrate_catalog(parking_engine, engine, apply=args.apply)


if __name__ == "__main__":
    main()
