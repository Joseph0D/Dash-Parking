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

**Con Docker (recomendado)** — un solo comando levanta base de datos, backend y frontend:

```bash
cp be/.env.example be/.env
cp fe/.env.example fe/.env
docker compose up --build
```

**Sin Docker** (backend):

```bash
cd be
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.scripts.seed   # crea admin, tarifas y espacios de ejemplo
uvicorn app.main:app --reload
```

Requiere una instancia de PostgreSQL propia — configura `DATABASE_URL` en `be/.env`.
API en `http://localhost:8000`, documentación interactiva en `http://localhost:8000/docs`.

```bash
pytest              # tests (usan SQLite en memoria, no requieren PostgreSQL)
ruff check .         # linter
ruff format --check .
```

**Sin Docker** (frontend):

```bash
cd fe
npm install
npm run dev
```

App en `http://localhost:5173`.

```bash
npm run lint
npm test
npm run build
```

