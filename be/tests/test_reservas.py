"""
Pruebas de cuentas, reservas con pago simulado y operaciones del dueño.

Necesitan la base nueva cargada y la variable PARKING_TEST_DATABASE_URL (ver db/README.md).
Cada prueba corre dentro de una transacción que se revierte: no deja datos.
"""

from __future__ import annotations

import os
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.main import app
from app.parking_database import get_parking_db
from app.services import availability_service as availability
from app.services import payment_simulator
from app.services.payment_simulator import PaymentMethod, simulate_charge

PARKING_TEST_DB = os.getenv("PARKING_TEST_DATABASE_URL")
requires_parking_db = pytest.mark.skipif(
    not PARKING_TEST_DB, reason="Define PARKING_TEST_DATABASE_URL (ver db/README.md)"
)

CAR_SPACE = 1  # A-001, zona de carros (datos del dump)
MOTO_SPACE = 201  # zona de motos


def tomorrow_at(hour: int):
    return (availability.now_colombia() + timedelta(days=1)).replace(
        hour=hour, minute=0, second=0, microsecond=0
    )


def slot(start_hour: int, end_hour: int) -> dict[str, str]:
    return {
        "fecha_inicio": tomorrow_at(start_hour).isoformat(),
        "fecha_fin": tomorrow_at(end_hour).isoformat(),
    }


# ---------------------------------------------------------------- unitarias (sin base de datos)


def test_simulator_approves_valid_amount():
    result = simulate_charge(PaymentMethod.NEQUI, Decimal(30000))
    assert result.approved and result.reference.startswith("SIM-NEQ-")


def test_simulator_rejects_invalid_or_over_limit_amounts():
    assert not simulate_charge(PaymentMethod.PSE, Decimal(0)).approved
    over = payment_simulator.MAX_SIMULATED_AMOUNT + 1
    assert not simulate_charge(PaymentMethod.DAVIPLATA, over).approved


# ---------------------------------------------------------------- integración (PostgreSQL real)


@pytest.fixture()
def api():
    engine = create_engine(PARKING_TEST_DB)
    connection = engine.connect()
    transaction = connection.begin()
    # create_savepoint: los commit/rollback del servicio no tocan la transacción externa
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    app.dependency_overrides[get_parking_db] = lambda: session
    with TestClient(app) as client:
        client.session = session
        yield client
    app.dependency_overrides.pop(get_parking_db, None)
    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()


