# RNF-005 — Mantenibilidad y escalabilidad

<!--
  ¿Qué? Requisito no funcional que define los estándares de mantenibilidad y crecimiento del sistema.
  ¿Para qué? Permitir que el proyecto evolucione sprint a sprint sin degradar su calidad.
  ¿Impacto? Sin esto, cada nueva funcionalidad se vuelve más costosa y riesgosa de agregar.
-->

---

## Identificación

| Campo         | Valor                            |
| ------------- | -------------------------------------|
| **ID**        | RNF-005                               |
| **Nombre**    | Mantenibilidad y escalabilidad         |
| **Categoría** | Calidad de código                        |
| **Prioridad** | Media                                     |
| **Estado**    | Implementado desde Sprint 0 (estándares) — evaluado continuamente |

---

## Requisitos

### RNF-005.1 — Código modular
El backend sigue la estructura `models/ schemas/ routers/ services/ utils/`; el frontend sigue
`api/ components/ pages/ hooks/`, según `CODING_STANDARDS.md`.

### RNF-005.2 — Documentación de código
Toda función con lógica de negocio no trivial documenta qué hace, para qué existe y qué impacto
tiene si falla (ver `CODING_STANDARDS.md`, sección 4).

### RNF-005.3 — Análisis estático obligatorio en CI
Todo Pull Request corre `ruff` (backend) y `eslint` (frontend) automáticamente — ver
`.github/workflows/ci.yml`.

### RNF-005.4 — Soporte para crecimiento de registros
El diseño de datos debe soportar un volumen creciente de historial sin degradar las consultas
(ver RNF-002.2 sobre índices).

### RNF-005.5 — Posibilidad de agregar nuevos módulos
La arquitectura por capas (routers/services/models) permite agregar nuevos módulos (ej. reservas,
membresías) sin reescribir los existentes.
