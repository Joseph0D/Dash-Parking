"""
Router: auth.py
Qué: Endpoints de registro, inicio de sesión y recuperación de contraseña.
Para qué: Punto de entrada de autenticación para toda la plataforma.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services import password_reset_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    surname: str = Field(..., min_length=2, max_length=120)
    document_type: str = Field(..., max_length=30)
    document_number: str = Field(..., min_length=1, max_length=30)
    phone: str = Field(..., pattern=r"^\d+$", max_length=30)
    email: str


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Autoregistro limitado a cliente o dueño; los roles privilegiados no son asignables aquí."""
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya está registrado"
        )

    user = User(
        name=payload.name,
        surname=payload.surname,
        document_type=payload.document_type,
        document_number=payload.document_number,
        phone=payload.phone,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole(payload.account_type),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if (constraint and "email" in constraint) or "users.email" in str(exc.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ese correo ya está registrado",
            ) from exc
        raise
    db.refresh(user)

    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Inicio de sesión (RF-012). Mensaje de error genérico (RN-020)."""
    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
    )

    user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise generic_error

    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post(
    "/password-reset/request",
    response_model=PasswordResetRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def request_password_reset(
    payload: PasswordResetRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> PasswordResetRequestResponse:
    if not settings.email_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La recuperación de contraseña no está disponible temporalmente",
        )
    client_ip = request.client.host if request.client is not None else "unknown"
    password_reset_service.request_password_reset(
        db,
        str(payload.email),
        client_ip,
        background_tasks,
    )
    return PasswordResetRequestResponse(
        message=password_reset_service.GENERIC_REQUEST_MESSAGE
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetConfirmResponse,
)
def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
) -> PasswordResetConfirmResponse:
    try:
        password_reset_service.reset_password(
            db,
            payload.token,
            payload.new_password,
        )
    except password_reset_service.InvalidPasswordResetTokenError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return PasswordResetConfirmResponse(
        message=password_reset_service.RESET_SUCCESS_MESSAGE
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    existing = db.execute(
        select(User).where(User.email == payload.email, User.id != current_user.id)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya está registrado"
        )

    current_user.name = payload.name
    current_user.surname = payload.surname
    current_user.document_type = payload.document_type
    current_user.document_number = payload.document_number
    current_user.phone = payload.phone
    current_user.email = payload.email
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
