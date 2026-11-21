# RF-018 — Perfil y vehículos del cliente

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-018 |
| **Módulo** | Cuentas y vehículos |
| **HUs asociadas** | HU-03, HU-04, HU-05A, HU-05B, HU-05C |
| **Estado** | Parcial; las operaciones base existen, la conservación de historial debe verificarse |

## Requisito

El cliente autenticado consulta y actualiza sus datos personales y administra únicamente sus
propios vehículos. El backend valida la propiedad en cada operación y conserva las relaciones
históricas necesarias al retirar un vehículo.

## Reglas

- El documento de identidad no se modifica desde el flujo normal de perfil.
- La unicidad y validación de placas dependen del tipo de vehículo; bicicleta y patineta pueden
  no requerir placa.
- Un cambio de tipo no debe invalidar reservas o sesiones activas.
- La eliminación no debe borrar el historial financiero u operativo asociado.

## Trazabilidad de implementación

- Backend: `be/app/routers/auth.py`, `be/app/routers/vehicles.py`.
- Frontend: `fe/src/pages/client/VehiclesPanel.tsx`.
- Las pruebas de propiedad y retención del historial deben añadirse o actualizarse junto con los
  cambios de esquema.
