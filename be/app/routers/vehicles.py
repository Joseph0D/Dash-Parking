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
from app.schemas.vehicle import (
    VehicleCreateRequest,
    VehicleQRPassResponse,
    VehicleResponse,
    VehicleUpdateRequest,
)
from app.services.qr_service import get_or_create_vehicle_qr
from app.models.enums import ReservationStatus, SessionStatus, VehicleType
from app.models.reservation import Reservation
from app.models.parking_session import ParkingSession
from app.models.vehicle_category import VehicleCategory

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


def _vehicle_category(db: Session, vehicle_type: VehicleType) -> VehicleCategory:
    category = db.execute(
        select(VehicleCategory).where(
            VehicleCategory.code == vehicle_type.value,
            VehicleCategory.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este tipo de vehículo no está habilitado en el catálogo",
        )
    return category


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def register_vehicle(
    payload: VehicleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VehicleResponse:
    plate = normalize_plate(payload.plate) if payload.plate else None
    if plate is not None:
        existing = db.execute(select(Vehicle).where(Vehicle.plate == plate)).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esa placa ya está registrada")

    category = _vehicle_category(db, payload.vehicle_type)
    vehicle = Vehicle(
        plate=plate,
        vehicle_type=payload.vehicle_type,
        vehicle_category=category,
        brand=payload.brand,
        model=payload.model,
        color=payload.color,
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


@router.get("/{vehicle_id}/qr", response_model=VehicleQRPassResponse)
def get_vehicle_qr(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VehicleQRPassResponse:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    token, image_base64 = get_or_create_vehicle_qr(db, vehicle)
    return VehicleQRPassResponse(
        token=token,
        qr_image_base64=image_base64,
        vehicle_id=vehicle.id,
        plate=vehicle.plate,
    )


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VehicleResponse:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")

    plate = normalize_plate(payload.plate) if payload.plate else None
    if plate is not None:
        existing = db.execute(
            select(Vehicle).where(Vehicle.plate == plate, Vehicle.id != vehicle.id)
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Esa placa ya está registrada")

    vehicle.plate = plate
    vehicle.vehicle_type = payload.vehicle_type
    vehicle.vehicle_category = _vehicle_category(db, payload.vehicle_type)
    vehicle.brand = payload.brand
    vehicle.model = payload.model
    vehicle.color = payload.color
    db.commit()
    db.refresh(vehicle)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_vehicle(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None or vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    active_reservation = db.execute(
        select(Reservation).where(
            Reservation.vehicle_id == vehicle.id,
            Reservation.status == ReservationStatus.CONFIRMED,
        )
    ).first()
    if active_reservation is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes eliminar un vehículo con una reserva activa",
        )
    active_session = db.execute(
        select(ParkingSession).where(
            ParkingSession.vehicle_id == vehicle.id,
            ParkingSession.status == SessionStatus.ACTIVE,
        )
    ).first()
    if active_session is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puedes eliminar un vehículo con un ticket activo",
        )
    db.delete(vehicle)
    db.commit()
