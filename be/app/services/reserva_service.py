"""
Módulo: reserva_service.py
Qué: Reservar un espacio por franja con pago simulado, cancelar con devolución simulada y las
     operaciones del dueño (ver reservas, registrar ingreso y salida).
Para qué: Ciclo del espacio del informe: Disponible → Reservado → Ocupado → Disponible.
Impacto: Reserva y pago se confirman en UNA transacción: si el cobro falla, la reserva no
         queda. Las reglas (cruce de horarios, tipo de vehículo, reembolso) viven en las
         funciones SQL de db/migrations; aquí solo se orquestan y se traducen sus errores.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.parking_auth import ROLE_ADMIN, Account
from app.schemas.reservas import (
    CancelacionResponse,
    CrearReservaRequest,
    ReservaCreadaData,
    ReservaCreadaResponse,
    ReservaDetalle,
    SalidaResponse,
    TicketActivo,
)
from app.services import availability_service
from app.services.parking_errors import translate_db_error
from app.services.payment_simulator import simulate_charge

_DETAIL_SELECT = """
    SELECT id_reserva, id_estacionamiento, nombre_parqueadero, id_espacio,
           numero_de_espacio AS numero_espacio, nombre_zona AS zona, id_vehiculo, placa,
           tipo_vehiculo, nombres || ' ' || apellidos AS cliente, fecha_inicio, fecha_fin,
           estado_visible AS estado_reserva, metodo_pago, monto_total, estado_pago,
           referencia_transaccion, id_comprobante, id_ticket,
           fecha_hora_entrada AS fecha_ingreso, fecha_hora_salida AS fecha_salida
    FROM vw_reservas_detalle
