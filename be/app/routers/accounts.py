"""
Router: accounts.py
Qué: Registro, login, perfil y vehículos de las cuentas de la base nueva.
Para qué: Que el cliente tenga sesión y vehículos propios para reservar un espacio.
Impacto: El token de estos endpoints es distinto al de /api/v1/auth (módulos anteriores).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.parking_auth import Account, get_current_account
from app.parking_database import get_parking_db
from app.schemas.accounts import (
    AccountResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VehicleCreate,
    VehicleResponse,
)
from app.services import account_service

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_parking_db)) -> TokenResponse:
    return account_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_parking_db)) -> TokenResponse:
    return account_service.login(db, data)


@router.get("/me", response_model=AccountResponse)
def me(account: Account = Depends(get_current_account)) -> AccountResponse:
    return AccountResponse(**account.__dict__)


@router.get("/me/vehicles", response_model=list[VehicleResponse])
def list_vehicles(
    account: Account = Depends(get_current_account), db: Session = Depends(get_parking_db)
) -> list[VehicleResponse]:
    return account_service.list_vehicles(db, account)


@router.post("/me/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    data: VehicleCreate,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_parking_db),
) -> VehicleResponse:
    return account_service.create_vehicle(db, account, data)
