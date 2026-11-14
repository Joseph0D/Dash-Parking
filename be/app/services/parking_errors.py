"""
Módulo: parking_errors.py
Qué: Traduce los errores que lanzan las funciones y restricciones de PostgreSQL (db/) a
     respuestas HTTP con un mensaje claro.
Para qué: Que "el espacio ya fue tomado" o "ese correo ya existe" lleguen al cliente como
          409/400 con texto útil, en vez de un 500 genérico.
Impacto: Si un código SQLSTATE nuevo no está aquí, se re-lanza y el cliente ve un 500.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError

_UNIQUE_MESSAGES = {
    "usuario_correo_key": "Ese correo ya está registrado",
    "usuario_documento_id_key": "Ese documento ya está registrado",
    "vehiculo_placa_key": "Esa placa ya está registrada",
    "pago_referencia_transaccion_key": "Referencia de pago repetida, intenta de nuevo",
}


def translate_db_error(exc: DBAPIError) -> HTTPException:
    """Convierte un error de la base en HTTPException. Re-lanza el original si no lo conoce."""
    orig = exc.orig
    sqlstate = getattr(orig, "sqlstate", None)
    diag = getattr(orig, "diag", None)
    message = getattr(diag, "message_primary", None) or str(orig)

    if sqlstate == "23P01":  # exclusion_violation: espacio ya reservado/ocupado en la franja
        return HTTPException(status.HTTP_409_CONFLICT, message)
    if sqlstate == "P0002":  # no_data_found: no existe/no es tuyo (404) o no hay cupo (409)
        conflict = "disponible" in message
        return HTTPException(
            status.HTTP_409_CONFLICT if conflict else status.HTTP_404_NOT_FOUND, message
        )
    if sqlstate == "23505":  # unique_violation
        constraint = getattr(diag, "constraint_name", None)
        return HTTPException(
            status.HTTP_409_CONFLICT, _UNIQUE_MESSAGES.get(constraint, "El registro ya existe")
        )
    if sqlstate == "23503":  # foreign_key_violation (ej. tipo de vehículo inexistente)
        return HTTPException(status.HTTP_400_BAD_REQUEST, "Dato relacionado inexistente")
    if sqlstate == "P0001":  # raise_exception: regla de negocio de las funciones SQL
        return HTTPException(status.HTTP_400_BAD_REQUEST, message)
    raise exc
