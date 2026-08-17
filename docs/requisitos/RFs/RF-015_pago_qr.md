# RF-015 — Pago y validación con código QR

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-015 · **Módulo** | Pagos · **Estado** | Implementado |
| **HU asociada** | HU-015 |

## Descripción
Genera un token único de un solo uso asociado a la sesión activa de un cliente, codificado en una
imagen QR. El operario (o el propio cliente) lo valida para completar el cobro.

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `session_id` | UUID | Sí | Sesión debe estar activa |
| `token` (al validar) | Texto | Sí | Debe existir y no estar usado |

## Proceso
1. Al solicitar el pase QR, se genera un token aleatorio (UUID4) y se guarda asociado a la sesión con `used = false`.
2. Se codifica el token en una imagen QR (PNG en base64) y se retorna al cliente.
3. Al validar (endpoint de operario), se busca el token, se verifica que no esté usado y que la sesión siga activa.
4. Si es válido, se retorna la info de la sesión para proceder al cobro (RF-006) y se marca el token `used = true`.

## Salidas
| Escenario | HTTP | Respuesta |
|---|---|---|
| QR generado | 200 | Imagen QR (base64) + token |
| Token válido | 200 | Datos de la sesión (placa, tiempo, monto) |
| Token inválido/usado | 409 | Mensaje de token inválido |

## Endpoints asociados
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/v1/sessions/{id}/qr` | Sí (dueño) | Genera el QR de la sesión |
| POST | `/api/v1/sessions/qr/validate` | Sí (operator/admin) | Valida un token QR |

## Reglas de negocio
- RN-026: Un token QR es de un solo uso.
- RN-027: El token no reemplaza el pago — solo identifica la sesión para agilizar el cobro (RF-006/RF-014).
