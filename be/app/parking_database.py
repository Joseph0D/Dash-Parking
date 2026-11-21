"""Conexión de mantenimiento a la base legada `dash_parking_v2`.

La disponibilidad y las reservas nuevas consultan `app.database` (dash_parking/UUID).
Esta conexión se conserva para scripts y operaciones sobre el respaldo; no es una fuente
activa de datos para los endpoints del producto.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

parking_engine = create_engine(settings.parking_database_url, pool_pre_ping=True)
ParkingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=parking_engine)


def get_parking_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: sesión de la base de disponibilidad, cerrada al terminar."""
    db = ParkingSessionLocal()
    try:
        yield db
    finally:
        db.close()
