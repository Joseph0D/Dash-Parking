# RF-013 — Reserva de espacio por parqueadero y rango horario

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-013 |
| **Módulo** | Reservas |
| **HUs asociadas** | HU-13, HU-14 (criterio fusionado), HU-15A, HU-15B, HU-16, HU-17 |
| **Estado** | Implementado para disponibilidad, reserva y cancelación; vencimiento automático pendiente |

## Descripción

Un cliente reserva un espacio compatible en un parqueadero para un intervalo. El backend asigna
un espacio libre y la base de datos impide el doble uso simultáneo. La disponibilidad se calcula
por fecha y rango: una reserva no ocupa el espacio fuera de su intervalo.

## Entradas

| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `parking_lot_id` | UUID | Sí | Parqueadero activo y con horario configurado |
| `vehicle_id` | UUID | Sí | Pertenece al usuario autenticado |
| `start_time` | Fecha/hora | Sí | Se interpreta en hora de Bogotá; debe ser futura |
| `end_time` | Fecha/hora | Sí | Posterior al inicio y dentro del horario aplicable |

## Proceso

1. Se comprueba que el vehículo pertenezca al cliente y que su categoría sea admitida.
2. Se valida parqueadero, horario, tipo de espacio e intervalo.
3. En una transacción se selecciona un espacio compatible y se crea la reserva confirmada.
4. La restricción PostgreSQL de intervalos evita solapamientos por espacio y vehículo incluso
   ante solicitudes concurrentes.
5. La cancelación autorizada marca la reserva cancelada; el cupo vuelve a estar disponible solo
   durante ese intervalo, sin alterar la disponibilidad de otras fechas.

## Reglas de negocio

- Los rangos se tratan como `[inicio, fin)`, por lo que dos reservas consecutivas pueden compartir
  el límite entre sus horarios.
- No existe un tope de 24 horas; prevalecen los horarios y reglas del parqueadero.
- Un parqueadero sin horario semanal completo no admite nuevas reservas.
- El dueño de un vehículo solo consulta/cancela sus reservas; el administrador consulta el alcance
  autorizado.
- El vencimiento automático y su tolerancia deben implementarse antes de aceptar HU-17.

## Endpoints y trazabilidad

- `POST /api/v1/reservations`, `GET /api/v1/reservations/me` y
  `DELETE /api/v1/reservations/{reservation_id}`.
- Backend: `be/app/routers/reservations.py`,
  `be/app/services/reservation_service.py`.
- Persistencia: `db/migrations/005_uuid_reservation_constraints.sql`.
- Frontend: `fe/src/pages/AvailabilityPage.tsx`,
  `fe/src/pages/client/ReservationsPanel.tsx`.
- Pruebas: `be/tests/test_reservations.py`,
  `be/tests/test_reservation_concurrency.py`.
