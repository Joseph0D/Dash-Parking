"""
Módulo: payment_simulator.py
Qué: Simulador de cobro para Tarjeta (crédito/débito), PSE, Nequi y Daviplata.
Para qué: Confirmar una reserva sin conexión real a entidades financieras (alcance académico
          del informe, tarea T03). No se piden ni guardan datos de tarjetas ni de cuentas.
Impacto: Es el ÚNICO punto que habría que reemplazar para integrar una pasarela real. Si
         rechaza el cobro, la reserva se revierte (ver reserva_service.create_reservation).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class PaymentMethod(StrEnum):
    """Valores exactos que acepta `pago.metodo_pago` (el efectivo es solo presencial)."""

    CREDIT_CARD = "Tarjeta Credito"
    DEBIT_CARD = "Tarjeta Debito"
    PSE = "PSE"
    NEQUI = "Nequi"
    DAVIPLATA = "Daviplata"


# Tope del cobro simulado: permite probar el camino de "pago rechazado" sin dinero real.
MAX_SIMULATED_AMOUNT = Decimal("10000000")

_PREFIX = {
    PaymentMethod.CREDIT_CARD: "TCR",
    PaymentMethod.DEBIT_CARD: "TDB",
    PaymentMethod.PSE: "PSE",
    PaymentMethod.NEQUI: "NEQ",
    PaymentMethod.DAVIPLATA: "DVP",
}


@dataclass(frozen=True)
class PaymentResult:
    approved: bool
    reference: str
    message: str


def simulate_charge(method: PaymentMethod, amount: Decimal) -> PaymentResult:
    """Simula el cobro: aprueba si el monto es válido y no supera el tope simulado."""
    reference = f"SIM-{_PREFIX[method]}-{uuid.uuid4().hex[:10].upper()}"
    if amount <= 0:
        return PaymentResult(False, reference, "El monto a pagar no es válido")
    if amount > MAX_SIMULATED_AMOUNT:
        return PaymentResult(False, reference, "El pago supera el límite permitido (simulado)")
    return PaymentResult(True, reference, "Pago simulado aprobado")
