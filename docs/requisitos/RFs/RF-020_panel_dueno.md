# RF-020 — Panel diario aislado por parqueadero

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-020 |
| **Módulo** | Administración de parqueaderos |
| **HU asociada** | HU-34 |
| **Estado** | Implementado para consulta diaria y gestión básica |

## Requisito

El dueño consulta por separado las reservas del día, la ocupación por tipo de vehículo y los
ingresos asociados a cada parqueadero propio. Las cifras y acciones quedan acotadas al
parqueadero seleccionado.

## Reglas

- Cada endpoint verifica rol y propiedad; ocultar enlaces en frontend no sustituye la autorización
  del backend.
- Los reportes históricos o exportables no se consideran parte del panel diario; se trazan por
  HU-31/RF-009/RF-017.
- Los totales deben calcularse desde la fuente UUID canónica.

## Trazabilidad de implementación

- Backend: `be/app/routers/owner_parking_lots.py`,
  `be/app/services/owner_parking_lot_service.py`.
- Frontend: `fe/src/pages/owner/OwnerDashboard.tsx`.
- Pruebas: `be/tests/test_owner_parking_lots.py`.
