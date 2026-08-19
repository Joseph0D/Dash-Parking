# HU-001 — Registro de ingreso de vehículo

<!--
  ¿Qué? Historia de usuario que describe el registro del ingreso de un vehículo al parqueadero.
  ¿Para qué? Formalizar la necesidad de dejar constancia digital de cada ingreso, reemplazando el registro manual.
  ¿Impacto? Es la puerta de entrada del flujo operativo — sin este registro no hay ocupación, cobro ni trazabilidad.
-->

---

## Identificación

| Campo            | Valor                     |
| ---------------- | -------------------------- |
| **ID**           | HU-001                     |
| **Título**       | Registro de ingreso de vehículo |
| **Módulo**       | Ingreso                    |
| **Prioridad**    | Alta (Core)                |
| **Estado**       | Implementado |
| **RF asociados** | RF-001                     |

---

## Historia

**Como** operario,
**quiero** registrar el ingreso de un vehículo indicando su placa y tipo,
**para** dejar constancia digital del ingreso y habilitar el control de ocupación.

---

## Criterios de aceptación

### CA-001.1 — Registro con datos mínimos

- **Dado que** estoy en la pantalla de registro de ingreso,
- **cuando** ingreso la placa y selecciono el tipo de vehículo (carro, moto, camión) y confirmo,
- **entonces** el sistema registra el ingreso con fecha y hora actuales de forma automática, sin que yo deba digitarlas.

### CA-001.2 — Validación de placa obligatoria

- **Dado que** estoy completando el formulario de ingreso,
- **cuando** dejo el campo de placa vacío e intento confirmar,
- **entonces** debo ver un mensaje de error indicando que la placa es obligatoria.

### CA-001.3 — Normalización de placa

- **Dado que** ingreso una placa con espacios o en minúsculas (ej. `abc 123`),
- **cuando** el sistema la procesa,
- **entonces** se almacena normalizada (mayúsculas, sin espacios: `ABC123`), para evitar duplicados por formato.

### CA-001.4 — Rechazo de placa ya registrada dentro

- **Dado que** una placa ya tiene un ingreso activo (sin salida registrada),
- **cuando** intento registrar un nuevo ingreso con la misma placa,
- **entonces** el sistema rechaza la operación e indica que ese vehículo ya está dentro del parqueadero.

### CA-001.5 — Confirmación del ingreso

- **Dado que** el ingreso se registró correctamente,
- **cuando** el sistema responde,
- **entonces** debo ver la placa, el tipo de vehículo, la hora de ingreso y el espacio asignado (ver HU-002).

---

## Referencia de implementación (Sprint 0)

- Endpoint: `POST /api/v1/vehicles/entry`
- Dominio: `app/models/vehicle.py` (`Vehicle`), `app/services/parking_service.py`
- La persistencia real en PostgreSQL se agrega en el Sprint 1 (ver `entregable-s01-plan-de-trabajo.md`).
