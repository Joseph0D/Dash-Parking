# HU-006 — Registro del pago del servicio

<!--
  ¿Qué? Historia de usuario que describe el registro del pago realizado por el cliente.
  ¿Para qué? Dejar trazabilidad económica de cada cobro efectuado.
  ¿Impacto? Sin este registro no hay forma de auditar los ingresos reales del parqueadero.
-->

---

## Identificación

| Campo            | Valor                            |
| ---------------- | ----------------------------------|
| **ID**           | HU-006                            |
| **Título**       | Registro del pago del servicio    |
| **Módulo**       | Salida                            |
| **Prioridad**    | Alta (Core)                       |
| **Estado**       | Planificado (Sprint 4 — Reglas de negocio) |
| **RF asociados** | RF-006                            |

---

## Historia

**Como** operario,
**quiero** registrar el pago realizado por el cliente al momento de la salida,
**para** dejar trazabilidad del cobro y cerrar el ciclo del vehículo en el sistema.

---

## Criterios de aceptación

### CA-006.1 — Registro del valor pagado

- **Dado que** el sistema calculó el valor a pagar (HU-005),
- **cuando** el operario confirma el pago,
- **entonces** se registra el valor pagado asociado a esa salida.

### CA-006.2 — Vínculo con el registro de salida

- **Dado que** un pago fue registrado,
- **cuando** se consulta el historial de ese vehículo (HU-008),
- **entonces** el pago aparece asociado al ingreso y salida correspondientes.

### CA-006.3 — Salida no se completa sin pago

- **Dado que** el operario intenta cerrar la salida sin confirmar el pago,
- **cuando** el sistema valida la operación,
- **entonces** la salida no queda marcada como completada hasta que el pago se registre.
