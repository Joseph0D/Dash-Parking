"""
Módulo: enums.py
Qué: Enumeraciones de dominio compartidas entre modelos ORM y esquemas Pydantic.
Para qué: Evitar strings "mágicos" repetidos entre capas (RNF-004 integridad del dato).
"""
from __future__ import annotations

from enum import Enum


class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"


class UserRole(str, Enum):
    CLIENT = "client"
    OPERATOR = "operator"
    ADMIN = "admin"


class SpotStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class ReservationStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentMethod(str, Enum):
    CASH = "cash"
    VIRTUAL = "virtual"
    QR = "qr"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    REJECTED = "rejected"
