# Base de datos — Dash Parking (esquema en español)

> **Estado:** el backend (`be/`) todavía usa el esquema anterior (tablas en inglés, IDs UUID).
> Mientras no se migre, esta base debe vivir en una base **separada** (`dash_parking_v2`)
> para no mezclarse con las tablas que crea `python -m app.scripts.seed`.

## Archivos

| Archivo | Para qué |
|---|---|
| `migrations/001_fix_missing_fields_and_integration.sql` | Campos vacíos/faltantes + roles, comprobante, pago de reservas |
| `migrations/002_time_based_reservations.sql` | Reservas por franja horaria (requiere la 001) |
| `tests/time_based_reservations_test.sql` | Pruebas (corren en una transacción y hacen `ROLLBACK`) |
| `dash_parking_complete.sql` | Estado final listo para una base nueva (dump original + 001 + 002) |

## Opción A — con Docker Compose (automático)

`docker compose up` crea `dash_parking_v2` y carga `dash_parking_complete.sql` mediante
`db/init/01-create-parking-v2.sh`. **Solo ocurre cuando el volumen está vacío.** Si ya tienes el
volumen de antes, tienes dos caminos: `docker compose down -v` (borra los datos del esquema
anterior) o cargarla a mano como en la opción B-bis.

## Opción B-bis — base nueva a mano

```bash
docker exec dash-parking-db createdb -U dash_parking dash_parking_v2
docker exec -i dash-parking-db psql -U dash_parking -d dash_parking_v2 < db/dash_parking_complete.sql
```

## Opción C — ya tienes cargado `dump-dash_parking-202609161534.sql`

Aplicar **en orden y una sola vez**:

```bash
docker exec -i dash-parking-db psql -U dash_parking -d <tu_base> -v ON_ERROR_STOP=1 < db/migrations/001_fix_missing_fields_and_integration.sql
docker exec -i dash-parking-db psql -U dash_parking -d <tu_base> -v ON_ERROR_STOP=1 < db/migrations/002_time_based_reservations.sql
```

## Pruebas

```bash
docker exec -i dash-parking-db psql -U dash_parking -d dash_parking_v2 < db/tests/time_based_reservations_test.sql
```

Esperado: 8 líneas `ERROR` (son los casos "FALLA esperada") y ningún cambio en los datos.

## Reglas de negocio de las reservas por tiempo

- Una reserva ocupa el espacio solo en `[fecha_reserva, fecha_hora_fin)`. Reservar 10:00–11:00 deja
  el espacio libre a las 9:00 y a las 11:00; 10:00–11:00 y 11:00–12:00 son compatibles.
- Dos reservas `activa` del mismo espacio no pueden cruzarse: lo garantiza la restricción
  `reserva_sin_traslape` (resiste concurrencia) y el trigger `trg_reserva_libre` da el mensaje claro.
- Una entrada sin reserva (`ticket`) no puede ocupar un espacio reservado por otro en ese momento.
- Todas las fechas son hora Colombia (`America/Bogota`, fijada con `ALTER DATABASE`).

## Funciones que consumirá el backend

| Función | Uso |
|---|---|
| `fn_estado_espacios(parqueadero, tipo_vehiculo, inicio, fin)` | Cuadrícula de espacios: `Disponible` / `Reservado` / `Ocupado` / `Mantenimiento` en esa franja |
| `fn_disponibilidad_franja(parqueadero, inicio, fin)` | Libres / reservados / ocupados por zona |
| `fn_crear_reserva(usuario, vehiculo, parqueadero, inicio, fin, [espacio])` | Crea la reserva; sin espacio asigna uno libre |
| `fn_tarifa_vigente(tipo_vehiculo, fecha, [parqueadero])` | Tarifa vigente por parqueadero |
| `fn_precio_estimado(parqueadero, tipo_vehiculo, inicio, fin)` | Precio de una franja antes de pagar (`NULL` si no hay tarifa) |
| `fn_monto_por_minutos(tarifa, minutos)` | Regla de cobro única (por minuto; desde 24 h, tarifa de día) |

Códigos de error (SQLSTATE) para mapear a HTTP: `23P01` espacio no disponible (409),
`P0002` sin espacios (409), `P0001` regla de negocio (400).

## Pendiente (no incluido en estas migraciones)

- `usuario.password_hash` queda en `NULL` para los usuarios del dump: se llena cuando existan el
  registro/login. No se sembraron contraseñas para no versionar credenciales.
- `estacionamiento.id_propietario` queda en `NULL` hasta que exista el usuario con rol `dueno`.
- El dump trae pagos de ejemplo que no cuadran con el trigger de cálculo (p. ej. pago 6: 12 h de
  carro a $25.000; el trigger daría $360.000). Hay que decidir si la tarifa por día funciona como
  tope diario; hoy solo se aplica desde 24 h.
- Los nombres de tablas y columnas están en español (decisión del equipo con la BD nueva), lo que
  se aparta de la regla "nomenclatura técnica en inglés" de `CODING_STANDARDS.md`: conviene
  dejarlo registrado como excepción.
