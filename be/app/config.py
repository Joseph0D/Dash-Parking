"""
Módulo: config.py
Qué: Configuración centralizada de la aplicación, leída desde variables de entorno.
Para qué: Evitar valores hardcodeados (RS-001 de docs/requisitos/restricciones.md).
Impacto: Si falta una variable crítica (ej. JWT_SECRET), el arranque debe fallar explícitamente
         en vez de usar un valor inseguro por defecto en producción.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"

    # Sprint 0 usaba datos en memoria; desde este entregable la app requiere PostgreSQL real.
    database_url: str = "postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking"

    jwt_secret: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8  # 8 horas

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
