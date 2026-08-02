<!-- Basado en docs/estandar-codigo-template.md del bootcamp. Completado para el stack real
     de Dash Parking (FastAPI + React/TypeScript + PostgreSQL). -->

# CODING_STANDARDS — Dash Parking

## 1. Stack del Proyecto

| Capa | Tecnología elegida | Versión |
|---|---|---|
| Backend | FastAPI (Python) | Python 3.12 / FastAPI 0.115+ |
| Frontend | React + TypeScript (Vite) | React 18 / Vite 5 / TypeScript 5 |
| Base de datos | PostgreSQL | 16 |
| Contenedores | Docker + Docker Compose (obligatorio, sin alternativa) | — |
| Otros (colas, cache, etc.) | No aplica — sin alcance identificado en el informe de diseño | — |

---

## 2. Idioma

- Nomenclatura técnica (variables, funciones, clases, tablas, campos, ramas, commits): **inglés**
- Comentarios y documentación: **español**
- Ejemplo:

```python
# Calcula el valor a pagar según el tiempo de permanencia y la tarifa vigente
def calculate_parking_fee(entry_time: datetime, exit_time: datetime, rate: Decimal) -> Decimal:
    ...
```

---

## 3. Reglas de Nombrado

| Elemento | Convención | Ejemplo |
|---|---|---|
| Variables | `snake_case` (Python) / `camelCase` (TS) | `entry_time` / `entryTime` |
| Funciones / métodos | `snake_case` (Python) / `camelCase` (TS) | `register_entry()` / `registerEntry()` |
| Clases / componentes | `PascalCase` | `ParkingService`, `VehicleEntryForm` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_PARKING_CAPACITY` |
| Atributos privados | prefijo `_` | `_internal_cache` |
| Archivos de componente (frontend) | `PascalCase.tsx` | `VehicleEntryForm.tsx` |
| Archivos utilitarios | `camelCase.ts` / `snake_case.py` | `formatCurrency.ts` / `date_utils.py` |
| Tablas (BD) | `snake_case`, plural | `vehicles`, `parking_spots` |
| Campos (BD) | `snake_case` | `entry_time`, `is_occupied` |
| Llave primaria | `id` | `id` |
| Llave foránea | `<tabla_singular>_id` | `vehicle_id`, `parking_spot_id` |
| Ramas Git | `feature/kebab-case-slug` | `feature/vehicle-domain-model` |

---

## 4. Documentación de Código

- Toda función pública con lógica de negocio no trivial lleva un comentario que responda:
  **¿Qué hace? ¿Para qué existe? ¿Qué impacto tiene si falla?**
- No documentar lo obvio (`# incrementa i en 1` sobre `i += 1`)
- Cabecera de archivo cuando el archivo tiene más de una responsabilidad clara:

```python
"""
Módulo: parking_service.py
Qué: Lógica de negocio para el registro de ingreso/salida de vehículos.
Para qué: Centraliza las reglas de asignación de espacios y cálculo de cobro fuera de los endpoints.
Impacto: Si falla, un vehículo podría ocupar un espacio ya asignado o cobrarse un valor incorrecto.
"""
```

---

## 5. Indentación y Formato

| Stack | Indentación | Line length | Formatter |
|---|:---:|:---:|---|
| Python (backend) | 4 espacios | 100 | `ruff format` |
| TypeScript/React (frontend) | 2 espacios | 100 | `prettier` |

---

## 6. Estructura del Proyecto (API REST)

```
dash-parking/
├── be/                    # Backend (FastAPI)
│   └── app/
│       ├── models/        # Entidades de dominio (Sprint 0: sin ORM; ORM se agrega en Sprint 1)
│       ├── schemas/       # DTOs de entrada/salida (Pydantic)
│       ├── routers/       # Endpoints, agrupados por dominio
│       ├── services/      # Lógica de negocio (reglas del parqueadero)
│       └── utils/         # Utilidades transversales
├── fe/                    # Frontend (React + TS)
│   └── src/
│       ├── api/           # Llamadas a la API de Dash Parking
│       ├── components/    # UI reutilizable (formularios de ingreso/salida, tablero de ocupación)
│       ├── pages/         # Una página por ruta
│       └── hooks/         # Lógica reutilizable de estado/efectos
├── docs-proyecto/         # Documentación técnica del proyecto (backlog, decisiones)
└── docker-compose.yml     # Se agrega a partir del Sprint 1 (servicio db) — ver docs/docker-guia.md
```

---

## 7. Herramientas de Análisis Estático

- [x] Linter configurado: `ruff` (backend), `eslint` (frontend)
- [x] Formatter configurado: `ruff format` (backend), `prettier` (frontend)
- [ ] Corre en pre-commit — Pendiente, opcional para el equipo
- [x] Corre en CI (obligatorio) — ver `.github/workflows/ci.yml`

---

## 8. Checklist de Adopción (Semana 1)

- [x] Este documento está completado y commiteado como `CODING_STANDARDS.md` en la raíz del proyecto real
- [ ] Linter y formatter instalados y corriendo localmente — **acción del equipo**: cada
  integrante ejecuta `pip install -r be/requirements-dev.txt` y `npm install` en `fe/`
- [ ] El equipo verificó que el linter falla ante una violación intencional (prueba real) —
  **acción del equipo**: ver `GUIA-CONFIGURACION-GITHUB.md`, paso 7
