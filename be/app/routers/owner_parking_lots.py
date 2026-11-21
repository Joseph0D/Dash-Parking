"""Endpoints de gestión aislada de parqueaderos para el rol dueño."""
from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_owner
from app.database import get_db
from app.models.user import User
from app.models.vehicle_category import VehicleCategory
from app.schemas.owner_parking_lot import (
    InventoryUpdateRequest,
    OwnerParkingLotDashboardResponse,
    OwnerParkingLotDetailResponse,
    ParkingLotCreateRequest,
    ParkingLotUpdateRequest,
    ScheduleUpdateRequest,
    VehicleCategoryResponse,
)
from app.services import owner_parking_lot_service as service
from app.services.availability_service import COLOMBIA_TZ

router = APIRouter(prefix="/api/v1/owner", tags=["owner-parking-lots"])


@contextmanager
def _translate_errors() -> Generator[None, None, None]:
    try:
        yield
    except service.ParkingLotNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except service.DuplicateParkingLotIdentificationError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except service.InvalidInventoryCategoryError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except (
        service.InventoryConflictError,
        service.ScheduleChangeConflictError,
    ) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get(
    "/vehicle-categories",
    response_model=list[VehicleCategoryResponse],
    dependencies=[Depends(require_owner)],
)
def list_vehicle_categories(
    db: Session = Depends(get_db),
) -> list[VehicleCategoryResponse]:
    categories = db.execute(
        select(VehicleCategory)
        .where(VehicleCategory.is_active.is_(True))
        .order_by(VehicleCategory.name)
    ).scalars().all()
    return [VehicleCategoryResponse.model_validate(category) for category in categories]


@router.get("/parking-lots", response_model=list[OwnerParkingLotDetailResponse])
def list_owned_parking_lots(
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> list[OwnerParkingLotDetailResponse]:
    with _translate_errors():
        return service.list_parking_lots(db, owner.id)


@router.post(
    "/parking-lots",
    response_model=OwnerParkingLotDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_parking_lot(
    payload: ParkingLotCreateRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDetailResponse:
    with _translate_errors():
        return service.create_parking_lot(db, owner, payload)


@router.get("/parking-lots/{lot_id}", response_model=OwnerParkingLotDetailResponse)
def get_parking_lot(
    lot_id: uuid.UUID,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDetailResponse:
    with _translate_errors():
        return service.get_parking_lot_detail(db, owner.id, lot_id)


@router.put("/parking-lots/{lot_id}", response_model=OwnerParkingLotDetailResponse)
def update_parking_lot(
    lot_id: uuid.UUID,
    payload: ParkingLotUpdateRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDetailResponse:
    with _translate_errors():
        return service.update_parking_lot(db, owner.id, lot_id, payload)


@router.put(
    "/parking-lots/{lot_id}/schedule",
    response_model=OwnerParkingLotDetailResponse,
)
def update_schedule(
    lot_id: uuid.UUID,
    payload: ScheduleUpdateRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDetailResponse:
    with _translate_errors():
        return service.update_schedule(db, owner.id, lot_id, payload)


@router.put(
    "/parking-lots/{lot_id}/inventory",
    response_model=OwnerParkingLotDetailResponse,
)
def update_inventory(
    lot_id: uuid.UUID,
    payload: InventoryUpdateRequest,
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDetailResponse:
    with _translate_errors():
        return service.update_inventory(db, owner.id, lot_id, payload.inventory)


@router.get(
    "/parking-lots/{lot_id}/dashboard",
    response_model=OwnerParkingLotDashboardResponse,
)
def parking_lot_dashboard(
    lot_id: uuid.UUID,
    report_date: date | None = Query(None),
    owner: User = Depends(require_owner),
    db: Session = Depends(get_db),
) -> OwnerParkingLotDashboardResponse:
    selected_date = report_date or datetime.now(COLOMBIA_TZ).date()
    with _translate_errors():
        return service.get_dashboard(db, owner.id, lot_id, selected_date)
