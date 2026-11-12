# HU-05C – Eliminación de vehículos

**Módulo:** vehículos · **Rol:** usuario

## Historia de usuario

> Como usuario con sesión iniciada, quiero eliminar un vehículo de mi cuenta, para no tener registrados vehículos que ya no uso.

## Criterios de aceptación

- [ ] Antes de eliminar, el sistema pide confirmación.
- [ ] No puedo eliminar un vehículo con reserva o ticket activo; se muestra el motivo.
- [ ] Al eliminar, el vehículo deja de aparecer en mi lista.
- [ ] El historial de reservas, tickets y pagos del vehículo se conserva.

## Dependencias

[HU-04](HU-04.md), [HU-05A](HU-05A.md).

## Pendientes por definir / notas técnicas

Definir si la eliminación es lógica (recomendado, para conservar el historial) o física.

## Cambio respecto a la historia original

Nueva: sale de dividir la HU-05 original.
