# Manual técnico — Dash Parking

Este manual describe la arquitectura que implementa actualmente el repositorio, cómo ejecutarla,
configurarla y verificarla. No contiene valores de secretos ni credenciales. Para la secuencia
detallada de publicación consulta también [despliegue público](./despliegue-publico.md).

## 1. Resumen del sistema

Dash Parking es una aplicación web con frontend de una sola página y API REST:

| Componente | Tecnología |
|---|---|
| Frontend | React 18, TypeScript, Vite, React Router |
| Mapas | Leaflet, React Leaflet y OpenStreetMap |
| Backend | Python 3.12, FastAPI, Pydantic 2 y SQLAlchemy 2 |
| Persistencia | PostgreSQL |
| Autenticación | JWT y contraseñas con hash bcrypt |
| Correo | SMTP para desarrollo o API HTTPS de Brevo |
| Ejecución local | Docker Compose |
| Despliegue preparado | Render para la API, Neon para PostgreSQL y Vercel para el frontend |

El backend expone documentación OpenAPI en `/docs` y `/openapi.json`. `/health` devuelve
`{"status":"ok"}` para comprobar que el proceso HTTP responde; no verifica por sí solo la conexión
a PostgreSQL, el correo ni la disponibilidad de los servicios externos.

## 2. Arquitectura y estructura

El backend separa las responsabilidades por capas:

- `be/app/routers/`: endpoints HTTP, autenticación/autorización y traducción de errores a códigos
  HTTP.
- `be/app/schemas/`: contratos de entrada y salida validados con Pydantic.
- `be/app/models/`: entidades SQLAlchemy.
- `be/app/services/`: reglas de negocio, consultas y transacciones.
- `be/app/core/`: configuración de seguridad y dependencias de autenticación/roles.
- `be/app/scripts/`: inicialización local, migración de catálogos y migraciones de producción.
- `db/migrations/`: SQL versionado para los esquemas PostgreSQL.
- `fe/src/api/`: cliente HTTP y tipos del frontend.
- `fe/src/context/`: sesiones y notificaciones globales.
- `fe/src/pages/` y `fe/src/components/`: pantallas y componentes React.

En una reserva UUID, el frontend consulta parqueaderos, tipos y espacios; el usuario elige un
vehículo y un horario; la API vuelve a validar los datos, bloquea el espacio durante la asignación
y persiste la reserva. La disponibilidad se calcula para el intervalo solicitado, no como una
ocupación permanente del espacio.

## 3. Rutas principales del frontend

| Ruta | Función |
|---|---|
| `/` | Inicio y mapa de parqueaderos |
| `/disponibilidad` | Consulta de disponibilidad y reservas |
| `/registro`, `/login` | Registro e inicio de sesión UUID |
| `/recuperar-contrasena`, `/restablecer-contrasena` | Recuperación de contraseña |
| `/cuenta` | Vehículos, sesiones y reservas del cliente |
| `/owner` | Panel protegido de dueño |
| `/dueno` | Redirección a `/owner` |
| `/admin` | Panel protegido de administrador u operario |

Las rutas privadas se protegen en el frontend con `ProtectedRoute`; la autorización definitiva
también debe validarse en el backend.

## 4. API

Prefijos funcionales registrados por `be/app/main.py`:

| Prefijo | Uso principal |
|---|---|
| `/api/v1/auth` | Registro, login, perfil y recuperación de contraseña UUID |
| `/api/v1/vehicles` | Vehículos del usuario y QR permanente por vehículo |
| `/api/v1/parking-lots` | Parqueaderos públicos, tipos de vehículo, disponibilidad y espacios |
| `/api/v1/owner` | Parqueaderos del dueño, horarios, inventario, tarifas y dashboard |
| `/api/v1/reservations` | Crear, listar las propias y cancelar reservas UUID |
| `/api/v1/sessions` | Ingresos, sesiones activas y consulta de sesiones |
| `/api/v1/payments` | Pagos simulados en efectivo/virtual y flujos QR |
| `/api/v1/rates`, `/api/v1/parking` | Tarifas y ocupación operativa |
| `/api/v1/reports` | Reportes administrativos |
| `/api/v1/accounts`, `/api/v1/reservas`, `/api/v1/tickets` | Compatibilidad con el sistema legado |

Los contratos completos deben consultarse en `/docs` para la versión que se esté ejecutando. Los
endpoints administrativos y de dueño requieren los roles correspondientes; los endpoints de
reservas UUID verifican que el usuario sea propietario del vehículo y que no exista solapamiento.

## 5. Identidad, autorización y datos heredados

El repositorio está en transición entre dos dominios de identidad y persistencia:

