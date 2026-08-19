"""Schemas del dashboard administrativo filtrable (RF-017)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import VehicleType


class VehicleTypeBreakdown(BaseModel):
    vehicle_type: VehicleType
    total_amount: Decimal
    session_count: int


class DailyBreakdown(BaseModel):
    day: date
    total_amount: Decimal
    session_count: int


class DashboardResponse(BaseModel):
    total_revenue: Decimal
    total_sessions: int
    average_session_amount: Decimal
    by_vehicle_type: list[VehicleTypeBreakdown]
    by_day: list[DailyBreakdown]
