# RF-019 — Registro de dueño y gestión de parqueaderos propios

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-019 |
| **Módulo** | Parqueaderos |
| **HUs asociadas** | HU-06, HU-07A, HU-07B, HU-08, HU-09, HU-10, HU-21, HU-32, HU-33 |
| **Estado** | Implementado; los catálogos globales siguen bajo administración de plataforma |

## Requisito

Una cuenta con rol dueño puede crear y gestionar uno o varios parqueaderos propios. Puede definir
ubicación geográfica, horarios semanales, inventario por categoría de vehículo y tarifa vigente
para cada tipo admitido. Las categorías globales y los tipos de espacio son administrados por la
plataforma, no creados arbitrariamente por cada dueño.

## Reglas

- La propiedad se comprueba en el backend en cada lectura y escritura.
- La ubicación se guarda como coordenadas; el mapa usa Leaflet/OpenStreetMap sin clave
  propietaria y conserva su atribución.
- Un horario no configurado bloquea nuevas reservas.
- No se reduce inventario ni se cambian horarios si eso deja reservas confirmadas o sesiones
  activas sin espacio u horario válido.
- El autorregistro solo permite roles cliente o dueño; no permite asignar operador o administrador.

## Trazabilidad de implementación

- Backend: `be/app/routers/owner_parking_lots.py`,
  `be/app/services/owner_parking_lot_service.py` y modelos `parking_lot`, `parking_rate`,
  `parking_lot_schedule` y `parking_space_type`.
- Frontend: `fe/src/pages/owner/OwnerDashboard.tsx`.
- Pruebas: `be/tests/test_owner_parking_lots.py`.
