# RF-022 — Búsqueda geográfica y disponibilidad por horario

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-022 |
| **Módulo** | Búsqueda y reservas |
| **HUs asociadas** | HU-11, HU-12 |
| **Estado** | Parcial; mapa y disponibilidad implementados, búsqueda y filtros deben verificarse |

## Requisito

El visitante consulta parqueaderos, ubicación y cupos por tipo de vehículo. Puede abrir el detalle
de un lugar, consultar disponibilidad para una fecha y un rango horario, y continuar a la reserva.
Los cupos futuros se calculan para ese intervalo: una reserva del martes no ocupa el miércoles.

## Reglas

- La disponibilidad se calcula desde parqueaderos, espacios, horarios y reservas de la base UUID.
- Los espacios inactivos y parqueaderos sin horario configurado no se ofrecen para reservar.
- El mapa actualiza su resumen cada cinco segundos; toda reserva vuelve a validar el cupo en el
  backend y en la base de datos.
- Las ubicaciones de demostración se identifican como ficticias; no se presentan como negocios
  reales.
- La búsqueda de direcciones usa Leaflet/OpenStreetMap y se ejecuta tras una acción explícita.

## Trazabilidad de implementación

- Backend: `be/app/routers/availability.py`, `be/app/services/availability_service.py`.
- Frontend: `fe/src/components/ParkingMap.tsx`, `fe/src/pages/AvailabilityPage.tsx`.
- Pruebas de API: `be/tests/test_availability.py`.
