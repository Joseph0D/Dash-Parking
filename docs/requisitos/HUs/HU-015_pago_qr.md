# HU-015 — Pago con código QR

<!--
  ¿Qué? Historia que genera un código QR para pagar/validar la salida de una sesión de parqueo.
  ¿Para qué? Permitir escanear en la talanquera o pagar desde el celular del cliente.
  ¿Impacto? Sin QR, el operario debe teclear manualmente cada salida, reintroduciendo errores.
-->

## Identificación

| Campo | Valor |
|---|---|
| **ID** | HU-015 |
| **Módulo** | Pagos |
| **Prioridad** | Alta (Core — solicitado explícitamente por el cliente) |
| **Estado** | Implementado |
| **RF asociados** | RF-015 |

## Historia

**Como** cliente, **quiero** generar un código QR de mi sesión activa, **para** que el operario lo escanee (o yo lo use) para pagar y abrir la talanquera.

## Criterios de aceptación

### CA-015.1 — Generación del QR
Dado que tengo una sesión activa, cuando solicito el pase QR, entonces el sistema genera una imagen QR que codifica un token único y de un solo uso asociado a esa sesión.

### CA-015.2 — Validación por el operario
Dado que un operario escanea/ingresa el token del QR, cuando lo valida contra el backend, entonces el sistema retorna los datos de la sesión (placa, tiempo, monto) para proceder al cobro.

### CA-015.3 — Expiración del token
Dado que un token QR ya fue usado para completar un pago, cuando se intenta validar de nuevo, entonces el sistema lo rechaza por token inválido/expirado.
