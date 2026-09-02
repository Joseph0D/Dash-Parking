"""
Módulo: qr_service.py
Qué: Genera y valida los tokens QR de un solo uso asociados a una sesión (RF-015).
Para qué: Permitir pagar/validar una sesión escaneando un código en lugar de digitar la placa.
Impacto: Si el token se pudiera reutilizar, un mismo QR permitiría cobrar dos veces (RN-026).
"""
from __future__ import annotations

import base64
import secrets
from io import BytesIO

import qrcode
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parking_session import ParkingSession
from app.models.qr_token import QRToken


class InvalidQRTokenError(Exception):
    """El token no existe, ya fue usado, o la sesión ya no está activa (RN-026)."""


def generate_qr_pass(db: Session, session: ParkingSession) -> tuple[str, str]:
    """Genera un token nuevo para la sesión y lo codifica como imagen QR en base64."""
    token_value = secrets.token_urlsafe(24)
    qr_token = QRToken(session_id=session.id, token=token_value, used=False)
    db.add(qr_token)
    db.commit()

    qr_image = qrcode.make(token_value)
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")

    return token_value, image_base64


def validate_qr_token(db: Session, token_value: str) -> ParkingSession:
    """Valida un token QR, lo marca como usado y retorna la sesión asociada."""
    qr_token = db.execute(select(QRToken).where(QRToken.token == token_value)).scalar_one_or_none()
    if qr_token is None or qr_token.used:
        raise InvalidQRTokenError("Token QR inválido o ya utilizado")

    session = db.get(ParkingSession, qr_token.session_id)
    if session is None or session.status.value != "active":
        raise InvalidQRTokenError("La sesión asociada a este QR ya no está activa")

    qr_token.used = True
    db.commit()
    return session
