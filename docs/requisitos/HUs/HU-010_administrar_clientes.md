# HU-010 — Administración de información de clientes

<!--
  ¿Qué? Historia de usuario que describe el registro y consulta de clientes frecuentes.
  ¿Para qué? Asociar vehículos a un cliente para dar mejor trazabilidad y atención.
  ¿Impacto? Sin este registro, no se puede identificar clientes recurrentes ni personalizar el servicio.
-->

---

## Identificación

| Campo            | Valor                                       |
| ---------------- | ---------------------------------------------|
| **ID**           | HU-010                                        |
| **Título**       | Administración de información de clientes     |
| **Módulo**       | Clientes                                      |
| **Prioridad**    | Media (Secundaria)                            |
| **Estado**       | Planificado (Sprint 6 — Flujos secundarios)   |
| **RF asociados** | RF-010                                        |

---

## Historia

**Como** administrador,
**quiero** registrar y consultar información de clientes frecuentes,
**para** asociarlos a sus vehículos y llevar un mejor control de la atención.

---

## Criterios de aceptación

### CA-010.1 — Registro de cliente

- **Dado que** un cliente es nuevo,
- **cuando** el administrador lo registra con nombre y datos de contacto,
- **entonces** el cliente queda disponible para asociarse a uno o más vehículos.

### CA-010.2 — Asociación cliente-vehículo

- **Dado que** un cliente está registrado,
- **cuando** se asocia una placa a ese cliente,
- **entonces** los ingresos posteriores de esa placa se vinculan automáticamente al cliente.

### CA-010.3 — Consulta de historial por cliente

- **Dado que** un cliente tiene vehículos asociados con historial,
- **cuando** el administrador consulta su ficha,
- **entonces** ve el historial de ingresos/salidas de todos sus vehículos.
