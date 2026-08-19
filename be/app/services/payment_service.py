"""
Módulo: payment_service.py
Qué: Orquesta el cobro de una sesión activa, sin importar el método (efectivo, virtual, QR).
Para qué: Sustento de RF-006, RF-014, RF-015. Único punto donde se crea un Payment y se cierra
          la sesión, garantizando RN-011 (una salida no se completa sin pago) y RN-024 (un solo
          pago 'paid' por sesión).
Impacto: Si falla, se podría cerrar una sesión sin pago o cobrarla dos veces.

Nota (RT-004 / restricciones.md): no existen credenciales de una pasarela real en este entorno
académico. `_simulate_gateway_approval` reemplaza la llamada HTTP real a Wompi/PSE/Nequi —
mover a una integración real solo implica reemplazar esa función, sin tocar el resto del flujo.
"""
from __future__ import annotations

import secrets
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.enums import PaymentMethod, PaymentStatus, SessionStatus
from app.models.parking_session import ParkingSession
from app.models.payment import Payment
from app.models.rate import Rate
from app.services.fee_service import calculate_amount
from app.services.parking_service import NoActiveRateError, close_session


class SessionNotActiveError(Exception):
    """La sesión ya fue cerrada o no existe (RN-011)."""


class SessionAlreadyPaidError(Exception):
    """Ya existe un pago 'paid' para esta sesión (RN-024)."""


def _simulate_gateway_approval() -> bool:
    """Simula la respuesta de una pasarela de pago virtual. Siempre aprueba en este entregable
    académico — el punto de extensión queda documentado en RF-014 (RN-025)."""
    return True


def current_amount(db: Session, session: ParkingSession) -> Decimal:
    rate = db.query(Rate).filter(Rate.vehicle_type == session.vehicle.vehicle_type).one_or_none()
    if rate is None:
        raise NoActiveRateError("No hay una tarifa configurada para este tipo de vehículo")
    return calculate_amount(session.entry_time, rate.price_per_hour)


def _guard_session_payable(session: ParkingSession) -> None:
    if session.status != SessionStatus.ACTIVE:
        raise SessionNotActiveError("La sesión no está activa")
    if any(p.status == PaymentStatus.PAID for p in session.payments):
        raise SessionAlreadyPaidError("Esta sesión ya fue pagada")


def pay_with_cash(db: Session, session: ParkingSession) -> Payment:
    """Cobro manual desde el panel de administración (RF-006)."""
    _guard_session_payable(session)
    amount = current_amount(db, session)
    payment = Payment(
        session_id=session.id,
        amount=amount,
        method=PaymentMethod.CASH,
        status=PaymentStatus.PAID,
        reference=f"CASH-{secrets.token_hex(4).upper()}",
    )
    db.add(payment)
    db.commit()
    close_session(db, session)
    db.refresh(payment)
    return payment


def pay_virtual(db: Session, session: ParkingSession) -> Payment:
    """Cobro por método virtual simulado (RF-014)."""
    _guard_session_payable(session)
    amount = current_amount(db, session)
    reference = f"VIRT-{secrets.token_hex(4).upper()}"

    approved = _simulate_gateway_approval()
    payment = Payment(
        session_id=session.id,
        amount=amount,
        method=PaymentMethod.VIRTUAL,
        status=PaymentStatus.PAID if approved else PaymentStatus.REJECTED,
        reference=reference,
    )
    db.add(payment)
    db.commit()

    if approved:
        close_session(db, session)

    db.refresh(payment)
    return payment


def pay_via_qr_session(db: Session, session: ParkingSession) -> Payment:
    """Cobro luego de validar un token QR (RF-015) — reutiliza el mismo flujo que efectivo."""
    return pay_with_cash(db, session)
