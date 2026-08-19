"""
Router: spots.py
Qué: Consulta pública de ocupación del parqueadero (RF-003).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import SpotStatus
from app.models.parking_spot import ParkingSpot
from app.schemas.parking_spot import OccupancySummary, ParkingSpotResponse

router = APIRouter(prefix="/api/v1/parking", tags=["parking"])


@router.get("/occupancy", response_model=OccupancySummary)
def get_occupancy(db: Session = Depends(get_db)) -> OccupancySummary:
    spots = db.execute(select(ParkingSpot)).scalars().all()
    occupied = sum(1 for s in spots if s.status == SpotStatus.OCCUPIED)
    reserved = sum(1 for s in spots if s.status == SpotStatus.RESERVED)
    return OccupancySummary(
        total_spots=len(spots),
        occupied_spots=occupied,
        reserved_spots=reserved,
        available_spots=len(spots) - occupied - reserved,
        spots=[ParkingSpotResponse.model_validate(s) for s in spots],
    )
