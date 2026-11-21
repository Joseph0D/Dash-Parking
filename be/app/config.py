"""
Módulo: config.py
Qué: Configuración centralizada de la aplicación, leída desde variables de entorno.
Para qué: Evitar valores hardcodeados (RS-001 de docs/requisitos/restricciones.md).
Impacto: Si falta una variable crítica (ej. JWT_SECRET), el arranque debe fallar explícitamente
         en vez de usar un valor inseguro por defecto en producción.
"""
from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_env: str = "development"

    # Sprint 0 usaba datos en memoria; desde este entregable la app requiere PostgreSQL real.
    database_url: str = "postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking"

    # Base legada que se conserva como respaldo; no es la fuente de disponibilidad nueva.
    parking_database_url: str = (
        "postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking_v2"
    )

    jwt_secret: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8  # 8 horas

    cors_origins: str = "http://localhost:5173"
    frontend_base_url: str = "http://localhost:5173"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

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
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
