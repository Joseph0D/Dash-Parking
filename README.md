# Dash Parking

Sistema de gestión integral de un parqueadero: reserva de espacios, control de ingreso/salida de
vehículos, ocupación en tiempo real, cálculo automático del cobro, pago virtual y por QR,
administración de tarifas y clientes, y un dashboard administrativo filtrable.

Proyecto real del bootcamp de Asesoría Desarrollo — Codificación.

## Estado

✅ **Versión funcional de punta a punta** — backend real sobre PostgreSQL, frontend React
conectado, y los 17 requisitos funcionales documentados en `docs/requisitos/` implementados
(RF-001 a RF-017: desde el ingreso de un vehículo hasta reservas, pagos virtual/QR y el
dashboard filtrable).
## Funcionalidades

**Cliente**
- Crear cuenta y vehículos propios (RF-016, RF-001)
- Reservar un espacio eligiendo vehículo, fecha/hora de llegada y tiempo de ocupación (RF-013)
- Ver su sesión activa con tiempo transcurrido y valor a pagar en vivo (RF-005)
- Pagar virtual (RF-014) o generar un código QR para pagar/validar en la talanquera (RF-015)

**Administrador / Operario**
- Ver ocupación en tiempo real y vehículos actualmente dentro (RF-003)
- Registrar ingreso y salida con cobro en efectivo (RF-001, RF-004, RF-006)
- Validar el QR de un cliente y cobrar (RF-015)
- Administrar tarifas por tipo de vehículo (RF-007)
- Dashboard con ganancia total, filtrable por tipo de vehículo y por rango de fechas (RF-017)

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python 3.12) + SQLAlchemy + JWT/bcrypt |
| Frontend | React + TypeScript (Vite) + React Router |
| Base de datos | PostgreSQL 16 |
| Contenedores | Docker + Docker Compose |

Ver detalle y justificación en [`CODING_STANDARDS.md`](CODING_STANDARDS.md).

## Documentación técnica

- [Manual técnico (PDF)](docs/manual-tecnico.pdf)
- [Manual técnico editable (Markdown)](docs/manual-tecnico.md)
- [Guía de despliegue público](docs/despliegue-publico.md)
- [Historias de usuario y requisitos](docs/requisitos/README.md)

> **Nota sobre los pagos**: "pago virtual" y "pago QR" están implementados end-to-end (generan
> referencias y códigos QR reales), pero la pasarela de pago está **simulada** — no hay
> credenciales de una pasarela real (Wompi/PSE/Nequi) en este entorno académico. El punto de
> integración queda documentado y aislado en `be/app/services/payment_service.py` para conectar
> una pasarela real sin cambiar el resto del sistema. Ver `docs/requisitos/RFs/RF-014_pago_virtual.md`.

## Estructura

```
dash-parking/
├── be/                          # Backend FastAPI
│   └── app/
│       ├── models/              # Entidades ORM (User, Vehicle, ParkingSpot, Rate, ...)
│       ├── schemas/             # DTOs Pydantic
│       ├── routers/             # Endpoints por dominio
│       ├── services/            # Lógica de negocio (cobro, reservas, QR, pagos, reportes)
│       ├── core/                # Seguridad (JWT/bcrypt) y dependencias de autorización
│       └── scripts/seed.py      # Datos iniciales (admin, tarifas, espacios)
├── fe/                          # Frontend React + TypeScript
│   └── src/
│       ├── api/                 # Cliente HTTP tipado, un módulo por dominio
│       ├── components/          # UI reutilizable (Button, Card, Badge, Toast, Navbar)
│       ├── context/              # Sesión global (AuthContext) y notificaciones (ToastContext)
│       └── pages/                 # client/ (panel de cliente) y admin/ (panel de administración)
├── docs/
│   └── requisitos/               # HUs, RFs, RNFs y restricciones (trazables al informe de diseño)
├── docker-compose.yml
├── CODING_STANDARDS.md
```

## Cómo correr el proyecto

Los archivos `.env` no se guardan en Git porque pueden contener secretos. Después de clonar el
repositorio, hay que crearlos desde las plantillas. Para que el mapa, la disponibilidad y las
reservas funcionen localmente, deben estar activos PostgreSQL, el backend y el frontend; ejecutar
solo Vite (`npm run dev`) no inicia la API y produce `Failed to fetch`.

**Windows (PowerShell) — recomendado con Docker Desktop**

Desde la carpeta raíz del repositorio:

```powershell
if (-not (Test-Path be\.env)) { Copy-Item be\.env.example be\.env }
if (-not (Test-Path fe\.env)) { Copy-Item fe\.env.example fe\.env }
docker compose up --build
```

Cuando los servicios estén listos, abre `http://localhost:5173`; la API responde en
`http://localhost:8000` y su documentación en `http://localhost:8000/docs`. Mantén Docker Desktop
y Compose ejecutándose mientras uses la aplicación. Para detenerlos, pulsa `Ctrl+C` en esa
terminal.

**Linux/macOS:** desde la raíz, ejecuta `cp be/.env.example be/.env` y
`cp fe/.env.example fe/.env`; luego `docker compose up --build`.

**Sin Docker:** inicia PostgreSQL, configura `DATABASE_URL` en `be/.env`, inicia el backend en una
terminal y el frontend en otra. La dirección predeterminada de desarrollo para la API es
`http://localhost:8000`; cambia `VITE_API_BASE_URL` en `fe/.env` solo si el backend escucha en otra
dirección.

Si aparece `Failed to fetch` y la consola muestra `ERR_CONNECTION_REFUSED` en el puerto `8000`,
comprueba que el backend esté ejecutándose y que `http://localhost:8000/health` responda.

Backend, desde `be/`:

```bash
cd be
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.scripts.seed   # crea admin, tarifas y espacios de ejemplo
uvicorn app.main:app --reload
```

Requiere una instancia de PostgreSQL propia y las bases de datos configuradas en `be/.env`.

```bash
pytest              # tests (usan SQLite en memoria, no requieren PostgreSQL)
ruff check .         # linter
ruff format --check .
```

Frontend, en otra terminal desde `fe/`:

```bash
cd fe
npm ci
npm run dev
```

App en `http://localhost:5173`.

```bash
npm run lint
npm test
npm run build
```