1. **Flujo UUID principal:** `/api/v1/auth`, `/api/v1/vehicles`,
   `/api/v1/reservations` y `/api/v1/owner` usan usuarios UUID y `DATABASE_URL`. Los roles de esta
   capa son `client`, `owner`, `operator` y `admin`.
2. **Flujo legado:** `/api/v1/accounts`, `/api/v1/reservas` y `/api/v1/tickets` usan cuentas con
   IDs numéricos, roles en español y `PARKING_DATABASE_URL`. Su JWT incluye un tipo de cuenta.

Los tokens de ambas capas no son intercambiables. `dash_parking` es la base UUID canónica para las
funciones nuevas; `dash_parking_v2` conserva el esquema legado. No se debe apuntar una capa a la
base de la otra ni asumir que los registros se sincronizan automáticamente.

El frontend ya dirige `/dueno` al panel UUID, pero el router legado sigue registrado. La variable
`PARKING_DATABASE_URL` no figura actualmente en `render.yaml`; por tanto, los endpoints heredados
que la necesitan no deben considerarse operativos en Render hasta configurarla de forma segura o
retirar/migrar esos endpoints.

## 6. Modelo de datos y reglas relevantes

En la base UUID, las relaciones principales son:

- Un usuario puede registrar vehículos.
- Un parqueadero tiene ubicación, horarios semanales, zonas, espacios y tarifas por categoría de
  vehículo.
- Una reserva referencia vehículo, parqueadero y espacio, además de inicio, fin y estado.
- Una sesión representa la permanencia efectiva de un vehículo; los pagos se vinculan a sesiones.
- Los tokens de recuperación se guardan como hash y los intentos se registran para limitar abuso.

Las franjas se comparan como intervalos semiabiertos `[inicio, fin)`: dos reservas contiguas son
compatibles, pero dos intervalos que se cruzan no pueden compartir espacio ni vehículo. La base
PostgreSQL refuerza esta regla con restricciones de exclusión; la aplicación convierte los
conflictos de concurrencia en HTTP `409`.

Los horarios de dueño usan días de semana de lunes `0` a domingo `6` y hora de Bogotá. Para
permitir reservas debe configurarse un horario para cada día, incluidos los días cerrados.

## 7. Configuración por entorno

Los archivos `.env.example`, `be/.env.example` y `fe/.env.example` contienen plantillas para
desarrollo. No guardar `.env` reales, cadenas de conexión ni secretos en Git, tickets o chats.

### Backend

| Variable | Propósito |
|---|---|
| `APP_ENV` | Distingue desarrollo de producción. |
| `DATABASE_URL` | PostgreSQL UUID principal; en producción debe usar TLS. |
| `PARKING_DATABASE_URL` | PostgreSQL legado requerido por `/api/v1/accounts` y `/api/v1/reservas`. |
| `JWT_SECRET` | Secreto de firma JWT; en producción requiere al menos 32 caracteres aleatorios. |
| `JWT_ALGORITHM` | Algoritmo JWT; el valor configurado por defecto es HS256. |
| `JWT_EXPIRE_MINUTES` | Duración del token; por defecto, ocho horas. |
| `CORS_ORIGINS` | Orígenes frontend permitidos, separados por coma y sin rutas. Producción exige HTTPS. |
| `FRONTEND_BASE_URL` | URL HTTPS usada para construir enlaces de recuperación. |
| `EMAIL_PROVIDER` | `smtp` o `brevo`; Render Free debe usar Brevo por HTTPS. |
| `EMAIL_TIMEOUT_SECONDS` | Timeout del proveedor de correo. |
| `BREVO_API_KEY` | Clave de API para el proveedor Brevo; solo en el gestor de secretos. |
| `EMAIL_FROM_EMAIL`, `EMAIL_FROM_NAME` | Remitente verificado y nombre del correo. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` | Parámetros SMTP cuando ese proveedor se use. |
| `SMTP_FROM_EMAIL`, `SMTP_USE_TLS`, `SMTP_USE_SSL` | Remitente y modo de conexión SMTP. |
| `MIGRATIONS_DIR` | Directorio de migraciones dentro de la imagen; definido por el Dockerfile. |
| `PORT` | Puerto asignado por la plataforma; Uvicorn lo consume al arrancar. |

No se deben configurar a la vez TLS y SSL SMTP. El programa valida en producción el formato seguro
de `DATABASE_URL`, el secreto JWT, las URL HTTPS de frontend/CORS y la configuración del proveedor
de correo.

### Frontend

| Variable | Propósito |
|---|---|
| `VITE_API_BASE_URL` | URL base HTTPS de la API. Vite la incorpora durante el build. |

No incluir secretos en variables `VITE_*`: quedan disponibles en el bundle público.

## 8. Ejecución local

Requisitos: Docker Desktop con Compose, o Python 3.12, Node.js/npm y PostgreSQL.

### Docker Compose (recomendado)

Desde la raíz del repositorio, en PowerShell:

```powershell
Copy-Item be\.env.example be\.env
Copy-Item fe\.env.example fe\.env
docker compose up --build
```

La aplicación queda disponible en `http://localhost:5173`, la API en
`http://localhost:8000` y OpenAPI en `http://localhost:8000/docs`. El Compose local inicia
PostgreSQL, ejecuta seeds de demostración y está destinado solo a desarrollo.

