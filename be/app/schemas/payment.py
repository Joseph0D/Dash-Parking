"""Schemas de pagos: virtual y QR (RF-006, RF-014, RF-015)."""
from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import PaymentMethod, PaymentStatus


class VirtualPaymentRequest(BaseModel):
    session_id: uuid.UUID


class CashPaymentRequest(BaseModel):
    session_id: uuid.UUID


class PaymentResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    reference: str

    model_config = {"from_attributes": True}


class QRPassResponse(BaseModel):
    token: str
    qr_image_base64: str
    session_id: uuid.UUID


class QRValidateRequest(BaseModel):
    token: str


class QRValidateResponse(BaseModel):
    session_id: uuid.UUID
    plate: str
    vehicle_type: str
    elapsed_seconds: int
    amount: Decimal
