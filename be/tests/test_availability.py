"""
Pruebas de disponibilidad por franja (parqueaderos, tipos de vehículo y espacios).

Las reglas viven en PostgreSQL (db/migrations/002_*.sql), por eso las pruebas de integración
necesitan la base de disponibilidad cargada y la variable PARKING_TEST_DATABASE_URL, por ejemplo:

    PARKING_TEST_DATABASE_URL=postgresql+psycopg://dash_parking:dash_parking@localhost:5432/dash_parking_v2

Cada prueba corre dentro de una transacción que se revierte, así que no deja datos.
Sin la variable, solo se ejecutan las pruebas unitarias de validación de la franja.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.main import app
from app.parking_database import get_parking_db
from app.services import availability_service as service

PARKING_TEST_DB = os.getenv("PARKING_TEST_DATABASE_URL")
requires_parking_db = pytest.mark.skipif(
    not PARKING_TEST_DB, reason="Define PARKING_TEST_DATABASE_URL (ver db/README.md)"
)


def tomorrow_at(hour: int) -> datetime:
    return (service.now_colombia() + timedelta(days=1)).replace(
        hour=hour, minute=0, second=0, microsecond=0
    )


def window(start_hour: int, end_hour: int) -> dict[str, str]:
    return {
        "start": tomorrow_at(start_hour).isoformat(),
        "end": tomorrow_at(end_hour).isoformat(),
    }


# ---------------------------------------------------------------- unitarias (sin base de datos)


def test_normalize_window_rejects_end_before_start():
    with pytest.raises(service.InvalidTimeWindowError):
        service.normalize_window(tomorrow_at(11), tomorrow_at(10))


def test_normalize_window_rejects_past_start():
    past = service.now_colombia() - timedelta(hours=2)
    with pytest.raises(service.InvalidTimeWindowError):
        service.normalize_window(past, past + timedelta(hours=1))


def test_normalize_window_converts_utc_to_colombia():
    # 15:00 UTC == 10:00 en Colombia (UTC-5, sin horario de verano)
    start_utc = tomorrow_at(15).replace(tzinfo=service.timezone.utc)
    start, end = service.normalize_window(start_utc, start_utc + timedelta(hours=1))
    assert (start.hour, end.hour, start.tzinfo) == (10, 11, None)


# ---------------------------------------------------------------- integración (PostgreSQL real)


@pytest.fixture()
def parking_client():
    engine = create_engine(PARKING_TEST_DB)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    app.dependency_overrides[get_parking_db] = lambda: session
    with TestClient(app) as test_client:
        test_client.session = session
        yield test_client
    app.dependency_overrides.pop(get_parking_db, None)

    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()


def space_status(client: TestClient, space_id: int, start_hour: int, end_hour: int) -> str:
    resp = client.get(
        "/api/v1/parking-lots/1/spaces",
        params={"vehicle_type_id": 1, **window(start_hour, end_hour)},
    )
    assert resp.status_code == 200
    return next(s["status"] for s in resp.json()["spaces"] if s["id"] == space_id)


@requires_parking_db
def test_list_parking_lots(parking_client):
    resp = parking_client.get("/api/v1/parking-lots")
    assert resp.status_code == 200
    lot = resp.json()[0]
    assert {"id", "name", "identification", "address", "phone", "total_capacity"} <= lot.keys()


@requires_parking_db
def test_vehicle_types_include_hourly_price(parking_client):
    resp = parking_client.get("/api/v1/parking-lots/1/vehicle-types")
    assert resp.status_code == 200
    car = next(t for t in resp.json() if t["id"] == 1)
    assert Decimal(car["price_per_hour"]) == Decimal(30000)  # 500 por minuto (datos del dump)


@requires_parking_db
def test_zone_availability_is_consistent(parking_client):
    resp = parking_client.get("/api/v1/parking-lots/1/availability", params=window(10, 11))
    assert resp.status_code == 200
    zones = resp.json()["zones"]
    assert zones
    for zone in zones:
        assert zone["available"] + zone["reserved"] + zone["occupied"] <= zone["capacity"]


@requires_parking_db
def test_spaces_grid_has_status_and_estimated_price(parking_client):
    resp = parking_client.get(
        "/api/v1/parking-lots/1/spaces", params={"vehicle_type_id": 1, **window(10, 11)}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert Decimal(body["estimated_price"]) == Decimal(30000)  # 60 min x 500
    assert body["available_count"] == sum(s["status"] == "available" for s in body["spaces"])
    assert {s["zone_name"] for s in body["spaces"]} == {body["spaces"][0]["zone_name"]}


@requires_parking_db
def test_space_is_reserved_only_during_its_time_slot(parking_client):
    """Reservar de 10:00 a 11:00 no ocupa el espacio a las 9:00 ni a las 11:00."""
    before = parking_client.get(
        "/api/v1/parking-lots/1/spaces", params={"vehicle_type_id": 1, **window(10, 11)}
    ).json()["available_count"]

    parking_client.session.execute(
        text("SELECT fn_crear_reserva(1, 1, 1, :s, :e, 1)"),
        {"s": tomorrow_at(10), "e": tomorrow_at(11)},
    )

    assert space_status(parking_client, 1, 10, 11) == "reserved"
    assert space_status(parking_client, 1, 9, 10) == "available"
    assert space_status(parking_client, 1, 11, 12) == "available"
    assert space_status(parking_client, 1, 10, 12) == "reserved"  # franja que se cruza
    after = parking_client.get(
        "/api/v1/parking-lots/1/spaces", params={"vehicle_type_id": 1, **window(10, 11)}
    ).json()["available_count"]
    assert after == before - 1


@requires_parking_db
def test_unknown_parking_lot_is_404(parking_client):
    assert parking_client.get("/api/v1/parking-lots/999/vehicle-types").status_code == 404
    resp = parking_client.get("/api/v1/parking-lots/999/availability", params=window(10, 11))
    assert resp.status_code == 404


@requires_parking_db
def test_unknown_vehicle_type_is_404(parking_client):
    resp = parking_client.get(
        "/api/v1/parking-lots/1/spaces", params={"vehicle_type_id": 999, **window(10, 11)}
    )
    assert resp.status_code == 404


@requires_parking_db
def test_invalid_windows_are_422(parking_client):
    reversed_window = {"start": tomorrow_at(11).isoformat(), "end": tomorrow_at(10).isoformat()}
    assert (
        parking_client.get(
            "/api/v1/parking-lots/1/availability", params=reversed_window
        ).status_code
        == 422
    )
    past = service.now_colombia() - timedelta(hours=3)
    past_window = {"start": past.isoformat(), "end": (past + timedelta(hours=1)).isoformat()}
    assert (
        parking_client.get("/api/v1/parking-lots/1/availability", params=past_window).status_code
        == 422
    )
    assert parking_client.get("/api/v1/parking-lots/1/availability").status_code == 422
