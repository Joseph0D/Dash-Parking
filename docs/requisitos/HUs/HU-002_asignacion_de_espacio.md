# HU-002 — Asignación automática de espacio

<!--
  ¿Qué? Historia de usuario que describe la asignación automática de un espacio disponible al vehículo que ingresa.
  ¿Para qué? Evitar que un operario asigne manualmente un espacio ya ocupado y garantizar control de disponibilidad.
  ¿Impacto? Sin esta regla, dos vehículos podrían quedar asociados al mismo espacio, rompiendo la trazabilidad de ocupación.
-->

---

## Identificación

| Campo            | Valor                          |
| ---------------- | ------------------------------- |
| **ID**           | HU-002                          |
| **Título**       | Asignación automática de espacio |
| **Módulo**       | Ingreso                         |
| **Prioridad**    | Alta (Core)                     |
| **Estado**       | En progreso (Sprint 0: regla de negocio implementada en memoria) |
| **RF asociados** | RF-002                          |

---

## Historia

**Como** sistema,
**quiero** asignar automáticamente un espacio disponible al vehículo que ingresa,
**para** evitar que un operario asigne manualmente un espacio que ya está ocupado.

---

## Criterios de aceptación

### CA-002.1 — Asignación automática al confirmar ingreso

- **Dado que** un operario confirma el registro de ingreso de un vehículo (HU-001),
- **cuando** hay al menos un espacio libre,
- **entonces** el sistema asigna automáticamente el primer espacio disponible, sin intervención manual del operario.

### CA-002.2 — Rechazo por falta de disponibilidad

- **Dado que** todos los espacios están ocupados,
- **cuando** se intenta registrar un nuevo ingreso,
- **entonces** el sistema rechaza el registro e informa que no hay espacios disponibles.

### CA-002.3 — Un espacio no puede tener dos vehículos

- **Dado que** un espacio ya está ocupado por un vehículo,
- **cuando** el sistema intenta asignarlo a otro vehículo,
- **entonces** la operación falla — esta es una regla de negocio no negociable del dominio.

### CA-002.4 — El espacio queda visible como ocupado

- **Dado que** un espacio fue asignado,
- **cuando** se consulta el estado del parqueadero (HU-003),
- **entonces** ese espacio aparece como ocupado, con la placa del vehículo que lo ocupa.

---

## Referencia de implementación (Sprint 0)

- Dominio: `app/models/vehicle.py` (`ParkingSpot.assign()` / `.release()`)
- Servicio: `app/services/parking_service.py` (`ParkingService._first_available_spot()`)
