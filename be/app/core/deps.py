"""
Módulo: deps.py
Qué: Dependencias de FastAPI para obtener el usuario autenticado y exigir un rol específico.
Para qué: Sustento de RN-021 — cada endpoint sensible valida explícitamente el rol requerido,
          no solo la autenticación.
Impacto: Si estas dependencias fallan silenciosamente, un cliente podría acceder a endpoints
         de administrador (tarifas, reportes, eliminar registros).
"""
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resuelve el usuario autenticado a partir del JWT. 401 si falta o es inválido."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_error

    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_error

    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise credentials_error
    return user


def require_role(*allowed_roles: UserRole):
    """Fábrica de dependencia: exige que el usuario autenticado tenga uno de los roles dados."""

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user

    return _dependency


require_admin = require_role(UserRole.ADMIN)
require_staff = require_role(UserRole.ADMIN, UserRole.OPERATOR)
