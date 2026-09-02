# HU-005 — Cálculo de tiempo de permanencia y valor a pagar

<!--
  ¿Qué? Historia de usuario que describe el cálculo automático del cobro al momento de la salida.
  ¿Para qué? Eliminar errores humanos de cálculo de tiempo y tarifa, principal problema identificado en el diagnóstico.
  ¿Impacto? Un error aquí se traduce directamente en pérdida económica o en cobro incorrecto al cliente.
-->

---

## Identificación

| Campo            | Valor                                            |
| ---------------- | -------------------------------------------------- |
| **ID**           | HU-005                                             |
| **Título**       | Cálculo de tiempo de permanencia y valor a pagar   |
| **Módulo**       | Salida                                             |
| **Prioridad**    | Alta (Core)                                        |
| **Estado**       | Implementado |
| **RF asociados** | RF-005                                             |

---

## Historia

**Como** sistema,
**quiero** calcular automáticamente el tiempo de permanencia y el valor a pagar al momento de la salida,
**para** evitar errores de cálculo y liquidación manual del cobro.

---

## Criterios de aceptación

### CA-005.1 — Cálculo del tiempo de permanencia

- **Dado que** un vehículo tiene hora de ingreso y hora de salida registradas,
- **cuando** el sistema calcula el tiempo de permanencia,
- **entonces** el resultado es la diferencia exacta entre ambas marcas de tiempo.

### CA-005.2 — Aplicación de la tarifa vigente

- **Dado que** existe una tarifa activa para el tipo de vehículo,
- **cuando** se calcula el valor a pagar,
- **entonces** el sistema aplica la tarifa vigente al tiempo de permanencia calculado (ver HU-007).

### CA-005.3 — Visualización previa a la confirmación

- **Dado que** el operario está cerrando el proceso de salida,
- **cuando** el sistema termina el cálculo,
- **entonces** se muestra el tiempo de permanencia y el valor a pagar antes de confirmar la salida definitiva.

### CA-005.4 — Sin tarifa configurada

- **Dado que** no existe una tarifa vigente para el tipo de vehículo,
- **cuando** el sistema intenta calcular el cobro,
- **entonces** bloquea la operación e informa que debe configurarse una tarifa antes de continuar.
