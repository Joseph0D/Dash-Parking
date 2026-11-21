# Base de datos — Dash Parking

> **Estado de transición:** la base `dash_parking` (SQLAlchemy/UUID) es la fuente canónica para
> cuentas, el catálogo, la disponibilidad y las nuevas reservas. `dash_parking_v2` se conserva
> intacta como respaldo. No elimines ninguna de las dos bases.

## Archivos

| Archivo | Para qué |
|---|---|
| `migrations/000_uuid_initial_schema.sql` | Esquema inicial versionado para una base UUID nueva |
| `migrations/001_fix_missing_fields_and_integration.sql` | Campos vacíos/faltantes + roles, comprobante, pago de reservas |
| `migrations/002_time_based_reservations.sql` | Reservas por franja horaria (requiere la 001) |
| `migrations/003_bogota_parking_map.sql` | Ubicaciones demo de Bogotá, coordenadas y espacios/tarifas para disponibilidad |
| `migrations/004_uuid_parking_schema.sql` | Esquema de parqueaderos, roles, horarios, categorías y tarifas en la base UUID |
| `migrations/005_uuid_reservation_constraints.sql` | No-solapamiento por espacio y vehículo para reservas UUID |
| `migrations/006_password_reset.sql` | Tokens hasheados y registro de límites de recuperación de contraseña |
| `be/app/scripts/migrate_parking_catalog.py` | Simulación/importación idempotente del catálogo v2 a la base UUID |
| `tests/time_based_reservations_test.sql` | Pruebas (corren en una transacción y hacen `ROLLBACK`) |
| `tests/uuid_reservation_constraints_test.sql` | Prueba transaccional de las restricciones de reservas UUID |
| `dash_parking_complete.sql` | Estado final listo para una base nueva (dump original + 001 + 002) |

## Despliegue de demostración

La configuración preparada usa Vercel para el frontend, Render Free para la API y Neon Free
para PostgreSQL. Es una demo pública, no un servicio con disponibilidad garantizada: Render puede
dormir la API tras inactividad y Neon Free tiene límites y no ofrece SLA. Render Free bloquea SMTP
saliente, por lo que la recuperación de contraseña usa la API HTTPS de Brevo en ese entorno.
Neon incluye `btree_gist`, requerido por la migración 005.

El contenedor de producción ejecuta `python -m app.scripts.migrate_production` antes de iniciar
Uvicorn. El runner registra cada archivo en `dash_parking_schema_migrations`, toma un advisory lock
de PostgreSQL y aplica, en orden, `000`, `004`, `005` y `006`. Las migraciones `001`–`003` son de
la base legada `dash_parking_v2` y no se ejecutan contra la base UUID de producción. En una base
existente sin registro de migraciones, el runner detecta el esquema base y no vuelve a crear sus
tablas; un esquema parcial detiene el despliegue para evitar una inicialización ambigua.

`Base.metadata.create_all()` permanece únicamente para desarrollo y pruebas. El seed del
administrador y los datos de ejemplo está bloqueado cuando `APP_ENV=production`. Consulta
[`docs/despliegue-publico.md`](../docs/despliegue-publico.md) para crear servicios y configurar
variables sin incluir secretos en el repositorio.

## Opción A — con Docker Compose (automático)

`docker compose up` crea `dash_parking_v2` y carga `dash_parking_complete.sql` mediante
`db/init/01-create-parking-v2.sh`, que luego aplica `migrations/003_bogota_parking_map.sql`.
**Solo ocurre cuando el volumen está vacío.** Si ya tienes el
volumen de antes, tienes dos caminos: `docker compose down -v` (borra los datos del esquema
anterior) o cargarla a mano como en la opción B-bis.

Para una base ya creada, ejecutar la migración 003 (es repetible):

```bash
docker exec -i dash-parking-db psql -U dash_parking -d dash_parking_v2 -v ON_ERROR_STOP=1 < db/migrations/003_bogota_parking_map.sql
```

Los parqueaderos nuevos son ubicaciones ficticias para demostración; su disponibilidad sí se
consulta desde los espacios, reservas y tickets de esta base de datos.

## Migración del catálogo a la base UUID

La migración 004 es aditiva y repetible. Primero respalda ambas bases; por ejemplo, en PowerShell:

