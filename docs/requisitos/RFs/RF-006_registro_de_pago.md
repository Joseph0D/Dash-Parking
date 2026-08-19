# RF-006 — Registro del pago del servicio

<!--
  ¿Qué? Requisito funcional que define el registro del pago realizado por el cliente.
  ¿Para qué? Dejar trazabilidad económica de cada cobro efectuado y cerrar el ciclo del vehículo.
  ¿Impacto? Sin este registro no hay forma de auditar los ingresos reales del negocio.
-->

---

## Identificación

| Campo         | Valor                        |
| ------------- | --------------------------------|
| **ID**        | RF-006                           |
| **Nombre**    | Registro del pago del servicio   |
| **Módulo**    | Salida                           |
| **Prioridad** | Alta                              |
| **Estado**    | Implementado |
| **Informe original** | RF11                        |

---

## Descripción

El sistema debe registrar el pago efectuado por el cliente, asociado al registro de salida
correspondiente, y bloquear el cierre de la salida hasta que el pago se confirme.

---

## Entradas

| Campo    | Tipo    | Obligatorio | Validaciones                          |
| -------- | ------- | ----------- | ---------------------------------------- |
| `amount` | Decimal | Sí          | Debe coincidir con el valor calculado (RF-005) |
| `plate`  | Texto   | Sí          | Debe corresponder a una salida en proceso |

---

## Proceso

1. El sistema muestra el valor calculado (RF-005).
2. El operario confirma el pago.
3. El sistema registra el pago asociado a la salida.
4. La salida queda marcada como completada.

---

## Salidas

| Escenario            | Código HTTP | Respuesta                    |
| ----------------------- | ----------- | -------------------------------- |
| Pago registrado         | 200         | Confirmación del pago y cierre de la salida |
| Monto no coincide       | 422         | Mensaje de validación             |

---

## Endpoints asociados

| Método | Ruta                             | Auth requerida | Descripción                    |
| ------ | ----------------------------------- | -------------- | --------------------------------- |
| POST   | `/api/v1/vehicles/{plate}/payment`  | Sí             | Registra el pago y cierra la salida |

---

## Reglas de negocio

- RN-011: Una salida no se considera completada hasta que el pago quede registrado.
