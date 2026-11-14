"""
Módulo: parking_auth.py
Qué: Autenticación de las cuentas de la base nueva (tabla `usuario`, con rol): emisión del JWT,
     dependencia que resuelve la cuenta y control de roles.
Para qué: Que reservar, pagar y administrar un parqueadero exijan sesión y respeten el rol
          (cliente, dueño, administrador) definido en el informe.
Impacto: El token lleva `typ: account` y un id entero, así que NO sirve en los módulos
         anteriores (que usan UUID) ni al revés. Si esto falla, un cliente podría ver o
         cancelar reservas ajenas o registrar ingresos en un parqueadero que no es suyo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import decode_access_token
from app.parking_database import get_parking_db

ROLE_CLIENT = "cliente"
ROLE_OWNER = "dueno"
ROLE_ADMIN = "administrador"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/accounts/login", auto_error=False)


@dataclass(frozen=True)
class Account:
    id: int
    first_name: str
    last_name: str
    email: str
    role: str


def create_account_token(account_id: int, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(account_id), "role": role, "typ": "account", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_account(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_parking_db),
) -> Account:
    """Resuelve la cuenta del JWT. El rol se lee de la base en cada petición (no del token)."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token) if token else None
    if payload is None or payload.get("typ") != "account":
        raise credentials_error
    try:
        account_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise credentials_error from None

    row = (
        db.execute(
            text(
                """
                SELECT u.id_usuario AS id, u.nombres AS first_name, u.apellidos AS last_name,
                       u.correo AS email, r.nombre_rol AS role
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                WHERE u.id_usuario = :id
                """
            ),
            {"id": account_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise credentials_error
    return Account(**row)


def require_roles(*roles: str):
    """Dependencia que exige que la cuenta tenga alguno de los roles (403 si no)."""

    def checker(account: Account = Depends(get_current_account)) -> Account:
        if account.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta acción")
        return account

    return checker
