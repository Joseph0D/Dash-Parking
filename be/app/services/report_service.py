"""
Módulo: report_service.py
Qué: Calcula las métricas agregadas del dashboard administrativo (RF-009, RF-017).
Para qué: Centraliza la lógica de agregación/filtrado para no duplicarla en el router.
Impacto: Es la fuente de la cifra de "ganancia total" que ve el propietario — un filtro mal
         aplicado distorsiona directamente la métrica financiera reportada (RN-029, RN-030).
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from app.models.enums import PaymentStatus, VehicleType
from app.models.parking_session import ParkingSession
from app.models.payment import Payment
from app.models.vehicle import Vehicle
from app.schemas.report import DailyBreakdown, DashboardResponse, VehicleTypeBreakdown


def build_dashboard(
    db: Session,
    vehicle_type: VehicleType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DashboardResponse:
    query = (
        select(Payment, Vehicle.vehicle_type)
        .join(ParkingSession, ParkingSession.id == Payment.session_id)
        .join(Vehicle, Vehicle.id == ParkingSession.vehicle_id)
        .where(Payment.status == PaymentStatus.PAID)
    )

    if vehicle_type is not None:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
    if start_date is not None:
        query = query.where(Payment.created_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date is not None:
        query = query.where(Payment.created_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))

    rows = db.execute(query).all()

    total_revenue = sum((p.amount for p, _ in rows), Decimal("0"))
    total_sessions = len(rows)
    average = (total_revenue / total_sessions) if total_sessions else Decimal("0")

    by_type: dict[VehicleType, list[Decimal]] = {}
    for payment, v_type in rows:
        by_type.setdefault(v_type, []).append(payment.amount)

    by_vehicle_type = [
        VehicleTypeBreakdown(
            vehicle_type=v_type,
            total_amount=sum(amounts, Decimal("0")),
            session_count=len(amounts),
        )
        for v_type, amounts in by_type.items()
    ]

    daily_query = (
        select(cast(Payment.created_at, Date).label("day"), func.sum(Payment.amount), func.count(Payment.id))
        .join(ParkingSession, ParkingSession.id == Payment.session_id)
        .join(Vehicle, Vehicle.id == ParkingSession.vehicle_id)
        .where(Payment.status == PaymentStatus.PAID)
    )
    if vehicle_type is not None:
        daily_query = daily_query.where(Vehicle.vehicle_type == vehicle_type)
    if start_date is not None:
        daily_query = daily_query.where(Payment.created_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date is not None:
        daily_query = daily_query.where(Payment.created_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))
    daily_query = daily_query.group_by("day").order_by("day")

    by_day = [
        DailyBreakdown(day=day, total_amount=total or Decimal("0"), session_count=count)
        for day, total, count in db.execute(daily_query).all()
    ]

    return DashboardResponse(
        total_revenue=total_revenue,
        total_sessions=total_sessions,
        average_session_amount=average.quantize(Decimal("0.01")),
        by_vehicle_type=by_vehicle_type,
        by_day=by_day,
    )
