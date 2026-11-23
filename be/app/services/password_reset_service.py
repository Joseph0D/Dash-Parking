"""Creación, envío y consumo seguro de tokens de restablecimiento de contraseña."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import hash_password
from app.models.password_reset import PasswordResetAttempt, PasswordResetToken
from app.models.user import User
from app.services.email_service import send_password_reset_email

TOKEN_TTL = timedelta(minutes=30)
RATE_WINDOW = timedelta(hours=1)
ATTEMPTS_PER_EMAIL = 3
ATTEMPTS_PER_IP = 10
ATTEMPT_RETENTION = timedelta(days=1)
GENERIC_REQUEST_MESSAGE = (
    "Si el correo está asociado a una cuenta, recibirás instrucciones para restablecer la contraseña."
)
RESET_SUCCESS_MESSAGE = "La contraseña se restableció correctamente. Ya puedes iniciar sesión."


class InvalidPasswordResetTokenError(ValueError):
    """El token no existe, venció o ya fue utilizado."""


def _privacy_hash(value: str) -> str:
    return hmac.new(
        settings.jwt_secret.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _lock_rate_keys(db: Session, email_hash: str, ip_hash: str) -> None:
    if db.get_bind().dialect.name != "postgresql":
        return
    lock_ids = sorted(
        int.from_bytes(bytes.fromhex(value[:16]), byteorder="big", signed=True)
        for value in (email_hash, ip_hash)
    )
    for lock_id in lock_ids:
        db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": lock_id})


def request_password_reset(
    db: Session,
    email: str,
    client_ip: str,
    background_tasks: BackgroundTasks,
) -> None:
    now = datetime.now(timezone.utc)
    normalized_email = email.strip().lower()
    email_hash = _privacy_hash(f"email:{normalized_email}")
    ip_hash = _privacy_hash(f"ip:{client_ip}")
    _lock_rate_keys(db, email_hash, ip_hash)
    db.execute(
        delete(PasswordResetAttempt).where(
            PasswordResetAttempt.created_at < now - ATTEMPT_RETENTION
        )
    )
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.expires_at < now - ATTEMPT_RETENTION
        )
    )

    cutoff = now - RATE_WINDOW
    email_count = db.execute(
        select(func.count(PasswordResetAttempt.id)).where(
            PasswordResetAttempt.email_hash == email_hash,
            PasswordResetAttempt.created_at >= cutoff,
        )
    ).scalar_one()
    ip_count = db.execute(
        select(func.count(PasswordResetAttempt.id)).where(
            PasswordResetAttempt.ip_hash == ip_hash,
            PasswordResetAttempt.created_at >= cutoff,
        )
    ).scalar_one()
    if email_count >= ATTEMPTS_PER_EMAIL or ip_count >= ATTEMPTS_PER_IP:
        db.commit()
        return

    db.add(
        PasswordResetAttempt(
            email_hash=email_hash,
            ip_hash=ip_hash,
            created_at=now,
        )
    )
    user = db.execute(
        select(User).where(func.lower(User.email) == normalized_email)
    ).scalar_one_or_none()
    if user is None:
        db.commit()
        return

    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            created_at=now,
            expires_at=now + TOKEN_TTL,
        )
    )
    db.commit()
    background_tasks.add_task(send_password_reset_email, user.email, raw_token)


def reset_password(db: Session, token: str, new_password: str) -> None:
    now = datetime.now(timezone.utc)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    reset_token = db.execute(
        select(PasswordResetToken)
        .where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .with_for_update()
    ).scalar_one_or_none()
    if reset_token is None:
        raise InvalidPasswordResetTokenError("El enlace no es válido o ya venció")

    user = db.get(User, reset_token.user_id)
    if user is None:
        raise InvalidPasswordResetTokenError("El enlace no es válido o ya venció")

    user.password_hash = hash_password(new_password)
    reset_token.used_at = now
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.id != reset_token.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    db.commit()
