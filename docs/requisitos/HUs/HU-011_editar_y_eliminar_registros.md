# HU-011 — Actualización y eliminación de registros según permisos

<!--
  ¿Qué? Historia de usuario que describe la corrección/eliminación de registros por parte del administrador.
  ¿Para qué? Permitir corregir errores de digitación sin perder trazabilidad de la operación.
  ¿Impacto? Sin control de esta operación, cualquier usuario podría alterar el historial y romper la trazabilidad exigida.
-->

---

## Identificación

| Campo            | Valor                                                  |
| ---------------- | -------------------------------------------------------- |
| **ID**           | HU-011                                                    |
| **Título**       | Actualización y eliminación de registros según permisos   |
| **Módulo**       | Administrativo                                            |
| **Prioridad**    | Media (Secundaria)                                        |
| **Estado**       | Planificado (Sprint 6 — Flujos secundarios)                |
| **RF asociados** | RF-011                                                     |

---

## Historia

**Como** administrador,
**quiero** actualizar o eliminar registros de ingreso/salida según permisos,
**para** corregir errores de digitación sin perder trazabilidad del historial.

---

## Criterios de aceptación

### CA-011.1 — Solo administrador puede eliminar

- **Dado que** un usuario con rol operario intenta eliminar un registro,
- **cuando** envía la solicitud,
- **entonces** el sistema la rechaza por falta de permisos.

### CA-011.2 — Toda edición queda auditada

- **Dado que** un administrador edita un registro,
- **cuando** la edición se guarda,
- **entonces** el sistema registra quién hizo el cambio, cuándo y qué campo se modificó.

### CA-011.3 — Confirmación antes de eliminar registro con pago

- **Dado que** un registro tiene un pago asociado,
- **cuando** el administrador intenta eliminarlo,
- **entonces** el sistema exige una confirmación explícita antes de proceder.
