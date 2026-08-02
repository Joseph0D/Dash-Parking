# Dash Parking

Sistema de gestión integral de un parqueadero: control de ingreso/salida de vehículos, ocupación
de espacios en tiempo real, cálculo automático del cobro, administración de tarifas y clientes, y
reportes administrativos.

Proyecto real del bootcamp de Asesoría Desarrollo — Codificación. Semana 1: Alistamiento
Acelerado y Arranque de Código.

## Estado

🚧 Sprint 0 — dominio inicial (registro de ingreso de vehículo) construido y probado. Ver
[`entregable-s01-plan-de-trabajo.md`](entregable-s01-plan-de-trabajo.md) para el backlog completo
y la progresión de sprints.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python 3.12) |
| Frontend | React + TypeScript (Vite) |
| Base de datos | PostgreSQL 16 (se conecta desde el Sprint 1) |
| Contenedores | Docker + Docker Compose |

Ver detalle y justificación en [`CODING_STANDARDS.md`](CODING_STANDARDS.md).

## Estructura

```
dash-parking/
├── be/                     # Backend FastAPI
├── fe/                     # Frontend React + TypeScript
├── docs-proyecto/          # Backlog e historias de usuario
├── entregable-s01-plan-de-trabajo.md
├── CODING_STANDARDS.md
└── GUIA-CONFIGURACION-GITHUB.md
```

## Cómo correr el backend localmente

```bash
cd be
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000` — documentación interactiva en
`http://localhost:8000/docs`.

Correr las pruebas:

```bash
cd be
pytest
```

Correr el linter:

```bash
cd be
ruff check .
ruff format --check .
```

## Cómo correr el frontend localmente

```bash
cd fe
npm install
npm run dev
```

App disponible en `http://localhost:5173`.

```bash
npm run lint
npm test
npm run build
```

## Backlog y GitHub Projects

El backlog priorizado vive en [`entregable-s01-plan-de-trabajo.md`](entregable-s01-plan-de-trabajo.md)
(Sección 3) y en detalle, listo para copiar como Issues, en
[`docs-proyecto/backlog-historias-usuario.md`](docs-proyecto/backlog-historias-usuario.md).

Pasos de configuración de GitHub (repo, Project, branch protection, CI) en
[`GUIA-CONFIGURACION-GITHUB.md`](GUIA-CONFIGURACION-GITHUB.md).

## Flujo de trabajo

`feature/<slug> → develop → main`, con Conventional Commits. Ver
[`GUIA-CONFIGURACION-GITHUB.md`](GUIA-CONFIGURACION-GITHUB.md) para la configuración de branch
protection y CI.
