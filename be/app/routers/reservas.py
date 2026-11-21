"""
Router: reservas.py
Qué: Reservar con pago simulado, listar y cancelar reservas, y operaciones del dueño
     (reservas del parqueadero, ingreso y salida de vehículos).
Para qué: MVP del informe — `POST /api/v1/reservas/crear` — y el ciclo completo del espacio:
          Disponible → Reservado → Ocupado → Disponible.
Impacto: Cada endpoint valida el rol: un cliente solo ve y cancela SUS reservas, y el dueño
         solo gestiona los parqueaderos donde es propietario.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.parking_auth import (
    ROLE_ADMIN,
    ROLE_OWNER,
    Account,
    get_current_account,
    require_roles,
)
from app.parking_database import get_parking_db
from app.schemas.reservas import (
    CancelacionResponse,
    CrearReservaRequest,
    ReservaCreadaResponse,
    ReservaDetalle,
    SalidaResponse,
    TicketActivo,
)
from app.services import reserva_service as service

router = APIRouter(prefix="/api/v1", tags=["reservas"])

managers_only = require_roles(ROLE_OWNER, ROLE_ADMIN)


@router.post(
    "/reservas/crear", response_model=ReservaCreadaResponse, status_code=status.HTTP_201_CREATED
)
def crear_reserva(
    data: CrearReservaRequest,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_parking_db),
) -> ReservaCreadaResponse:
    return service.create_reservation(db, account, data)


@router.get("/reservas/mias", response_model=list[ReservaDetalle])
def mis_reservas(
    account: Account = Depends(get_current_account), db: Session = Depends(get_parking_db)
) -> list[ReservaDetalle]:
    return service.list_my_reservations(db, account)


@router.post("/reservas/{reserva_id}/cancelar", response_model=CancelacionResponse)
def cancelar_reserva(
    reserva_id: int,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_parking_db),
) -> CancelacionResponse:
    return service.cancel_reservation(db, account, reserva_id)


@router.get("/reservas/parqueadero", response_model=list[ReservaDetalle])
def reservas_del_parqueadero(
    solo_vigentes: bool = True,
    account: Account = Depends(managers_only),
    db: Session = Depends(get_parking_db),
) -> list[ReservaDetalle]:
    return service.list_managed_reservations(db, account, solo_vigentes)


@router.post("/reservas/{reserva_id}/ingreso", response_model=ReservaDetalle)
def registrar_ingreso(
    reserva_id: int,
    account: Account = Depends(managers_only),
    db: Session = Depends(get_parking_db),
) -> ReservaDetalle:
    return service.register_entry(db, account, reserva_id)


@router.get("/tickets/activos", response_model=list[TicketActivo])
def tickets_activos(
    account: Account = Depends(managers_only), db: Session = Depends(get_parking_db)
) -> list[TicketActivo]:
    return service.list_active_tickets(db, account)


@router.post("/tickets/{ticket_id}/salida", response_model=SalidaResponse)
def registrar_salida(
    ticket_id: int,
    account: Account = Depends(managers_only),
    db: Session = Depends(get_parking_db),
) -> SalidaResponse:
    return service.register_exit(db, account, ticket_id)