### Backend sin Docker

```powershell
Set-Location be
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m app.scripts.seed
uvicorn app.main:app --reload
```

Debe existir PostgreSQL y `DATABASE_URL` debe apuntar a la base local. En desarrollo, FastAPI crea
tablas mediante `Base.metadata.create_all`; producción no usa este mecanismo.

### Frontend sin Docker

```powershell
Set-Location fe
npm ci
npm run dev
```

Configurar `VITE_API_BASE_URL` para apuntar a la API local.

## 9. Migraciones y despliegue

El Dockerfile de producción ejecuta `python -m app.scripts.migrate_production` antes de Uvicorn.
El runner toma un advisory lock de PostgreSQL, registra las versiones aplicadas en
`dash_parking_schema_migrations` y aplica, en orden:

1. `000_uuid_initial_schema.sql`
2. `004_uuid_parking_schema.sql`
3. `005_uuid_reservation_constraints.sql`
4. `006_password_reset.sql`

Las migraciones `001`–`003` corresponden al esquema heredado y **no** se aplican contra la base
UUID de Render. El runner crea el esquema inicial solo cuando la base está vacía, reconoce un
esquema completo existente y detiene el arranque si detecta un esquema parcial. Antes de operar
sobre bases con datos, mantener un respaldo restaurable.

`render.yaml` describe una API Docker llamada `dash-parking-api`, plan Free, región Virginia,
health check `/health` y auto-deploy apagado. El contenedor de producción no ejecuta seeds. Para
el flujo de publicación, variables de Render y configuración de Vercel, sigue
[despliegue público](./despliegue-publico.md). La base UUID debe tener TLS habilitado y las
variables secretas se cargan directamente en la plataforma, nunca en el repositorio.

## 10. Correo y recuperación de contraseña

El proveedor se selecciona con `EMAIL_PROVIDER`. Brevo se invoca mediante HTTPS; SMTP se conserva
para entornos compatibles. El restablecimiento usa un token aleatorio de un solo uso, almacena su
SHA-256, expira a los 30 minutos y limita solicitudes por correo e IP. La respuesta del endpoint
no revela si una cuenta existe. Si falta la configuración requerida, el endpoint devuelve HTTP
`503`; si Brevo o SMTP falla durante el envío, el error se registra sin imprimir la clave.

## 11. Semillas y datos de demostración

Los datos de ejemplo pertenecen al desarrollo local. `docker-compose.yml` invoca los scripts de
seed para facilitar pruebas; `be/Dockerfile` no los ejecuta. Además, `seed.py` bloquea su uso
cuando `APP_ENV=production`. No usar las cuentas o datos de demostración como identidad real ni
habilitarlos en un servicio público.

## 12. Pruebas y calidad

Backend, desde `be/`:

```powershell
python -m pytest
python -m ruff check app tests
python -m ruff format --check app tests
```

La mayoría de las pruebas usa SQLite en memoria. La prueba PostgreSQL de concurrencia requiere
`RESERVATION_TEST_DATABASE_URL`; sin esa variable pytest la omite y no valida la restricción real
de PostgreSQL.

Frontend, desde `fe/`:

```powershell
npm test
npm run lint
npm run build
```

## 13. Límites operativos conocidos

- Los pagos virtuales y QR están simulados; no hay una pasarela bancaria real integrada.
- Render Free puede suspender el proceso tras inactividad y la primera petición puede tardar.
- `/health` verifica el proceso HTTP, no la base de datos, Brevo ni la pasarela de pago.
- Las capas UUID y heredada mantienen bases, formatos de ID y tokens distintos. Antes de retirar
  las rutas heredadas, migrar sus consumidores y confirmar que no existan integraciones externas.
- Para producción real se necesitan respaldo/retención, monitoreo y un plan de restauración probado;
  los planes gratuitos son adecuados para demostración, no ofrecen disponibilidad garantizada.
