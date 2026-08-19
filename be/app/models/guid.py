"""
Módulo: guid.py
Qué: Tipo de columna UUID portable entre PostgreSQL (producción) y SQLite (tests en CI).
Para qué: Los modelos usaban `sqlalchemy.dialects.postgresql.UUID`, que no existe en SQLite —
          esto haría fallar cualquier test que no tenga un PostgreSQL real disponible.
Impacto: Sin este tipo, el pipeline de CI (que usa SQLite en memoria, ver tests/conftest.py)
         no podría ejecutar ningún test que toque un modelo con id UUID.
"""
from __future__ import annotations

import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Usa el UUID nativo de PostgreSQL en producción; en cualquier otro motor (SQLite en
    tests) lo almacena como CHAR(36) y convierte automáticamente al leer/escribir."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
