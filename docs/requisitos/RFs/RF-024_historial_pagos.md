# RF-024 — Historial de pagos y comprobantes

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-024 |
| **Módulo** | Pagos |
| **HUs asociadas** | HU-26, HU-27A, HU-27B |
| **Estado** | Pendiente; mantener en el backlog |

## Requisito

El cliente consulta únicamente sus pagos y comprobantes; el administrador de plataforma consulta
el conjunto autorizado. Los dueños reciben solo los pagos asociados a sus parqueaderos.
Los comprobantes deben tener identificador único y mostrar el detalle mínimo necesario.

## Reglas

- Un historial no autoriza a leer pagos de otro usuario o parqueadero.
- No se almacenan datos completos de tarjeta ni códigos de seguridad.
- La exportación PDF y la integración con una factura tributaria requieren definición aparte.

## Trazabilidad

- Historias: [HU-26](../HUs/HU-26.md), [HU-27A](../HUs/HU-27A.md),
  [HU-27B](../HUs/HU-27B.md).
- El estado de producción queda pendiente hasta que existan endpoints, permisos y pruebas de
  aislamiento específicos.
