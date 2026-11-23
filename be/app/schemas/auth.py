"""Schemas de autenticación, registro y recuperación de contraseña."""
from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    surname: str | None = Field(default=None, min_length=2, max_length=120)
    document_type: str | None = Field(default=None, max_length=30)
    document_number: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, pattern=r"^\d+$", max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    account_type: Literal["client", "owner"] = "client"

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes en UTF-8")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str | None
    document_type: str | None
    document_number: str | None
    phone: str | None
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetRequestResponse(BaseModel):
    message: str


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes en UTF-8")
        return value


class PasswordResetConfirmResponse(BaseModel):
    message: str
