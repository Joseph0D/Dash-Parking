# HU-30A – Asignación de roles

**Módulo:** administración · **Rol:** administrador

## Historia de usuario

> Como administrador de plataforma, quiero asignar los roles cliente, dueño, operador y administrador de plataforma, para definir qué puede hacer cada persona.

## Criterios de aceptación

- [ ] El autorregistro solo permite crear cuentas cliente o dueño.
- [ ] Solo el administrador de plataforma puede asignar o cambiar roles privilegiados.
- [ ] Solo el administrador puede cambiar el rol de otro usuario.
- [ ] Cada usuario tiene un solo rol.
- [ ] Siempre debe existir al menos un administrador.

## Dependencias

[HU-01](HU-01.md), [HU-02](HU-02.md).

## Pendientes por definir / notas técnicas

El operador conserva un alcance por parqueadero asignado; el dueño solo administra sus
parqueaderos. No se permite autorregistro de operador ni administrador.

## Cambio respecto a la historia original

Se amplía el conjunto de roles y se prohíbe la asignación de roles privilegiados por autorregistro.
La interfaz administrativa para cambiar roles debe validarse por separado.
