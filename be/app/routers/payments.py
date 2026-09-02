"""
Router: payments.py
Qué: Cobro de una sesión activa por efectivo (staff), virtual (cliente) o QR (RF-006, RF-014, RF-015).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_staff
from app.database import get_db
from app.models.enums import PaymentStatus
from app.models.parking_session import ParkingSession
from app.models.user import User
from app.schemas.payment import (
    CashPaymentRequest,
    PaymentResponse,
    QRPassResponse,
    QRValidateRequest,
    QRValidateResponse,
    VirtualPaymentRequest,
)
from app.services.fee_service import elapsed_seconds
from app.services.payment_service import (
    SessionAlreadyPaidError,
    SessionNotActiveError,
    current_amount,
    pay_via_qr_session,
    pay_virtual,
    pay_with_cash,
)
from app.services.parking_service import NoActiveRateError
from app.services.qr_service import InvalidQRTokenError, generate_qr_pass, validate_qr_token

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


def _get_owned_session(db: Session, session_id: uuid.UUID, current_user: User) -> ParkingSession:
    session = db.get(ParkingSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    if current_user.role.value == "client" and session.vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes pagar esta sesión")
    return session


@router.post("/virtual", response_model=PaymentResponse)
def pay_virtual_endpoint(
    payload: VirtualPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Pago virtual simulado (RF-014)."""
    session = _get_owned_session(db, payload.session_id, current_user)
    try:
        payment = pay_virtual(db, session)
    except (SessionNotActiveError, SessionAlreadyPaidError, NoActiveRateError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    if payment.status == PaymentStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="El pago fue rechazado, intenta con otro método")

    return PaymentResponse.model_validate(payment)


@router.post("/cash", response_model=PaymentResponse)
def pay_cash_endpoint(
    payload: CashPaymentRequest,
    _staff: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Cobro manual en efectivo desde el panel de administración (RF-006)."""
    session = db.get(ParkingSession, payload.session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    try:
        payment = pay_with_cash(db, session)
    except (SessionNotActiveError, SessionAlreadyPaidError, NoActiveRateError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return PaymentResponse.model_validate(payment)


@router.get("/qr/{session_id}", response_model=QRPassResponse)
def get_qr_pass(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> QRPassResponse:
    """Genera el pase QR de una sesión activa (RF-015)."""
    session = _get_owned_session(db, session_id, current_user)
    token, image_base64 = generate_qr_pass(db, session)
    return QRPassResponse(token=token, qr_image_base64=image_base64, session_id=session.id)


@router.post("/qr/validate", response_model=QRValidateResponse)
def validate_qr(
    payload: QRValidateRequest,
    _staff: User = Depends(require_staff),
    db: Session = Depends(get_db),
) -> QRValidateResponse:
    """El operario valida el QR mostrado por el cliente para proceder al cobro (RF-015)."""
    try:
        session = validate_qr_token(db, payload.token)
    except InvalidQRTokenError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return QRValidateResponse(
        session_id=session.id,
        plate=session.vehicle.plate,
        vehicle_type=session.vehicle.vehicle_type.value,
        elapsed_seconds=elapsed_seconds(session.entry_time),
        amount=current_amount(db, session),
    )


@router.post("/qr/{session_id}/charge", response_model=PaymentResponse)
def charge_after_qr(session_id: uuid.UUID, _staff: User = Depends(require_staff), db: Session = Depends(get_db)) -> PaymentResponse:
    """Cobra la sesión después de validar el QR (equivalente a efectivo/QR presencial)."""
    session = db.get(ParkingSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    try:
        payment = pay_via_qr_session(db, session)
    except (SessionNotActiveError, SessionAlreadyPaidError, NoActiveRateError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return PaymentResponse.model_validate(payment)
