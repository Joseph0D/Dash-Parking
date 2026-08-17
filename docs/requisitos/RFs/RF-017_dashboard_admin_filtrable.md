# RF-017 — Dashboard administrativo con filtros

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-017 · **Módulo** | Administrativo · **Estado** | Implementado |
| **HU asociada** | HU-017 (extiende RF-009) |

## Descripción
Expone un endpoint de métricas agregadas (ganancia total, número de sesiones, ocupación) que
acepta filtros combinables por tipo de vehículo y por rango de fechas.

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `vehicle_type` | Enum | No | `car`, `motorcycle`, `bicycle` |
| `start_date` | Fecha | No | ≤ `end_date` si ambos se envían |
| `end_date` | Fecha | No | ≥ `start_date` si ambos se envían |

## Proceso
1. Se parte de todos los `Payment` en estado `paid` (join con `ParkingSession`).
2. Se aplican los filtros recibidos (AND entre sí).
3. Se agregan: suma de montos (ganancia total), conteo de sesiones, promedio de duración.
4. Se agrega también el desglose por tipo de vehículo para graficar en el frontend.

## Salidas
| Escenario | HTTP | Respuesta |
|---|---|---|
| Consulta exitosa | 200 | Ganancia total, conteo, desglose por tipo de vehículo y por día |

## Endpoints asociados
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/v1/reports/dashboard?vehicle_type=&start_date=&end_date=` | Sí (solo admin) | Métricas agregadas y filtrables |

## Reglas de negocio
- RN-029: Solo se cuentan pagos en estado `paid` — sesiones activas sin pagar no suman a la ganancia.
- RN-030: Ausencia de un filtro implica "sin restricción" en ese campo (no excluye datos).