```powershell
docker exec dash-parking-db pg_dump -U dash_parking -Fc -f /tmp/dash_parking.dump dash_parking
docker cp dash-parking-db:/tmp/dash_parking.dump "$env:TEMP\dash_parking-backup.dump"
docker exec dash-parking-db pg_dump -U dash_parking -d dash_parking_v2 -Fc -f /tmp/dash_parking_v2.dump
docker cp dash-parking-db:/tmp/dash_parking_v2.dump "$env:TEMP\dash-parking-v2-backup.dump"
```

Aplica el esquema a `dash_parking` y simula la importación antes de confirmarla:

```powershell
docker exec dash-parking-db psql -U dash_parking -d dash_parking -v ON_ERROR_STOP=1 -f /db/004_uuid_parking_schema.sql
docker exec dash-parking-backend python -m app.scripts.migrate_parking_catalog
docker exec dash-parking-backend python -m app.scripts.migrate_parking_catalog --apply
```

La importación conserva los IDs numéricos de origen en columnas `legacy_id`, crea IDs UUID,
asocia espacios, zonas, categorías y tarifas, y no asigna dueño a registros cuyo usuario legado
no puede vincularse con una cuenta UUID. El catálogo de camiones queda disponible para nuevas
configuraciones. En el conjunto de demostración actual se esperan 4 parqueaderos, 5 categorías
heredadas, 6 tipos de espacio, 20 zonas, 689 espacios y 25 tarifas; el script informa los conteos
reales antes de importar.

Esta fase **no copia** usuarios, vehículos, reservas, tickets ni pagos de v2: sus identidades no
tienen una correspondencia segura con las cuentas UUID. La base v2 no se modifica y sigue siendo
el respaldo de las operaciones legadas. No hay un rollback destructivo: si la simulación reporta
conflictos, corrige el mapeo antes de `--apply`;
los datos de origen permanecen intactos.

La migración 005 agrega restricciones PostgreSQL de exclusión por espacio y vehículo sobre rangos
`[inicio, fin)`. Antes de aplicarla revisa y detiene la migración si encuentra reservas confirmadas
solapadas o rangos inválidos. Requiere permiso para instalar `btree_gist`:

```powershell
docker cp db\migrations\005_uuid_reservation_constraints.sql dash-parking-db:/tmp/005_uuid_reservation_constraints.sql
docker exec dash-parking-db psql -U dash_parking -d dash_parking -v ON_ERROR_STOP=1 -f /tmp/005_uuid_reservation_constraints.sql
docker cp db\tests\uuid_reservation_constraints_test.sql dash-parking-db:/tmp/uuid_reservation_constraints_test.sql
docker exec dash-parking-db psql -U dash_parking -d dash_parking -v ON_ERROR_STOP=1 -f /tmp/uuid_reservation_constraints_test.sql
```

La migración 006 agrega las tablas para tokens de recuperación de un solo uso y límites por correo
e IP. Los correos se envían por SMTP con configuración exclusivamente en `be/.env` (ver
`be/.env.example`); configura también `FRONTEND_BASE_URL` para que el enlace del correo apunte al
frontend correspondiente:

```powershell
docker cp db\migrations\006_password_reset.sql dash-parking-db:/tmp/006_password_reset.sql
docker exec dash-parking-db psql -U dash_parking -d dash_parking -v ON_ERROR_STOP=1 -f /tmp/006_password_reset.sql
```

Los tokens se guardan como SHA-256, vencen a los 30 minutos y las solicitudes excedentes reciben
la misma respuesta genérica que las solicitudes aceptadas (máximo 3 por correo y 10 por IP en una
hora). El proveedor se selecciona con `EMAIL_PROVIDER`: `smtp` para el entorno local y `brevo`
para despliegues gratuitos que bloquean SMTP saliente. Si el proveedor seleccionado no está
configurado, el endpoint responde `503` de forma consistente para todas las direcciones; no se
revela si una cuenta existe.

Los horarios semanales se interpretan con `day_of_week` de lunes (0) a domingo (6), en hora de
Bogotá. Para reservar se requiere una fila para cada día; un día cerrado debe registrarse
explícitamente. Los parqueaderos heredados sin horarios permiten consultar ocupación, pero no
aceptan reservas hasta que se configure el horario. Las franjas pueden exceder 24 horas.

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
