# HU-008 — Búsqueda de vehículos y consulta de historial

<!--
  ¿Qué? Historia de usuario que describe la búsqueda de vehículos por placa y la consulta de su historial.
  ¿Para qué? Permitir auditoría y resolución de reclamos sobre ingresos, salidas y pagos pasados.
  ¿Impacto? Sin esta consulta, no hay forma de verificar información histórica ante un reclamo o auditoría.
-->

---

## Identificación

| Campo            | Valor                                        |
| ---------------- | ----------------------------------------------|
| **ID**           | HU-008                                         |
| **Título**       | Búsqueda de vehículos y consulta de historial  |
| **Módulo**       | Administrativo                                 |
| **Prioridad**    | Media (Secundaria)                             |
| **Estado**       | Planificado (Sprint 6 — Flujos secundarios)    |
| **RF asociados** | RF-008                                         |

---

## Historia

**Como** administrador,
**quiero** buscar vehículos por placa y consultar su historial de ingresos, salidas y pagos,
**para** resolver reclamos y auditar la operación del parqueadero.

---

## Criterios de aceptación

### CA-008.1 — Búsqueda exacta y parcial por placa

- **Dado que** ingreso una placa completa o parcial en el buscador,
- **cuando** ejecuto la búsqueda,
- **entonces** el sistema muestra todos los vehículos cuya placa coincide.

### CA-008.2 — Historial cronológico

- **Dado que** selecciono un vehículo desde el resultado de búsqueda,
- **cuando** consulto su historial,
- **entonces** veo sus ingresos, salidas y pagos asociados, ordenados por fecha descendente.

### CA-008.3 — Búsqueda sin resultados

- **Dado que** ninguna placa registrada coincide con el criterio de búsqueda,
- **cuando** ejecuto la búsqueda,
- **entonces** el sistema muestra un mensaje indicando que no se encontraron resultados.
