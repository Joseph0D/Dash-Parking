"""
Módulo: account_service.py
Qué: Registro, login y vehículos de las cuentas de la base nueva (`usuario`, `vehiculo`).
Para qué: Que un cliente tenga sesión y vehículos propios antes de reservar (módulos
          Autenticación/Roles y Gestión de Vehículos del informe).
Impacto: Las contraseñas solo se guardan hasheadas (bcrypt). Un registro siempre crea rol
         `cliente`; dueños y administradores se asignan fuera de la API.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.parking_auth import Account, create_account_token
from app.core.security import hash_password, verify_password
from app.schemas.accounts import (
    AccountResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VehicleCreate,
    VehicleResponse,
)
from app.services.parking_errors import translate_db_error


def _token_for(account: Account) -> TokenResponse:
    return TokenResponse(
        access_token=create_account_token(account.id, account.role),
        user=AccountResponse(**account.__dict__),
    )


def register(db: Session, data: RegisterRequest) -> TokenResponse:
    try:
        row = (
            db.execute(
                text(
                    """
                    INSERT INTO usuario (nombres, apellidos, documento_id, telefono, correo,
                                         password_hash, id_rol)
                    VALUES (:first_name, :last_name, :document_id, :phone, lower(:email),
                            :password_hash, (SELECT id_rol FROM rol WHERE nombre_rol = 'cliente'))
                    RETURNING id_usuario AS id
                    """
                ),
                {
                    "first_name": data.first_name.strip(),
                    "last_name": data.last_name.strip(),
                    "document_id": data.document_id.strip(),
                    "phone": data.phone.strip(),
                    "email": data.email.strip(),
                    "password_hash": hash_password(data.password),
                },
            )
            .mappings()
            .one()
        )
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc

    return _token_for(
        Account(
            id=row["id"],
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=data.email.strip().lower(),
            role="cliente",
        )
    )


def login(db: Session, data: LoginRequest) -> TokenResponse:
    row = (
        db.execute(
            text(
                """
                SELECT u.id_usuario AS id, u.nombres AS first_name, u.apellidos AS last_name,
                       u.correo AS email, r.nombre_rol AS role, u.password_hash
                FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                WHERE lower(u.correo) = lower(:email)
                """
            ),
            {"email": data.email.strip()},
        )
        .mappings()
        .first()
    )
    # Mismo mensaje para "no existe", "sin contraseña" y "contraseña incorrecta": no revela cuentas.
    if (
        row is None
        or row["password_hash"] is None
        or not verify_password(data.password, row["password_hash"])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")
    return _token_for(
        Account(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            role=row["role"],
        )
    )


_VEHICLE_SELECT = """
    SELECT v.id_vehiculo AS id, v.placa AS plate, v.id_tipo_vehiculo AS vehicle_type_id,
           tv.nombre_tipo AS vehicle_type_name, v.marca AS brand, v.modelo AS model, v.color
    FROM vehiculo v JOIN tipo_vehiculo tv ON tv.id_tipo_vehiculo = v.id_tipo_vehiculo
"""


def list_vehicles(db: Session, account: Account) -> list[VehicleResponse]:
    rows = db.execute(
        text(_VEHICLE_SELECT + " WHERE v.id_usuario = :uid ORDER BY v.id_vehiculo"),
        {"uid": account.id},
    ).mappings()
    return [VehicleResponse(**row) for row in rows]


def create_vehicle(db: Session, account: Account, data: VehicleCreate) -> VehicleResponse:
    try:
        new_id = db.execute(
            text(
                """
                INSERT INTO vehiculo (id_usuario, id_tipo_vehiculo, placa, marca, modelo, color)
                VALUES (:uid, :vtype, upper(:plate), :brand, :model, :color)
                RETURNING id_vehiculo
                """
            ),
            {
                "uid": account.id,
                "vtype": data.vehicle_type_id,
                "plate": data.plate.strip(),
                "brand": data.brand,
                "model": data.model,
                "color": data.color,
            },
        ).scalar_one()
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise translate_db_error(exc) from exc
    row = (
        db.execute(text(_VEHICLE_SELECT + " WHERE v.id_vehiculo = :id"), {"id": new_id})
        .mappings()
        .one()
    )
    return VehicleResponse(**row)
