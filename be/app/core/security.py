"""
Módulo: security.py
Qué: Hashing de contraseñas (bcrypt) y emisión/verificación de tokens JWT.
Para qué: Sustento de RF-012 (autenticación por rol) y RNF-001 (seguridad).
Impacto: Es el único lugar donde se manejan contraseñas y tokens — un error aquí compromete
         la seguridad de toda la plataforma (RS-001, RN-019).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(plain_password: str) -> str:
    """Hashea una contraseña con bcrypt (RN-019: nunca se guarda en texto plano)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash almacenado."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """Genera un JWT con el id y el rol del usuario, para validar permisos sin otra consulta."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Decodifica y valida un JWT. Retorna None si es inválido o expiró (RNF-001.2)."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
