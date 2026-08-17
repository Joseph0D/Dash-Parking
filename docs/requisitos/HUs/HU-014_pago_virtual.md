# HU-014 — Pago virtual del servicio

<!--
  ¿Qué? Historia que permite pagar una sesión de parqueo por un medio virtual (simulado).
  ¿Para qué? Evitar manejo de efectivo y agilizar la salida.
  ¿Impacto? Sin esto, todo pago requeriría efectivo físico en la talanquera.
-->

## Identificación

| Campo | Valor |
|---|---|
| **ID** | HU-014 |
| **Módulo** | Pagos |
| **Prioridad** | Alta (Core — solicitado explícitamente por el cliente) |
| **Estado** | Implementado — pasarela simulada (ver `restricciones.md`) |
| **RF asociados** | RF-014 |

## Historia

**Como** cliente, **quiero** pagar el valor calculado de mi sesión mediante un método virtual, **para** finalizar mi salida sin usar efectivo.

## Criterios de aceptación

### CA-014.1 — Selección de método virtual
Dado que tengo una sesión activa con monto calculado, cuando elijo "pago virtual", entonces el sistema genera una referencia de pago única y muestra el estado "procesando".

### CA-014.2 — Confirmación simulada
Dado que la pasarela real no está disponible en este entorno académico, cuando se confirma el pago simulado, entonces el sistema marca la sesión como pagada, libera el espacio y genera el comprobante — de forma idéntica a como lo haría una pasarela real (Wompi/PSE), para que conectar una real en el futuro no cambie el contrato de la API.

### CA-014.3 — Pago rechazado
Dado que el pago simulado responde como rechazado, cuando esto ocurre, entonces la sesión permanece sin pagar y el cliente puede reintentar con otro método.
