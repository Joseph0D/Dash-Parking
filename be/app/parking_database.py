"""
Módulo: parking_database.py
Qué: Engine y sesiones de SQLAlchemy contra la base de disponibilidad por franjas
     (`dash_parking_v2`, esquema en español definido en db/).
Para qué: Consultar parqueaderos, zonas y espacios por franja horaria llamando a las funciones
          de PostgreSQL (`fn_estado_espacios`, `fn_disponibilidad_franja`, `fn_precio_estimado`).
Impacto: Si esta base no está cargada o no responde, solo fallan los endpoints de
         disponibilidad (503); el resto de la API sigue usando `app.database`.
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
