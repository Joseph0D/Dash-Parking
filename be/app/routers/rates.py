"""
Router: rates.py
Qué: Administración de tarifas por tipo de vehículo (RF-007). Solo administrador (RN-012).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database import get_db
from app.models.rate import Rate
from app.models.user import User
from app.schemas.rate import RateResponse, RateUpsertRequest

router = APIRouter(prefix="/api/v1/rates", tags=["rates"])


@router.get("", response_model=list[RateResponse])
def list_rates(db: Session = Depends(get_db)) -> list[RateResponse]:
    """Público: el frontend necesita mostrar tarifas vigentes sin exigir sesión (landing)."""
    rates = db.execute(select(Rate)).scalars().all()
    return [RateResponse.model_validate(r) for r in rates]


@router.put("", response_model=RateResponse)
def upsert_rate(
    payload: RateUpsertRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> RateResponse:
    """Crea o actualiza la tarifa vigente de un tipo de vehículo (RN-013: una vigente por tipo)."""
    rate = db.execute(select(Rate).where(Rate.vehicle_type == payload.vehicle_type)).scalar_one_or_none()
    if rate is None:
        rate = Rate(vehicle_type=payload.vehicle_type, price_per_hour=payload.price_per_hour)
        db.add(rate)
    else:
        rate.price_per_hour = payload.price_per_hour

    db.commit()
    db.refresh(rate)
    return RateResponse.model_validate(rate)
