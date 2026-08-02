"""
Módulo: main.py
Qué: Punto de entrada de la API de Dash Parking.
Para qué: Registra los routers disponibles. Sprint 0 solo expone el flujo de ingreso;
          los demás módulos (salida, tarifas, reportes, clientes) se agregan sprint a sprint
          según la progresión definida en entregable-s01-plan-de-trabajo.md.
"""
from fastapi import FastAPI

from app.routers import vehicles

app = FastAPI(
    title="Dash Parking API",
    description="Sistema de gestión integral de un parqueadero.",
    version="0.1.0",
)

app.include_router(vehicles.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Endpoint de verificación de salud del servicio (útil para Docker healthchecks futuros)."""
    return {"status": "ok"}


