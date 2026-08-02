# Plan de Trabajo — Dash Parking

## 1. Resumen del Informe de Diseño

- **Problema que resuelve el proyecto**: Dash Parking digitaliza la administración de un
  parqueadero que hoy opera de forma manual. El sistema debe controlar el ingreso y salida de
  vehículos, la ocupación de espacios, el cálculo automático del cobro por tiempo de permanencia,
  el registro de clientes y la generación de reportes administrativos, para reducir errores de
  cálculo/cobro, mejorar la trazabilidad y agilizar la atención.
- **Documentos de diseño disponibles**:
  - [x] Anteproyecto — parcial (problemática, objetivos, alcance funcional descritos; sin
    cronograma ni presupuesto formal)
  - [ ] Arquitectura técnica formal — **Pendiente de aclarar con instructor** (no hay diagrama de
    componentes/capas más allá de la lista de módulos funcionales)
  - [ ] Casos de uso (UML) — **Pendiente de aclarar con instructor** (no hay diagramas de casos de
    uso, solo actores y procesos principales descritos en prosa)
  - [ ] Historias de usuario formales — **Pendiente de aclarar con instructor** (no existían en
    formato `Como/quiero/para`; la Sección 3 de este documento las deriva de los Requisitos
    Funcionales RF01–RF20 y las Necesidades 1–7 del informe original, sin agregar alcance nuevo)
  - [x] Requisitos funcionales y no funcionales — completos (RF01–RF20 + RNF por atributo de calidad)
  - [x] Stakeholders y actores del sistema — completos

> Nota de trazabilidad: el informe de diseño original no traía historias de usuario ni modelo de
> datos. Las historias de la Sección 3 son una **traducción literal** de cada RF/Necesidad a
> formato ágil — no se inventó ningún alcance funcional adicional. Cualquier ambigüedad de
> arquitectura o modelo de datos se resolverá en el Sprint 1 (Semana 2 — Dominio y Persistencia).

## 2. Stack de Desarrollo

| Capa | Tecnología | Justificación breve |
|---|---|---|
| Backend | FastAPI (Python 3.12) | El informe de diseño exige una API que sirva múltiples procesos (ingreso, salida, tarifas, reportes) con validación fuerte de tipos de entrada (placa, tipo de vehículo, tarifa); FastAPI + Pydantic da esa validación de forma nativa y con bajo tiempo de arranque, clave dado el ritmo de Sprint 0 |
| Frontend | React + TypeScript (Vite) | Interfaz operativa (RNF de usabilidad: "interfaz intuitiva, operación sencilla") para operarios y administrador; componentes reutilizables para pantallas de ingreso/salida/reportes |
| Base de datos | PostgreSQL 16 | Relacional, encaja con las entidades fuertemente relacionadas del dominio (vehículo–espacio–tarifa–pago–cliente) y con la necesidad de integridad y trazabilidad (RNF de integridad y confiabilidad) |
| Contenedores | Docker + Docker Compose | Obligatorio del bootcamp, sin alternativa |
| Otros | — | No se identifican colas/cache en el alcance actual del informe de diseño |

## 3. Backlog Priorizado

