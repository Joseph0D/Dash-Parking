"""Schemas de cuentas (registro, login) y vehículos de la base nueva."""

from __future__ import annotations

from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    document_id: str = Field(min_length=5, max_length=20)
    phone: str = Field(min_length=7, max_length=15)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=100)
    password: str = Field(min_length=8, max_length=72)  # bcrypt solo usa 72 bytes


class LoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=1, max_length=72)


class AccountResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AccountResponse


class VehicleCreate(BaseModel):
    plate: str = Field(min_length=3, max_length=10, pattern=r"^[A-Za-z0-9-]+$")
    vehicle_type_id: int
    brand: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=30)


class VehicleResponse(BaseModel):
    id: int
    plate: str
    vehicle_type_id: int
    vehicle_type_name: str
    brand: str | None
    model: str | None
    color: str | None
