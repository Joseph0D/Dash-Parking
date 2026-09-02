# RF-004 — Registro de salida y liberación de espacio

<!--
  ¿Qué? Requisito funcional que define el registro de salida de un vehículo y la liberación de su espacio.
  ¿Para qué? Cerrar el ciclo de ocupación y habilitar el cálculo del cobro (RF-005).
  ¿Impacto? Sin este registro, el espacio queda ocupado indefinidamente aunque el vehículo ya se retiró.
-->

---

## Identificación

| Campo         | Valor                                     |
| ------------- | ---------------------------------------------|
| **ID**        | RF-004                                        |
| **Nombre**    | Registro de salida y liberación de espacio    |
| **Módulo**    | Salida                                        |
| **Prioridad** | Alta                                           |
| **Estado**    | Implementado |
| **Informe original** | RF07, RF10                              |

---

## Descripción

El sistema debe permitir buscar un vehículo por placa entre los que están dentro del parqueadero,
registrar su hora de salida y liberar automáticamente el espacio que ocupaba.

---

## Entradas

| Campo   | Tipo  | Obligatorio | Validaciones                             |
| ------- | ----- | ----------- | ------------------------------------------- |
| `plate` | Texto | Sí          | Debe corresponder a un vehículo con ingreso activo |

---

## Proceso

1. El operario busca el vehículo por placa.
2. El sistema valida que exista un ingreso activo para esa placa.
3. Se registra la hora de salida (UTC, automática).
4. Se dispara el cálculo del cobro (RF-005).
5. Se libera el espacio asociado (`ParkingSpot.release()`).

---

## Salidas

| Escenario                  | Código HTTP | Respuesta                                 |
| ----------------------------- | ----------- | -------------------------------------------- |
| Salida registrada             | 200         | Hora de salida, tiempo de permanencia, espacio liberado |
| Placa sin ingreso activo      | 404         | Mensaje: no se encontró el vehículo dentro del parqueadero |
| Salida ya registrada          | 409         | Mensaje: el vehículo ya tiene una salida registrada |

---

## Endpoints asociados

| Método | Ruta                              | Auth requerida | Descripción                    |
| ------ | ----------------------------------- | -------------- | --------------------------------- |
| POST   | `/api/v1/vehicles/{plate}/exit`    | Sí             | Registra la salida y libera el espacio |

---

## Reglas de negocio

- RN-007: La hora de salida nunca puede ser anterior a la hora de ingreso (regla ya validada en el dominio `Vehicle.register_exit()`).
- RN-008: La liberación del espacio es automática e inmediata al registrar la salida.
