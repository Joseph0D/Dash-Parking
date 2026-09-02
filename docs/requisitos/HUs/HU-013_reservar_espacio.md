# HU-013 — Reservar un espacio de parqueo

<!--
  ¿Qué? Historia que permite a un cliente reservar un espacio eligiendo cuánto tiempo lo ocupará.
  ¿Para qué? Asegurar cupo antes de llegar físicamente al parqueadero.
  ¿Impacto? Sin reserva, el cliente puede llegar y encontrar el parqueadero lleno.
-->

## Identificación

| Campo | Valor |
|---|---|
| **ID** | HU-013 |
| **Módulo** | Reservas |
| **Prioridad** | Alta (Core — solicitado explícitamente por el cliente) |
| **Estado** | Implementado (este entregable) |
| **RF asociados** | RF-013 |

## Historia

**Como** cliente, **quiero** reservar un espacio disponible indicando el vehículo, la fecha/hora de llegada y el tiempo que voy a ocuparlo, **para** asegurar mi cupo antes de llegar.

## Criterios de aceptación

### CA-013.1 — Selección de vehículo y duración
Dado que tengo al menos un vehículo registrado, cuando creo una reserva, entonces debo indicar el vehículo, la fecha/hora de llegada y la duración estimada (en horas).

### CA-013.2 — Bloqueo del espacio en el rango reservado
Dado que existe una reserva confirmada para un espacio en un rango horario, cuando otro cliente intenta reservar ese mismo espacio en un rango que se solapa, entonces el sistema rechaza la reserva.

### CA-013.3 — Cancelación
Dado que tengo una reserva confirmada y aún no ha llegado la hora de inicio, cuando la cancelo, entonces el espacio vuelve a quedar disponible para ese rango.

### CA-013.4 — Conversión a sesión activa
Dado que llego dentro de la ventana de mi reserva y registro el ingreso con la misma placa, entonces el sistema asocia automáticamente la sesión de parqueo con la reserva (no se cobra la reserva dos veces).
