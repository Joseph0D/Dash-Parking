# HU-07B – Actualización y desactivación de parqueaderos

**Módulo:** parqueaderos · **Rol:** dueño (administrador de plataforma para soporte)

## Historia de usuario

> Como dueño, quiero actualizar y desactivar mis parqueaderos, para mantener sus datos al día y retirarlos cuando ya no operen.

## Criterios de aceptación

- [ ] Puedo modificar los datos de un parqueadero; la identificación sigue siendo única.
- [ ] La capacidad total no puede ser menor que la suma de las capacidades de sus zonas.
- [ ] Para desactivar se pide confirmación.
- [ ] No puedo desactivar un parqueadero con reservas o tickets activos; se muestra el motivo.
- [ ] Un parqueadero desactivado no aparece en la búsqueda ni permite nuevas reservas.
- [ ] Puedo reactivar un parqueadero desactivado.
- [ ] No puedo modificar ni desactivar parqueaderos de otro dueño.

## Dependencias

[HU-07A](HU-07A.md), [HU-08](HU-08.md).

## Pendientes por definir / notas técnicas

Definir si la identificación es editable.

## Cambio respecto a la historia original

Se limita toda lectura y escritura a parqueaderos propios; la validación se realiza en el
backend, incluso si se altera el identificador enviado por el cliente.
