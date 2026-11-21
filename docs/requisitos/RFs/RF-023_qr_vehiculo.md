# RF-023 — Identificación de vehículo mediante QR

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-023 |
| **Módulo** | Vehículos y operación |
| **HU asociada** | HU-36 |
| **Estado** | Implementado |

## Requisito

El sistema mantiene un QR/token asociado a cada vehículo. El cliente autenticado puede mostrarlo
y un operador autorizado puede usar el token para localizar el vehículo e iniciar el ingreso.

## Reglas

- El token identifica un vehículo, no una cuenta ni una reserva, y no contiene datos personales
  legibles.
- Solo el titular consulta el QR desde su cuenta; el flujo de validación exige autenticación de
  operador/administrador.
- La autorización del endpoint y la validación del vehículo son obligatorias aunque el token sea
  correcto.
- Este requisito es distinto al QR de una sesión usado para facilitar el cobro (RF-015). El QR
  de reserva es una mejora futura y no se considera implementado.

## Trazabilidad de implementación

- Backend: `be/app/routers/vehicles.py`, `be/app/routers/sessions.py`,
  `be/app/services/qr_service.py`, `be/app/models/vehicle_qr_token.py`.
- Frontend: `fe/src/pages/client/VehiclesPanel.tsx`,
  `fe/src/pages/admin/EntryExitPanel.tsx`.
