"""Schemas para la gestión de parqueaderos por sus dueños."""
from __future__ import annotations

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ReservationStatus, VehicleType


class VehicleCategoryResponse(BaseModel):
    id: uuid.UUID
    code: VehicleType
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class ParkingScheduleEntry(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    opens_at: time | None = None
    closes_at: time | None = None
    is_closed: bool = False
    is_24_hours: bool = False
    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_hours(self) -> "ParkingScheduleEntry":
        if self.is_closed:
            if self.is_24_hours or self.opens_at is not None or self.closes_at is not None:
                raise ValueError("Un día cerrado no puede tener horario de apertura")
        elif self.is_24_hours:
            if self.opens_at is not None or self.closes_at is not None:
                raise ValueError("Un día 24 horas no puede tener horas de apertura o cierre")
        elif (
            self.opens_at is None
            or self.closes_at is None
            or self.opens_at == self.closes_at
        ):
            raise ValueError("Configura horas distintas o marca el día como 24 horas")
        return self


class ScheduleUpdateRequest(BaseModel):
    schedules: list[ParkingScheduleEntry] = Field(..., min_length=7, max_length=7)

    @model_validator(mode="after")
    def validate_days(self) -> "ScheduleUpdateRequest":
        if {entry.day_of_week for entry in self.schedules} != set(range(7)):
            raise ValueError("Configura exactamente un horario para cada día de la semana")
        return self


class InventoryItem(BaseModel):
    vehicle_category_id: uuid.UUID
    space_count: int = Field(..., ge=1, le=5000)
    price_per_minute: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    price_per_day: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    price_per_month: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)


class InventoryUpdateRequest(BaseModel):
    inventory: list[InventoryItem] = Field(..., min_length=1, max_length=6)

    @model_validator(mode="after")
    def validate_categories(self) -> "InventoryUpdateRequest":
        category_ids = [item.vehicle_category_id for item in self.inventory]
        if len(category_ids) != len(set(category_ids)):
            raise ValueError("No repitas tipos de vehículo")
        return self


class ParkingLotFields(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    identification: str = Field(..., min_length=1, max_length=40)
    address: str = Field(..., min_length=3, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ParkingLotCreateRequest(ParkingLotFields):
    schedules: list[ParkingScheduleEntry] = Field(..., min_length=7, max_length=7)
    inventory: list[InventoryItem] = Field(..., min_length=1, max_length=6)

    @model_validator(mode="after")
    def validate_configuration(self) -> "ParkingLotCreateRequest":
        if {entry.day_of_week for entry in self.schedules} != set(range(7)):
            raise ValueError("Configura exactamente un horario para cada día de la semana")
        category_ids = [item.vehicle_category_id for item in self.inventory]
        if len(category_ids) != len(set(category_ids)):
            raise ValueError("No repitas tipos de vehículo")
        return self


class ParkingLotUpdateRequest(ParkingLotFields):
    is_active: bool


class ParkingScheduleResponse(ParkingScheduleEntry):
    pass


class ParkingInventoryResponse(BaseModel):
    vehicle_category_id: uuid.UUID
    code: VehicleType
    name: str
    space_count: int
    price_per_minute: Decimal | None
    price_per_day: Decimal | None
    price_per_month: Decimal | None


class OwnerParkingLotResponse(ParkingLotFields):
    id: uuid.UUID
    total_capacity: int
    is_active: bool
    schedule_configured: bool

    model_config = {"from_attributes": True}


class OwnerParkingLotDetailResponse(OwnerParkingLotResponse):
    schedules: list[ParkingScheduleResponse]
    inventory: list[ParkingInventoryResponse]


class VehicleTypeCount(BaseModel):
    vehicle_type: VehicleType
    count: int


class ParkingReservationSummary(BaseModel):
    id: uuid.UUID
    plate: str | None
    vehicle_type: VehicleType
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    spot_code: str


class OwnerParkingLotDashboardResponse(BaseModel):
    report_date: date
    reservation_count: int
    daily_reservations: list[ParkingReservationSummary]
    reservations_by_vehicle_type: list[VehicleTypeCount]
    occupancy_by_vehicle_type: list[VehicleTypeCount]
    income_today: Decimal
