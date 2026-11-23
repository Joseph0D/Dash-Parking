"""
Módulo: main.py
Qué: Punto de entrada de la API de Dash Parking.
Para qué: Registra los routers y crea el esquema solo en desarrollo; producción migra antes
         de iniciar el servidor.
Impacto: Es el proceso que expone toda la funcionalidad — auth, vehículos, sesiones, reservas,
         pagos y reportes.

En desarrollo las tablas se crean automáticamente para facilitar `docker compose up`. En
producción, el contenedor aplica primero las migraciones versionadas y el servicio no modifica el
esquema al arrancar.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import *  # noqa: F401,F403  — registra todos los modelos antes de create_all
from app.routers import (
    accounts,
    auth,
    availability,
    owner_parking_lots,
    payments,
    rates,
    reports,
    reservas,
    reservations,
    sessions,
    spots,
    vehicles,
)

app = FastAPI(
    title="Dash Parking API",
    description="Sistema de gestión integral de un parqueadero.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if settings.app_env.casefold() == "production":
        settings.validate_production_config()
        return
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(availability.router)
app.include_router(owner_parking_lots.router)
app.include_router(accounts.router)
app.include_router(reservas.router)
app.include_router(spots.router)
app.include_router(rates.router)
app.include_router(sessions.router)
app.include_router(reservations.router)
app.include_router(payments.router)
app.include_router(reports.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Endpoint de verificación de salud del servicio (usado por el healthcheck de Docker)."""
    return {"status": "ok"}
