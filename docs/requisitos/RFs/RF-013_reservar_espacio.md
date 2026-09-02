# RF-013 — Reserva de espacio con tiempo de ocupación

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-013 · **Módulo** | Reservas · **Estado** | Implementado |
| **HU asociada** | HU-013 |

## Descripción
Permite a un cliente reservar un espacio de un tipo/zona determinado, para una fecha/hora de
llegada y una duración estimada. El espacio queda bloqueado para otras reservas en ese rango.

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `vehicle_id` | UUID | Sí | Debe pertenecer al usuario autenticado |
| `vehicle_type` | Enum | Sí | `car`, `motorcycle`, `bicycle` |
| `start_time` | Fecha/hora | Sí | Debe ser futura |
| `duration_hours` | Decimal | Sí | Mayor a 0, máximo 24 |

## Proceso
1. Se valida que el vehículo pertenezca al cliente.
2. Se calcula `end_time = start_time + duration_hours`.
3. Se busca un espacio del tipo solicitado sin reservas/sesiones que se solapen con ese rango.
4. Si existe, se crea la reserva en estado `confirmed`. Si no, se rechaza.

## Salidas
| Escenario | HTTP | Respuesta |
|---|---|---|
| Reserva confirmada | 201 | Reserva creada con espacio asignado |
| Sin disponibilidad en ese rango | 422 | Mensaje de no disponibilidad |

## Endpoints asociados
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/v1/reservations` | Sí (client) | Crea una reserva |
| DELETE | `/api/v1/reservations/{id}` | Sí (dueño o admin) | Cancela una reserva |
| GET | `/api/v1/reservations/me` | Sí (client) | Lista mis reservas |

## Reglas de negocio
- RN-022: No pueden solaparse dos reservas confirmadas para el mismo espacio.
- RN-023: Al registrar el ingreso con una placa que tiene reserva vigente, la sesión se vincula a la reserva y no se cobra la reserva por separado.
