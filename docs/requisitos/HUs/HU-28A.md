# HU-28A – Notificaciones de reservas

**Módulo:** notificaciones · **Rol:** usuario

## Historia de usuario

> Como usuario, quiero recibir un aviso cuando se confirma o cancela una reserva, para estar informado del estado de mi reserva.

## Criterios de aceptación

- [ ] Recibo una notificación al confirmarse una reserva con parqueadero, espacio y horario.
- [ ] Recibo una notificación al cancelarse una reserva.
- [ ] La notificación se envía en un máximo de 1 minuto tras el evento.

## Dependencias

[HU-13](HU-13.md), [HU-16](HU-16.md).

## Pendientes por definir / notas técnicas

Definir el canal (correo, notificación en la app, SMS o WhatsApp). Se supone correo y notificación en la app.

## Cambio respecto a la historia original

Nueva: sale de dividir la HU-28 por evento.