| # | Historia de Usuario | Core / Secundaria | Depende de |
|---|---|:---:|---|
| 1 | Como operario, quiero registrar el ingreso de un vehículo (placa, tipo, fecha/hora automática) para dejar constancia digital del ingreso (RF01–RF04) | Core | — |
| 2 | Como sistema, quiero asignar automáticamente un espacio disponible al vehículo que ingresa para evitar asignación doble (RF05, Necesidad 2) | Core | #1 |
| 3 | Como administrador, quiero consultar los vehículos actualmente dentro del parqueadero para conocer la ocupación en tiempo real (RF06, RF20) | Core | #1, #2 |
| 4 | Como operario, quiero registrar la salida de un vehículo para liberar el espacio que ocupaba (RF07, RF10) | Core | #1, #2 |
| 5 | Como sistema, quiero calcular automáticamente el tiempo de permanencia y el valor a pagar al momento de la salida para evitar errores de cobro (RF08, RF09, Necesidad 3) | Core | #4 |
| 6 | Como operario, quiero registrar el pago realizado por el cliente para dejar trazabilidad del cobro (RF11) | Core | #5 |
| 7 | Como administrador, quiero definir y actualizar las tarifas del parqueadero para que el cálculo del cobro use valores vigentes (RF15, módulo de tarifas) | Core | — |
| 8 | Como administrador, quiero buscar vehículos por placa y consultar el historial de ingresos/salidas para resolver reclamos y auditar operación (RF12, RF13) | Secundaria | #1, #4 |
| 9 | Como propietario, quiero generar reportes de ingresos económicos, ocupación y vehículos atendidos para apoyar decisiones administrativas (RF14, Necesidad 5) | Secundaria | #6, #8 |
| 10 | Como administrador, quiero registrar y consultar información de clientes frecuentes para asociarlos a sus vehículos (RF16, módulo de clientes) | Secundaria | #1 |
| 11 | Como administrador, quiero actualizar o eliminar registros según permisos para corregir errores de digitación sin perder trazabilidad (RF17, RF18) | Secundaria | #1, #4 |
| 12 | Como usuario del sistema, quiero autenticarme con un rol (administrador/operario) para que el sistema controle permisos de acceso (RNF de seguridad) | Core | — |

<!-- Backlog completo cargado como Issues en GitHub Projects — ver docs-proyecto/backlog-historias-usuario.md -->

## 4. Progresión de Sprints Propuesta

| Sprint | Semana | Historias asignadas |
|---|:---:|---|
| 1 — Dominio y persistencia | 2 | Modelo de dominio de #1, #2, #4, #7 (Vehículo, Espacio, Tarifa) + esquema de datos y migraciones |
| 2 — Autenticación y autorización | 3 | #12 |
| 3 — API CRUD entidades core | 4 | #1, #2, #4, #7 (endpoints completos) |
| 4 — Reglas de negocio y servicios | 5 | #5, #6 (cálculo de permanencia y cobro) |
| 5 — Integración frontend-backend | 6 | Pantallas de ingreso/salida sobre #1–#6 |
| 6 — Flujos y funcionalidades secundarias | 7 | #8, #10, #11 |
| 7 — Pruebas y manejo de errores | 8 | Cobertura de pruebas de #1–#8, manejo de errores |
| 8 — Cierre y avance 90% | 9 | #9 (reportes), gate Docker end-to-end |

## 5. Sprint 0 — Qué se codificó esta semana

- **Rama feature usada**: `feature/vehicle-domain-model`
- **Qué se construyó**: entidades de dominio `Vehicle` y `ParkingSpot` (sin persistencia aún —
  eso es Sprint 1), servicio `ParkingService.register_entry()` que aplica la regla de negocio
  "no se puede asignar un espacio ya ocupado", y el endpoint mínimo `POST /api/v1/vehicles/entry`
  que expone esa acción. Incluye pruebas unitarias del dominio y del endpoint.
- **PR mergeado a develop**: Pendiente — se genera al hacer push del repositorio local a GitHub
  (ver `GUIA-CONFIGURACION-GITHUB.md`, paso 8). El merge `feature/vehicle-domain-model → develop`
  ya está hecho localmente con `--no-ff` y CI (`ci.yml`) corre en cada PR desde que se suba.
- **Commit(s) representativo(s)**:
  - `feat(vehicles): add Vehicle and ParkingSpot domain entities`
  - `feat(vehicles): add parking service to register vehicle entry`
  - `feat(vehicles): add POST /vehicles/entry endpoint`
  - `test(vehicles): add unit tests for domain model and entry endpoint`

## 6. Roles del Equipo (Sprint 0)

<!-- ✏️ Completar con los nombres reales del equipo (4+ integrantes según lo indicado) -->

| Integrante | Rol |
|---|---|
| _Pendiente de completar_ | Scrum Master |
| _Pendiente de completar_ | Product Owner |
| _Pendiente de completar_ | Dev (Backend) |
| _Pendiente de completar_ | Dev (Frontend) |
| _Pendiente de completar_ | QA |

> Roles recomendados para rotar en próximos sprints, según `docs/guia-github-projects.md`.