def register(api: TestClient, email: str) -> dict[str, str]:
    resp = api.post(
        "/api/v1/accounts/register",
        json={
            "first_name": "Prueba",
            "last_name": "Cliente",
            "document_id": f"DOC-{abs(hash(email)) % 10**9}",
            "phone": "3001234567",
            "email": email,
            "password": "Secreta123!",
        },
    )
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def add_vehicle(api: TestClient, headers, plate: str, type_id: int = 1) -> int:
    resp = api.post(
        "/api/v1/accounts/me/vehicles",
        headers=headers,
        json={"plate": plate, "vehicle_type_id": type_id, "brand": "Mazda"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def reserve(api, headers, vehicle_id, start_hour=10, end_hour=11, space=CAR_SPACE, method="Nequi"):
    body = {
        "id_estacionamiento": 1,
        "id_vehiculo": vehicle_id,
        "metodo_pago": method,
        **slot(start_hour, end_hour),
    }
    if space is not None:
        body["id_espacio"] = space
    return api.post("/api/v1/reservas/crear", headers=headers, json=body)


def space_status(api, space_id: int, start_hour: int, end_hour: int, type_id: int = 1) -> str:
    resp = api.get(
        "/api/v1/parking-lots/1/spaces",
        params={
            "vehicle_type_id": type_id,
            "start": tomorrow_at(start_hour).isoformat(),
            "end": tomorrow_at(end_hour).isoformat(),
        },
    )
    return next(s["status"] for s in resp.json()["spaces"] if s["id"] == space_id)


@requires_parking_db
def test_register_login_and_me(api):
    headers = register(api, "nuevo@correo.com")
    assert api.get("/api/v1/accounts/me", headers=headers).json()["role"] == "cliente"
    login = api.post(
        "/api/v1/accounts/login", json={"email": "NUEVO@correo.com", "password": "Secreta123!"}
    )
    assert login.status_code == 200 and login.json()["user"]["email"] == "nuevo@correo.com"


@requires_parking_db
def test_duplicate_email_and_wrong_password(api):
    register(api, "dup@correo.com")
    again = api.post(
        "/api/v1/accounts/register",
        json={
            "first_name": "Otro",
            "last_name": "Usuario",
            "document_id": "DOC-OTRO-1",
            "phone": "3001234567",
            "email": "dup@correo.com",
            "password": "Secreta123!",
        },
    )
    assert again.status_code == 409
    bad = api.post("/api/v1/accounts/login", json={"email": "dup@correo.com", "password": "mal"})
    assert bad.status_code == 401


@requires_parking_db
def test_endpoints_require_a_valid_account_token(api):
    assert api.get("/api/v1/accounts/me").status_code == 401
    assert (
        api.get("/api/v1/accounts/me", headers={"Authorization": "Bearer xyz"}).status_code == 401
    )
    assert api.post("/api/v1/reservas/crear", json={}).status_code == 401


@requires_parking_db
def test_vehicles_create_list_and_duplicate_plate(api):
    headers = register(api, "veh@correo.com")
    add_vehicle(api, headers, "zzz999")
    listed = api.get("/api/v1/accounts/me/vehicles", headers=headers).json()
    assert [v["plate"] for v in listed] == ["ZZZ999"] and listed[0]["vehicle_type_name"] == "Carro"
    dup = api.post(
        "/api/v1/accounts/me/vehicles",
        headers=headers,
        json={"plate": "ZZZ999", "vehicle_type_id": 1},
    )
    assert dup.status_code == 409


@requires_parking_db
def test_reserve_and_pay_follows_report_contract(api):
    headers = register(api, "res@correo.com")
    vehicle_id = add_vehicle(api, headers, "RES001")
    resp = reserve(api, headers, vehicle_id)

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert (body["status"], body["code"]) == ("success", 201)
    data = body["data"]
    assert data["id_espacio"] == CAR_SPACE and data["estado_espacio"] == "Reservado"
    assert data["id_comprobante"].startswith("COMP-")
    summary = data["resumen"]
    assert Decimal(summary["monto_total"]) == Decimal(30000)  # 60 min x $500
    assert (summary["metodo_pago"], summary["estado_pago"]) == ("Nequi", "Aprobado")
    assert summary["placa"] == "RES001" and summary["numero_espacio"] == "A-001"


@requires_parking_db
def test_reserve_without_space_assigns_a_free_one(api):
    headers = register(api, "auto@correo.com")
    vehicle_id = add_vehicle(api, headers, "AUT001")
    resp = reserve(api, headers, vehicle_id, space=None, method="Daviplata")
    assert resp.status_code == 201
    assert space_status(api, resp.json()["data"]["id_espacio"], 10, 11) == "reserved"


@requires_parking_db
def test_reservation_only_occupies_its_time_slot(api):
    headers = register(api, "slot@correo.com")
    reserve(api, headers, add_vehicle(api, headers, "SLT001"))
    assert space_status(api, CAR_SPACE, 10, 11) == "reserved"
    assert space_status(api, CAR_SPACE, 9, 10) == "available"
    assert space_status(api, CAR_SPACE, 11, 12) == "available"


@requires_parking_db
def test_overlapping_reservation_is_409_but_back_to_back_is_allowed(api):
    first = register(api, "uno@correo.com")
    second = register(api, "dos@correo.com")
    reserve(api, first, add_vehicle(api, first, "UNO001"))
    second_vehicle = add_vehicle(api, second, "DOS001")

    assert reserve(api, second, second_vehicle, 10, 11).status_code == 409
    assert reserve(api, second, second_vehicle, 11, 12).status_code == 201


@requires_parking_db
def test_cannot_use_another_users_vehicle_or_wrong_vehicle_type(api):
    owner = register(api, "due@correo.com")
    thief = register(api, "ladron@correo.com")
    owner_vehicle = add_vehicle(api, owner, "DUE001")
    assert reserve(api, thief, owner_vehicle).status_code == 400

    # un carro no puede reservar un espacio de la zona de motos
    assert reserve(api, owner, owner_vehicle, space=MOTO_SPACE).status_code == 400


@requires_parking_db
def test_rejected_payment_leaves_no_reservation(api, monkeypatch):
    monkeypatch.setattr(payment_simulator, "MAX_SIMULATED_AMOUNT", Decimal(1000))
    headers = register(api, "rech@correo.com")
    resp = reserve(api, headers, add_vehicle(api, headers, "RCH001"))

    assert resp.status_code == 402
    assert api.get("/api/v1/reservas/mias", headers=headers).json() == []
    assert space_status(api, CAR_SPACE, 10, 11) == "available"


@requires_parking_db
def test_cancel_refunds_and_frees_the_space(api):
    headers = register(api, "can@correo.com")
    other = register(api, "otro@correo.com")
    reserva_id = reserve(api, headers, add_vehicle(api, headers, "CAN001")).json()["data"][
        "id_reserva"
    ]

    assert api.post(f"/api/v1/reservas/{reserva_id}/cancelar", headers=other).status_code == 404
    done = api.post(f"/api/v1/reservas/{reserva_id}/cancelar", headers=headers)
    assert done.status_code == 200
    assert Decimal(done.json()["monto_reembolsado"]) == Decimal(30000)

    mine = api.get("/api/v1/reservas/mias", headers=headers).json()[0]
    assert (mine["estado_reserva"], mine["estado_pago"]) == ("cancelada", "Reembolsado")
    assert space_status(api, CAR_SPACE, 10, 11) == "available"
    assert api.post(f"/api/v1/reservas/{reserva_id}/cancelar", headers=headers).status_code == 400


def make_staff(api: TestClient, email: str, role: str, owns_lot: bool) -> dict[str, str]:
    """Crea (dentro de la transacción de prueba) un dueño o administrador y devuelve su token."""
    api.session.execute(
        text(
            """
            INSERT INTO usuario (nombres, apellidos, documento_id, telefono, correo,
                                 password_hash, id_rol)
            VALUES ('Staff', 'Prueba', :doc, '3000000000', :email, :pw,
                    (SELECT id_rol FROM rol WHERE nombre_rol = :role))
            """
        ),
        {
            "doc": f"S-{abs(hash(email)) % 10**9}",
            "email": email,
            "pw": hash_password("Staff123!"),
            "role": role,
        },
    )
    if owns_lot:
        api.session.execute(
            text(
                "UPDATE estacionamiento SET id_propietario = "
                "(SELECT id_usuario FROM usuario WHERE correo = :email) "
                "WHERE id_estacionamiento = 1"
            ),
            {"email": email},
        )
    login = api.post("/api/v1/accounts/login", json={"email": email, "password": "Staff123!"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@requires_parking_db
def test_owner_endpoints_are_forbidden_to_clients_and_foreign_owners(api):
    client = register(api, "cli@correo.com")
    assert api.get("/api/v1/reservas/parqueadero", headers=client).status_code == 403
    assert api.get("/api/v1/tickets/activos", headers=client).status_code == 403

    reserve(api, client, add_vehicle(api, client, "CLI001"))
    stranger = make_staff(api, "ajeno@correo.com", "dueno", owns_lot=False)
    reserva_id = api.get("/api/v1/reservas/mias", headers=client).json()[0]["id_reserva"]
    assert api.post(f"/api/v1/reservas/{reserva_id}/ingreso", headers=stranger).status_code == 403
    assert api.get("/api/v1/reservas/parqueadero", headers=stranger).json() == []


@requires_parking_db
def test_full_lifecycle_reserved_occupied_available(api):
    """Disponible -> Reservado -> Ocupado -> Disponible (el dueño registra ingreso y salida)."""
    client = register(api, "ciclo@correo.com")
    owner = make_staff(api, "dueno-test@correo.com", "dueno", owns_lot=True)
    vehicle_id = add_vehicle(api, client, "CIC001")

    now = availability.now_colombia()
    resp = api.post(
        "/api/v1/reservas/crear",
        headers=client,
        json={
            "id_estacionamiento": 1,
            "id_vehiculo": vehicle_id,
            "id_espacio": CAR_SPACE,
            "metodo_pago": "Tarjeta Credito",
            "fecha_inicio": (now + timedelta(minutes=1)).isoformat(),
            "fecha_fin": (now + timedelta(hours=1, minutes=1)).isoformat(),
        },
    )
    assert resp.status_code == 201, resp.text
    reserva_id = resp.json()["data"]["id_reserva"]

    listed = api.get("/api/v1/reservas/parqueadero", headers=owner).json()
    assert reserva_id in [r["id_reserva"] for r in listed]

    # Ingreso: el espacio pasa a Ocupado y la reserva a "en curso"
    entry = api.post(f"/api/v1/reservas/{reserva_id}/ingreso", headers=owner)
    assert entry.status_code == 200, entry.text
    assert (entry.json()["estado_reserva"], entry.json()["estado_espacio"]) == (
        "en curso",
        "Ocupado",
    )
    now_window = {
        "vehicle_type_id": 1,
        # Se consulta desde 2 minutos antes porque, dentro de la transacción de prueba,
        # LOCALTIMESTAMP es la hora en que empezó la transacción (en producción, cada
        # petición tiene la suya).
        "start": (now - timedelta(minutes=2)).isoformat(),
        "end": (now + timedelta(minutes=30)).isoformat(),
    }
    spaces = api.get("/api/v1/parking-lots/1/spaces", params=now_window).json()["spaces"]
    assert next(s for s in spaces if s["id"] == CAR_SPACE)["status"] == "occupied"
    assert api.post(f"/api/v1/reservas/{reserva_id}/ingreso", headers=owner).status_code == 400

    tickets = api.get("/api/v1/tickets/activos", headers=owner).json()
    ticket = next(t for t in tickets if t["id_reserva"] == reserva_id)
    assert ticket["placa"] == "CIC001"

    # Salida: el espacio queda libre y la reserva finalizada
    exit_ = api.post(f"/api/v1/tickets/{ticket['id_ticket']}/salida", headers=owner)
    assert exit_.status_code == 200, exit_.text
    spaces = api.get("/api/v1/parking-lots/1/spaces", params=now_window).json()["spaces"]
    assert next(s for s in spaces if s["id"] == CAR_SPACE)["status"] == "available"
    mine = api.get("/api/v1/reservas/mias", headers=client).json()[0]
    assert mine["estado_reserva"] == "finalizada"


@requires_parking_db
def test_entry_before_the_reserved_time_is_rejected(api):
    client = register(api, "temprano@correo.com")
    owner = make_staff(api, "dueno-early@correo.com", "dueno", owns_lot=True)
    reserva_id = reserve(api, client, add_vehicle(api, client, "TMP001")).json()["data"][
        "id_reserva"
    ]
    resp = api.post(f"/api/v1/reservas/{reserva_id}/ingreso", headers=owner)
    assert resp.status_code == 400 and "15 minutos" in resp.json()["detail"]
