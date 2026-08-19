"""
Módulo: fee_service.py
Qué: Cálculo del tiempo de permanencia y el valor a pagar de una sesión.
Para qué: Sustento de RF-005. Centraliza la fórmula de cobro en un único lugar (RN-009, RN-010).
Impacto: Es el cálculo con mayor impacto económico directo del sistema — un error aquí
         afecta a todos los cobros.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal


def elapsed_seconds(entry_time: datetime, reference_time: datetime | None = None) -> int:
    """Segundos transcurridos desde el ingreso hasta `reference_time` (o ahora)."""
    now = reference_time or datetime.now(timezone.utc)
    return max(0, int((now - entry_time).total_seconds()))


def billed_hours(seconds: int) -> int:
    """
    Convierte segundos transcurridos en horas a cobrar.

    RN-010: se cobra por hora completa, con un mínimo de 1 hora — esta es la definición que
    quedó pendiente de aclarar en restricciones.md; se documenta aquí para que sea trivial
    ajustarla (ej. a fracción de 15 minutos) sin tocar el resto del flujo.
    """
    if seconds <= 0:
        return 0
    return max(1, math.ceil(seconds / 3600))


def calculate_amount(entry_time: datetime, price_per_hour: Decimal, reference_time: datetime | None = None) -> Decimal:
    """Calcula el valor a pagar: horas cobradas × tarifa vigente (RF-005, RF-007)."""
    seconds = elapsed_seconds(entry_time, reference_time)
    hours = billed_hours(seconds)
    amount = Decimal(hours) * price_per_hour
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
