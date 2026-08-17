# RF-014 — Pago virtual (simulado)

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-014 · **Módulo** | Pagos · **Estado** | Implementado (pasarela simulada) |
| **HU asociada** | HU-014 |

## Descripción
Procesa el pago de una sesión activa mediante un método "virtual" (equivalente a Nequi/PSE/tarjeta).
Al no contar con credenciales de una pasarela real en este entorno académico, el flujo se simula
end-to-end con el mismo contrato de API que tendría una integración real (ver `restricciones.md`).

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `session_id` | UUID | Sí | Sesión debe estar activa y con monto calculado |
| `method` | Enum | Sí | `virtual` |

## Proceso
1. Se calcula el monto vigente de la sesión (RF-005).
2. Se crea un registro de `Payment` en estado `pending` con una referencia única.
3. Se simula la respuesta de la pasarela (aprobado en el flujo normal).
4. Si aprueba: `Payment.status = paid`, se cierra la sesión (RF-004) y se libera el espacio.

## Salidas
| Escenario | HTTP | Respuesta |
|---|---|---|
| Pago aprobado | 200 | Comprobante, sesión cerrada |
| Pago rechazado (simulado) | 402 | Mensaje de rechazo, sesión sigue activa |

## Endpoints asociados
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/v1/payments/virtual` | Sí | Procesa un pago virtual sobre una sesión |

## Reglas de negocio
- RN-024: Una sesión solo puede tener un pago en estado `paid`.
- RN-025: El punto de integración con una pasarela real reemplaza únicamente el paso 3 (simulación → llamada HTTP real), sin cambiar el contrato del endpoint.
