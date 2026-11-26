"""
Módulo: config.py
Qué: Configuración centralizada de la aplicación, leída desde variables de entorno.
Para qué: Evitar valores hardcodeados (RS-001 de docs/requisitos/restricciones.md).
Impacto: Si falta una variable crítica (ej. JWT_SECRET), el arranque debe fallar explícitamente
         en vez de usar un valor inseguro por defecto en producción.
"""

from __future__ import annotations

from typing import Literal
from urllib.parse import parse_qs, urlsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_env: str = "development"

    # Sprint 0 usaba datos en memoria; desde este entregable la app requiere PostgreSQL real.
    database_url: str = (
        "postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking"
    )

    # Base legada que se conserva como respaldo; no es la fuente de disponibilidad nueva.
    parking_database_url: str = (
        "postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking_v2"
    )

    jwt_secret: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8  # 8 horas

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    frontend_base_url: str = "http://localhost:5173"
    email_provider: Literal["smtp", "brevo"] = "smtp"
    email_timeout_seconds: int = Field(default=10, gt=0, le=60)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    brevo_api_key: SecretStr | None = None
    email_from_email: str | None = None
    email_from_name: str = "Dash Parking"

    @field_validator("database_url")
    @classmethod
    def normalize_postgres_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value

    @property
    def smtp_configured(self) -> bool:
        has_username = bool(self.smtp_username)
        has_password = self.smtp_password is not None
        return bool(
            self.smtp_host
            and self.smtp_from_email
            and has_username == has_password
            and not (self.smtp_use_tls and self.smtp_use_ssl)
        )

    @property
    def brevo_configured(self) -> bool:
        return bool(
            self.brevo_api_key
            and self.brevo_api_key.get_secret_value()
            and self.email_from_email
        )

    @property
    def email_configured(self) -> bool:
        if self.email_provider == "brevo":
            return self.brevo_configured
        return self.smtp_configured

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    def validate_production_config(self) -> None:
        if self.app_env.casefold() != "production":
            return

        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL debe apuntar a PostgreSQL en producción")
        sslmode = parse_qs(urlsplit(self.database_url).query).get("sslmode", [""])[0]
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise ValueError(
                "DATABASE_URL debe exigir TLS con sslmode=require o superior"
            )
        if len(self.jwt_secret) < 32 or self.jwt_secret == "change-me-in-.env":
            raise ValueError(
                "JWT_SECRET debe ser un secreto aleatorio de al menos 32 caracteres"
            )
        frontend_url = urlsplit(self.frontend_base_url)
        if frontend_url.scheme != "https" or not frontend_url.netloc:
            raise ValueError("FRONTEND_BASE_URL debe usar HTTPS en producción")
        origins = self.cors_origins_list
        if not origins or any(not _is_https_origin(origin) for origin in origins):
            raise ValueError("CORS_ORIGINS debe contener únicamente orígenes HTTPS")
        if not self.email_configured:
            raise ValueError("El proveedor de correo seleccionado no está configurado")


def _is_https_origin(origin: str) -> bool:
    parsed = urlsplit(origin)
    return bool(
        parsed.scheme == "https"
        and parsed.hostname
        and parsed.hostname != "*"
        and not parsed.path
        and not parsed.query
        and not parsed.fragment
    )


settings = Settings()
