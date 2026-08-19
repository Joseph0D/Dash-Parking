"""
Router: vehicles.py
Qué: Registro y consulta de los vehículos del cliente autenticado (RF-001, RF-010).
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle, normalize_plate
from app.schemas.vehicle import VehicleCreateRequest, VehicleResponse

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def register_vehicle(
    payload: VehicleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VehicleResponse:
    plate = normalize_plate(payload.plate)
    existing = db.execute(select(Vehicle).where(Vehicle.plate == plate)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esa placa ya está registrada")

    vehicle = Vehicle(
        plate=plate,
        vehicle_type=payload.vehicle_type,
        model=payload.model,
        owner_id=current_user.id,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.get("/me", response_model=list[VehicleResponse])
def my_vehicles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[VehicleResponse]:
    vehicles = db.execute(select(Vehicle).where(Vehicle.owner_id == current_user.id)).scalars().all()
    return [VehicleResponse.model_validate(v) for v in vehicles]


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    db.delete(vehicle)
    db.commit()
