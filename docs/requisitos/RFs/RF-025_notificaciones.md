# RF-025 — Notificaciones de reservas y pagos

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-025 |
| **Módulo** | Notificaciones |
| **HUs asociadas** | HU-28A, HU-28B, HU-28C |
| **Estado** | Pendiente; el correo de recuperación no satisface este requisito |

## Requisito

El sistema informa al titular de los eventos de confirmación/cancelación de reserva y del
resultado de pago, y envía recordatorios solo para reservas vigentes.

## Reglas

- Una notificación transaccional no reemplaza el registro persistente del evento.
- El contenido no debe exponer datos a destinatarios distintos del titular.
- El canal, las preferencias, la política de reintentos y el tiempo objetivo de entrega deben
  definirse antes de implementar.
- No confundir estos avisos con el correo de recuperación de contraseña (RF-021).

## Trazabilidad

- Historias: [HU-28A](../HUs/HU-28A.md), [HU-28B](../HUs/HU-28B.md),
  [HU-28C](../HUs/HU-28C.md).
