"""Pruebas de app/services/fee_service.py (RF-005)."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.services.fee_service import billed_hours, calculate_amount, elapsed_seconds


def test_elapsed_seconds_is_never_negative():
    entry = datetime.now(timezone.utc)
    future_entry = entry + timedelta(hours=1)
    assert elapsed_seconds(future_entry, reference_time=entry) == 0


def test_elapsed_seconds_normalizes_naive_entry_as_utc():
    entry = datetime(2026, 1, 1, 12)
    reference = datetime(2026, 1, 1, 13, tzinfo=timezone.utc)

    assert elapsed_seconds(entry, reference_time=reference) == 3600


def test_elapsed_seconds_normalizes_naive_reference_as_utc():
    colombia = timezone(timedelta(hours=-5))
    entry = datetime(2026, 1, 1, 12, tzinfo=colombia)
    reference = datetime(2026, 1, 1, 18)

    assert elapsed_seconds(entry, reference_time=reference) == 3600


def test_billed_hours_rounds_up_partial_hour():
    assert billed_hours(3601) == 2  # una hora y un segundo -> se cobran 2 horas


def test_billed_hours_minimum_one_hour():
    assert billed_hours(0) == 1
    assert billed_hours(60) == 1  # un minuto -> mínimo 1 hora (RN-010)


def test_calculate_amount_multiplies_hours_by_rate():
    entry = datetime.now(timezone.utc) - timedelta(hours=2)
    amount = calculate_amount(entry, Decimal("4000"))
    assert amount == Decimal("8000.00")
