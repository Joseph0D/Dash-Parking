# HU-004 — Registro de salida de vehículo

<!--
  ¿Qué? Historia de usuario que describe el registro de salida de un vehículo y la liberación de su espacio.
  ¿Para qué? Cerrar el ciclo de ocupación iniciado en el ingreso y habilitar el cálculo del cobro.
  ¿Impacto? Sin este registro, el espacio queda "ocupado" indefinidamente y el sistema pierde control real de disponibilidad.
-->

---

## Identificación

| Campo            | Valor                        |
| ---------------- | ------------------------------ |
| **ID**           | HU-004                         |
| **Título**       | Registro de salida de vehículo |
| **Módulo**       | Salida                         |
| **Prioridad**    | Alta (Core)                    |
| **Estado**       | Planificado (Sprint 3 — API CRUD) |
| **RF asociados** | RF-004                         |

---

## Historia

**Como** operario,
**quiero** registrar la salida de un vehículo buscándolo por placa,
**para** liberar el espacio que ocupaba y habilitar el cálculo del cobro correspondiente.

---

## Criterios de aceptación

### CA-004.1 — Búsqueda por placa para salida

- **Dado que** estoy en la pantalla de salida,
- **cuando** ingreso la placa de un vehículo que está dentro del parqueadero,
- **entonces** el sistema muestra sus datos de ingreso (hora, espacio asignado).

### CA-004.2 — Placa no encontrada

- **Dado que** ingreso una placa que no tiene un ingreso activo,
- **cuando** intento registrar la salida,
- **entonces** el sistema informa que no se encontró un vehículo dentro con esa placa.

### CA-004.3 — Registro de hora de salida

- **Dado que** confirmo la salida de un vehículo válido,
- **cuando** el sistema procesa la operación,
- **entonces** registra la hora de salida automáticamente y pasa el flujo al cálculo del cobro (HU-005).

### CA-004.4 — Liberación del espacio

- **Dado que** la salida se registró correctamente,
- **cuando** consulto el estado del parqueadero (HU-003),
- **entonces** el espacio que ocupaba ese vehículo aparece nuevamente como disponible.

### CA-004.5 — No se puede registrar salida duplicada

- **Dado que** un vehículo ya tiene salida registrada,
- **cuando** se intenta registrar su salida nuevamente,
- **entonces** el sistema rechaza la operación.
