# RF-005 — Cálculo de tiempo de permanencia y valor a pagar

<!--
  ¿Qué? Requisito funcional que define el cálculo automático del cobro al momento de la salida.
  ¿Para qué? Eliminar el error humano de cálculo, principal problema identificado en el diagnóstico del parqueadero.
  ¿Impacto? Un error de cálculo se traduce directamente en pérdida económica o cobro incorrecto.
-->

---

## Identificación

| Campo         | Valor                                            |
| ------------- | ----------------------------------------------------|
| **ID**        | RF-005                                                |
| **Nombre**    | Cálculo de tiempo de permanencia y valor a pagar      |
| **Módulo**    | Salida                                                |
| **Prioridad** | Alta                                                   |
| **Estado**    | Implementado |
| **Informe original** | RF08, RF09                                      |

---

## Descripción

Al registrarse la salida (RF-004), el sistema debe calcular el tiempo de permanencia (diferencia
entre hora de salida y hora de ingreso) y el valor a pagar, aplicando la tarifa vigente para el
tipo de vehículo (RF-007).

---

## Entradas

| Campo         | Tipo     | Obligatorio | Validaciones                        |
| ------------- | -------- | ----------- | -------------------------------------- |
| `entry_time`  | Fecha/hora | Sí        | Debe existir (viene del registro de ingreso) |
| `exit_time`   | Fecha/hora | Sí        | Debe ser posterior a `entry_time`      |
| Tarifa vigente | Decimal | Sí          | Debe existir una tarifa activa para el tipo de vehículo |

---

## Proceso

1. Se obtiene `entry_time` y `exit_time` del vehículo.
2. Se calcula el tiempo de permanencia.
3. Se obtiene la tarifa vigente para el tipo de vehículo (RF-007).
4. Se calcula el valor a pagar = tiempo de permanencia × tarifa.
5. Se retorna el resultado antes de confirmar el pago (RF-006).

---

## Salidas

| Escenario                       | Código HTTP | Respuesta                                |
| ----------------------------------- | ----------- | -------------------------------------------- |
| Cálculo exitoso                     | 200         | Tiempo de permanencia y valor a pagar         |
| Sin tarifa configurada              | 422         | Mensaje: debe configurarse una tarifa antes de continuar |

---

## Endpoints asociados

El cálculo se ejecuta como parte de `POST /api/v1/vehicles/{plate}/exit` (RF-004), antes de confirmar el pago.

---

## Reglas de negocio

- RN-009: El valor a pagar siempre usa la tarifa vigente al momento de la salida, no la vigente al momento del ingreso.
- RN-010: El cálculo nunca se redondea a favor ni en contra sin una regla explícita definida por el negocio (pendiente de definir unidad de cobro: por hora, fracción, etc. — **Pendiente de aclarar con el propietario del parqueadero**).
