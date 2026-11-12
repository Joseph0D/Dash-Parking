# HU-07B – Actualización y desactivación de parqueaderos

**Módulo:** parqueaderos · **Rol:** administrador

## Historia de usuario

> Como administrador, quiero actualizar y desactivar parqueaderos, para mantener sus datos al día y retirarlos de la plataforma cuando ya no operen.

## Criterios de aceptación

- [ ] Puedo modificar los datos de un parqueadero; la identificación sigue siendo única.
- [ ] La capacidad total no puede ser menor que la suma de las capacidades de sus zonas.
- [ ] Para desactivar se pide confirmación.
- [ ] No puedo desactivar un parqueadero con reservas o tickets activos; se muestra el motivo.
- [ ] Un parqueadero desactivado no aparece en la búsqueda ni permite nuevas reservas.
- [ ] Puedo reactivar un parqueadero desactivado.

## Dependencias

[HU-07A](HU-07A.md), [HU-08](HU-08.md).

## Pendientes por definir / notas técnicas

Definir si la identificación es editable.

## Cambio respecto a la historia original

Nueva: sale de dividir la HU-07. Se define qué pasa con las reservas activas al desactivar.
