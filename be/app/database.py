"""
Módulo: database.py
Qué: Configura el engine y las sesiones de SQLAlchemy contra PostgreSQL.
Para qué: Punto único de conexión a la base de datos, usado por todos los routers vía `get_db`.
Impacto: Si la conexión falla aquí, ninguna funcionalidad que dependa de datos persistentes
         (todo excepto /health) puede operar.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todos los modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al terminar la request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
