"""
Módulo: main.py
Qué: Punto de entrada de la API de Dash Parking.
Para qué: Registra todos los routers del sistema y prepara la base de datos al arrancar.
Impacto: Es el proceso que expone toda la funcionalidad — auth, vehículos, sesiones, reservas,
         pagos y reportes.

Nota de alcance (MVP académico): las tablas se crean con `Base.metadata.create_all()` al iniciar,
en vez de usar migraciones con Alembic. Es una simplificación deliberada para que el equipo pueda
levantar el proyecto con `docker compose up` sin pasos adicionales; migrar a Alembic es la mejora
natural una vez el esquema se estabilice (no cambia ningún contrato de la API).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import *  # noqa: F401,F403  — registra todos los modelos antes de create_all
from app.routers import auth, payments, rates, reports, reservations, sessions, spots, vehicles

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
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(vehicles.router)
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
