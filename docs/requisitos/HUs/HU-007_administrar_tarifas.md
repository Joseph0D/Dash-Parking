# HU-007 — Administración de tarifas

<!--
  ¿Qué? Historia de usuario que describe la creación y actualización de tarifas del parqueadero.
  ¿Para qué? Permitir que el cálculo del cobro (HU-005) siempre use un valor vigente y correcto.
  ¿Impacto? Sin tarifas administrables, el cálculo de cobro no tiene fuente de verdad y el sistema no podría operar.
-->

---

## Identificación

| Campo            | Valor                          |
| ---------------- | -------------------------------- |
| **ID**           | HU-007                           |
| **Título**       | Administración de tarifas        |
| **Módulo**       | Tarifas                          |
| **Prioridad**    | Alta (Core)                      |
| **Estado**       | Planificado (Sprint 1 — Dominio y persistencia) |
| **RF asociados** | RF-007                           |

---

## Historia

**Como** administrador,
**quiero** definir y actualizar las tarifas del parqueadero por tipo de vehículo,
**para** que el sistema use siempre un valor vigente al calcular el cobro.

---

## Criterios de aceptación

### CA-007.1 — Creación de tarifa

- **Dado que** no existe una tarifa para un tipo de vehículo,
- **cuando** el administrador crea una tarifa (valor por unidad de tiempo),
- **entonces** queda disponible para ser usada en el cálculo del cobro.

### CA-007.2 — Actualización de tarifa

- **Dado que** existe una tarifa activa,
- **cuando** el administrador la actualiza,
- **entonces** los cálculos posteriores usan el nuevo valor, sin afectar cobros ya liquidados anteriormente.

### CA-007.3 — Solo el administrador puede modificar tarifas

- **Dado que** un usuario con rol operario intenta modificar una tarifa,
- **cuando** envía la solicitud,
- **entonces** el sistema la rechaza por falta de permisos (ver HU-012).

### CA-007.4 — Validación de valor de tarifa

- **Dado que** se intenta crear o actualizar una tarifa con un valor negativo o igual a cero,
- **cuando** se envía la solicitud,
- **entonces** el sistema la rechaza con un mensaje de validación.
