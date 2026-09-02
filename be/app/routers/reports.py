"""
Router: reports.py
Qué: Dashboard administrativo filtrable (RF-009, RF-017). Solo administrador.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database import get_db
from app.models.enums import VehicleType
from app.models.user import User
from app.schemas.report import DashboardResponse
from app.services.report_service import build_dashboard

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    vehicle_type: VehicleType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """Ganancia total, conteo de sesiones y desglose por tipo de vehículo y por día (RF-017)."""
    return build_dashboard(db, vehicle_type=vehicle_type, start_date=start_date, end_date=end_date)
