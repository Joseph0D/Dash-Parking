#!/bin/sh
# Carga la base de disponibilidad (dash_parking_v2) con el estado final del esquema en español.
# Para qué: que `docker compose up` deje lista la base que consume la API de disponibilidad.
# Impacto: la imagen de Postgres ejecuta este script SOLO cuando el volumen está vacío. Si ya
#          existía el volumen, cargar la base a mano (ver db/README.md).
set -e
createdb -U "$POSTGRES_USER" dash_parking_v2
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d dash_parking_v2 -f /db/dash_parking_complete.sql
