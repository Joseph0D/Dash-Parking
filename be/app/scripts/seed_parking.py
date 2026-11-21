"""
Módulo: seed_parking.py
Qué: Completa los datos vacíos de la base nueva (`dash_parking_v2`): contraseña de los usuarios
     que no tienen, cuentas de administrador y dueño, y el dueño del parqueadero.
Para qué: Que haya con qué iniciar sesión (cliente, dueño, administrador) y que cada
          parqueadero tenga propietario, sin cargar nada a mano.
Impacto: Solo credenciales de DESARROLLO (ver db/README.md); cambiarlas en cualquier despliegue
         real. Es idempotente y tolerante: si la base nueva aún no está cargada, avisa y
         termina sin error para no impedir el arranque del backend.

Uso: python -m app.scripts.seed_parking
"""

from __future__ import annotations

import os

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.core.security import hash_password
from app.parking_database import ParkingSessionLocal

DEMO_CLIENT_PASSWORD = os.getenv("DEMO_CLIENT_PASSWORD", "Cliente123!")

# Mismos correos y contraseñas que el seed anterior para el administrador, así hay un solo
# juego de credenciales de demostración.
STAFF = (
    {
        "role": "administrador",
        "first_name": "Administrador",
        "last_name": "Dash Parking",
        "document_id": "ADMIN-0001",
        "phone": "3000000001",
        "email": "admin@dashparking.dev",
        "password": "Admin123!",
    },
    {
        "role": "dueno",
        "first_name": "Dueño",
        "last_name": "Parqueadero Central",
        "document_id": "DUENO-0001",
        "phone": "3000000002",
        "email": "dueno@dashparking.dev",
        "password": "Dueno123!",
    },
)


def seed() -> None:
    with ParkingSessionLocal() as db:
        # 1) Usuarios existentes sin contraseña: se les asigna la de demostración de clientes.
        pending = (
            db.execute(
                text("SELECT id_usuario FROM usuario WHERE password_hash IS NULL ORDER BY 1")
            )
            .scalars()
            .all()
        )
        if pending:
            hashed = hash_password(DEMO_CLIENT_PASSWORD)  # un solo hash: mismo valor, mismo costo
            db.execute(
                text("UPDATE usuario SET password_hash = :h WHERE id_usuario = ANY(:ids)"),
                {"h": hashed, "ids": pending},
            )
        print(f"[seed_parking] Usuarios con contraseña de demostración asignada: {len(pending)}")

        # 2) Administrador y dueño
        for person in STAFF:
            exists = db.execute(
                text("SELECT 1 FROM usuario WHERE lower(correo) = :email"),
                {"email": person["email"]},
            ).first()
            if exists:
                continue
            db.execute(
                text(
                    """
                    INSERT INTO usuario (nombres, apellidos, documento_id, telefono, correo,
                                         password_hash, id_rol)
                    VALUES (:first_name, :last_name, :document_id, :phone, :email, :password_hash,
                            (SELECT id_rol FROM rol WHERE nombre_rol = :role))
                    """
                ),
                {**person, "password_hash": hash_password(person["password"])},
            )
            print(f"[seed_parking] Cuenta creada: {person['email']} ({person['role']})")

        # 3) Propietario de los parqueaderos que no tienen
        updated = db.execute(
            text(
                """
                UPDATE estacionamiento
                SET id_propietario = (SELECT id_usuario FROM usuario WHERE correo = :email)
                WHERE id_propietario IS NULL
                """
            ),
            {"email": "dueno@dashparking.dev"},
        ).rowcount
        print(f"[seed_parking] Parqueaderos con propietario asignado: {updated}")
        db.commit()


if __name__ == "__main__":
    try:
        seed()
    except (OperationalError, ProgrammingError) as exc:
        print(
            "[seed_parking] Omitido: la base dash_parking_v2 no está disponible o sin cargar "
            f"(ver db/README.md). Detalle: {type(exc).__name__}"
        )
