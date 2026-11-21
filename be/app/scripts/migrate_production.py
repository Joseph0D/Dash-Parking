"""Apply the versioned PostgreSQL schema migrations before starting the API."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from app.config import settings
from app.database import engine

logger = logging.getLogger(__name__)

MIGRATION_FILES = (
    "000_uuid_initial_schema.sql",
    "004_uuid_parking_schema.sql",
    "005_uuid_reservation_constraints.sql",
    "006_password_reset.sql",
)
MIGRATION_LOCK_ID = 815_720_241


def _migration_directory() -> Path:
    configured_directory = os.getenv("MIGRATIONS_DIR")
    if configured_directory:
        return Path(configured_directory)
    return Path(__file__).resolve().parents[3] / "db" / "migrations"


def run() -> None:
    settings.validate_production_config()
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Las migraciones de despliegue requieren PostgreSQL")

    migration_directory = _migration_directory()
    migrations = {
        filename: migration_directory / filename for filename in MIGRATION_FILES
    }
    missing = [str(path) for path in migrations.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Faltan archivos de migración: {', '.join(missing)}")

    connection = engine.raw_connection()
    cursor = connection.cursor()
    lock_acquired = False
    try:
        cursor.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_LOCK_ID,))
        connection.commit()
        lock_acquired = True

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dash_parking_schema_migrations (
                version VARCHAR(120) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        connection.commit()
        cursor.execute("SELECT version FROM dash_parking_schema_migrations")
        applied = {row[0] for row in cursor.fetchall()}

        for filename, path in migrations.items():
            if filename in applied:
                continue
            _apply_migration(connection, cursor, filename, path)

    finally:
        if lock_acquired:
            try:
                connection.rollback()
                cursor.execute(
                    "SELECT pg_advisory_unlock(%s)",
                    (MIGRATION_LOCK_ID,),
                )
                connection.commit()
            finally:
                cursor.close()
                connection.close()
        else:
            cursor.close()
            connection.close()


def _apply_migration(connection, cursor, filename: str, path: Path) -> None:
    if filename == "000_uuid_initial_schema.sql":
        cursor.execute(
            """
            SELECT to_regclass('public.users'),
                   to_regclass('public.vehicles'),
                   to_regclass('public.reservations'),
                   to_regclass('public.parking_spots')
            """
        )
        existing_tables = cursor.fetchone()
        if all(table is None for table in existing_tables):
            logger.info("Applying initial schema migration %s", filename)
            cursor.execute(path.read_text(encoding="utf-8"))
            connection.commit()
        elif all(table is not None for table in existing_tables):
            logger.info(
                "Existing UUID schema found; recording %s without recreating it",
                filename,
            )
        else:
            raise RuntimeError(
                "La base tiene un esquema UUID parcial; revisa su estado antes de migrar"
            )
    else:
        logger.info("Applying schema migration %s", filename)
        cursor.execute(path.read_text(encoding="utf-8"))
        connection.commit()

    cursor.execute(
        """
        INSERT INTO dash_parking_schema_migrations (version)
        VALUES (%s)
        """,
        (filename,),
    )
    connection.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
