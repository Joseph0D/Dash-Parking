"""
Schemas de reservas con pago simulado y de ingreso/salida.

Los nombres de campo están en español porque siguen el contrato del informe
(`POST /api/v1/reservas/crear` → `id_reserva`, `estado_espacio`, `id_comprobante`).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.services.payment_simulator import PaymentMethod


class CrearReservaRequest(BaseModel):
    id_estacionamiento: int
    id_vehiculo: int
    id_espacio: int | None = None  # si se omite, el sistema asigna un espacio libre
    fecha_inicio: datetime
    fecha_fin: datetime
    metodo_pago: PaymentMethod


class ReservaDetalle(BaseModel):
    """Resumen completo de una reserva (lo que se muestra en el comprobante)."""

    id_reserva: int
    id_estacionamiento: int
    nombre_parqueadero: str
    id_espacio: int
    numero_espacio: str
    zona: str
    id_vehiculo: int
    placa: str
    tipo_vehiculo: str
    cliente: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estado_reserva: str  # activa | en curso | vencida | finalizada | cancelada
    estado_espacio: str  # Reservado | Ocupado | Disponible
    metodo_pago: str | None
    monto_total: Decimal | None
    estado_pago: str | None
    referencia_transaccion: str | None
    id_comprobante: str | None
    id_ticket: int | None
    fecha_ingreso: datetime | None
    fecha_salida: datetime | None


class ReservaCreadaData(BaseModel):
    id_reserva: int
    id_espacio: int
    estado_espacio: str
    id_comprobante: str | None
    resumen: ReservaDetalle


class ReservaCreadaResponse(BaseModel):
    status: str = "success"
    message: str
    data: ReservaCreadaData
    code: int = 201


class CancelacionResponse(BaseModel):
    id_reserva: int
    estado_reserva: str
    monto_reembolsado: Decimal
    message: str


class TicketActivo(BaseModel):
    id_ticket: int
    id_reserva: int | None
    placa: str
    tipo_vehiculo: str
    numero_espacio: str
    zona: str
    nombre_parqueadero: str
    fecha_ingreso: datetime
    estado_ticket: str


class SalidaResponse(BaseModel):
    id_ticket: int
    estado_ticket: str
    fecha_salida: datetime
    message: str