"""


def _space_state(estado_reserva: str) -> str:
    """Estado del espacio según el punto del ciclo en que está la reserva."""
    if estado_reserva == "en curso":
        return "Ocupado"
    if estado_reserva == "activa":
        return "Reservado"
    return "Disponible"


def _detail(row) -> ReservaDetalle:
    return ReservaDetalle(**row, estado_espacio=_space_state(row["estado_reserva"]))


def get_detail(db: Session, reserva_id: int) -> ReservaDetalle:
    row = (
        db.execute(text(_DETAIL_SELECT + " WHERE id_reserva = :id"), {"id": reserva_id})
        .mappings()
        .first()
    )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La reserva no existe")
    return _detail(row)


def create_reservation(
    db: Session, account: Account, data: CrearReservaRequest
) -> ReservaCreadaResponse:
    try:
        start, end = availability_service.normalize_window(data.fecha_inicio, data.fecha_fin)
    except availability_service.InvalidTimeWindowError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    params = {
        "uid": account.id,
        "vid": data.id_vehiculo,
        "pid": data.id_estacionamiento,
        "start": start,
        "end": end,
        "space": data.id_espacio,
    }
    try:
        # 1) Aparta el espacio (la base rechaza cruces, tipo de vehículo incorrecto, etc.)
        reserva_id = db.execute(
            text(
                """
                SELECT id_reserva FROM fn_crear_reserva(
                    :uid, :vid, :pid, CAST(:start AS timestamp), CAST(:end AS timestamp), :space)
                """
            ),
            params,
        ).scalar_one()

        # 2) Cobra (simulado) el precio de la franja
        amount = db.execute(
            text(
                """
                SELECT fn_precio_estimado(:pid, v.id_tipo_vehiculo,
                                          CAST(:start AS timestamp), CAST(:end AS timestamp))
                FROM vehiculo v WHERE v.id_vehiculo = :vid
                """
            ),
            params,
        ).scalar_one()
        if amount is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "No hay tarifa vigente para este tipo de vehículo"
            )
        charge = simulate_charge(data.metodo_pago, amount)
        if not charge.approved:
            db.rollback()  # la reserva no debe quedar si el pago no se aprobó
            raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, charge.message)

        # 3) Registra el pago: el trigger fija la tarifa y el monto, y emite el comprobante
        db.execute(
            text(
                """
                INSERT INTO pago (id_reserva, id_tarifa, monto_total, metodo_pago, estado_pago,
                                  referencia_transaccion)
                VALUES (:rid, NULL, 0, :method, 'Aprobado', :reference)
                """
            ),
            {"rid": reserva_id, "method": data.metodo_pago.value, "reference": charge.reference},
        )
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc

    resumen = get_detail(db, reserva_id)
    return ReservaCreadaResponse(
        message="Reserva creada y pago simulado aprobado",
        data=ReservaCreadaData(
            id_reserva=resumen.id_reserva,
            id_espacio=resumen.id_espacio,
            estado_espacio=resumen.estado_espacio,
            id_comprobante=resumen.id_comprobante,
            resumen=resumen,
        ),
    )


def list_my_reservations(db: Session, account: Account) -> list[ReservaDetalle]:
    rows = db.execute(
        text(_DETAIL_SELECT + " WHERE id_usuario = :uid ORDER BY fecha_inicio DESC LIMIT 50"),
        {"uid": account.id},
    ).mappings()
    return [_detail(row) for row in rows]


def cancel_reservation(db: Session, account: Account, reserva_id: int) -> CancelacionResponse:
    try:
        refund = db.execute(
            text("SELECT fn_cancelar_reserva(:rid, :uid)"), {"rid": reserva_id, "uid": account.id}
        ).scalar_one()
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc
    return CancelacionResponse(
        id_reserva=reserva_id,
        estado_reserva="cancelada",
        monto_reembolsado=refund,
        message="Reserva cancelada; reembolso simulado procesado",
    )


# ------------------------------------------------------------------ operaciones del dueño


def _can_manage(db: Session, account: Account, parking_lot_id: int) -> bool:
    """El administrador gestiona todo; el dueño, solo los parqueaderos donde es propietario."""
    if account.role == ROLE_ADMIN:
        return True
    return (
        db.execute(
            text(
                "SELECT 1 FROM estacionamiento "
                "WHERE id_estacionamiento = :pid AND id_propietario = :uid"
            ),
            {"pid": parking_lot_id, "uid": account.id},
        ).first()
        is not None
    )


def _require_manage(db: Session, account: Account, parking_lot_id: int | None) -> None:
    if parking_lot_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El registro no existe")
    if not _can_manage(db, account, parking_lot_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ese parqueadero no es tuyo")


def list_managed_reservations(
    db: Session, account: Account, only_current: bool = True
) -> list[ReservaDetalle]:
    """Reservas de los parqueaderos que gestiona la cuenta. Por defecto, solo las vigentes."""
    where = "estado_visible IN ('activa', 'en curso')" if only_current else "TRUE"
    rows = db.execute(
        text(
            f"""{_DETAIL_SELECT}
            WHERE {where}
              AND (:is_admin OR id_estacionamiento IN
                   (SELECT id_estacionamiento FROM estacionamiento WHERE id_propietario = :uid))
            ORDER BY fecha_inicio LIMIT 200"""
        ),
        {"is_admin": account.role == ROLE_ADMIN, "uid": account.id},
    ).mappings()
    return [_detail(row) for row in rows]


def register_entry(db: Session, account: Account, reserva_id: int) -> ReservaDetalle:
    lot_id = db.execute(
        text("SELECT id_estacionamiento FROM reserva WHERE id_reserva = :id"), {"id": reserva_id}
    ).scalar_one_or_none()
    _require_manage(db, account, lot_id)
    try:
        db.execute(text("SELECT fn_registrar_ingreso(:id)"), {"id": reserva_id})
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc
    return get_detail(db, reserva_id)


def list_active_tickets(db: Session, account: Account) -> list[TicketActivo]:
    rows = db.execute(
        text(
            """
            SELECT t.id_ticket, t.id_reserva, v.placa, tv.nombre_tipo AS tipo_vehiculo,
                   e.numero_de_espacio AS numero_espacio, z.nombre_zona AS zona,
                   est.nombre_parqueadero, t.fecha_hora_entrada AS fecha_ingreso, t.estado_ticket
            FROM ticket t
            JOIN vehiculo v ON v.id_vehiculo = t.id_vehiculo
            JOIN tipo_vehiculo tv ON tv.id_tipo_vehiculo = v.id_tipo_vehiculo
            JOIN espacios e ON e.id_espacio = t.id_espacio
            JOIN zona z ON z.id_zona = e.id_zona
            JOIN estacionamiento est ON est.id_estacionamiento = e.id_estacionamiento
            WHERE t.fecha_hora_salida IS NULL
              AND (:is_admin OR est.id_propietario = :uid)
            ORDER BY t.fecha_hora_entrada
            """
        ),
        {"is_admin": account.role == ROLE_ADMIN, "uid": account.id},
    ).mappings()
    return [TicketActivo(**row) for row in rows]


def register_exit(db: Session, account: Account, ticket_id: int) -> SalidaResponse:
    lot_id = db.execute(
        text(
            "SELECT e.id_estacionamiento FROM ticket t "
            "JOIN espacios e ON e.id_espacio = t.id_espacio WHERE t.id_ticket = :id"
        ),
        {"id": ticket_id},
    ).scalar_one_or_none()
    _require_manage(db, account, lot_id)
    try:
        row = (
            db.execute(
                text(
                    "SELECT id_ticket, estado_ticket, fecha_hora_salida AS fecha_salida "
                    "FROM fn_registrar_salida(:id)"
                ),
                {"id": ticket_id},
            )
            .mappings()
            .one()
        )
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc
    return SalidaResponse(**row, message="Salida registrada: el espacio quedó disponible")
