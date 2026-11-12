# HU-28C – Notificaciones de pagos

**Módulo:** notificaciones · **Rol:** usuario

## Historia de usuario

> Como usuario, quiero recibir una notificación sobre el resultado de mi pago, para tener certeza de que se procesó.

## Criterios de aceptación

- [ ] Recibo una notificación cuando mi pago es aprobado.
- [ ] Recibo una notificación cuando mi pago es rechazado, con la opción de reintentar.
- [ ] La notificación se envía en un máximo de 1 minuto tras la respuesta de la pasarela.

## Dependencias

[HU-25](HU-25.md).

## Pendientes por definir / notas técnicas

Definir el canal, igual que en HU-28A.

## Cambio respecto a la historia original

Nueva: sale de dividir la HU-28 por evento. Incluye el aviso de rechazo.
