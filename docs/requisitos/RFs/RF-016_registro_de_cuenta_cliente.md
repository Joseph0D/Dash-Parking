# RF-016 — Registro de cuenta de cliente (autoregistro)

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-016 · **Módulo** | Autenticación · **Estado** | Implementado |
| **HU asociada** | HU-016 |

## Descripción
Permite a cualquier visitante crear su propia cuenta con rol `client`, sin intervención de un
administrador. Complementa RF-012 (login), que ya cubría la autenticación de staff.

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| `name` | Texto | Sí | Mínimo 2 caracteres |
| `email` | Email | Sí | Formato válido, único en el sistema |
| `password` | Texto | Sí | Mínimo 8 caracteres |

## Proceso
1. Se valida el formato de los datos.
2. Se verifica que el correo no exista.
3. Se hashea la contraseña (bcrypt) y se crea el usuario con `role = client`.
4. Se retorna un token de sesión (login automático tras el registro).

## Salidas
| Escenario | HTTP | Respuesta |
|---|---|---|
| Cuenta creada | 201 | Token de sesión + datos del usuario |
| Correo ya registrado | 409 | Mensaje de conflicto |

## Endpoints asociados
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/v1/auth/register` | No | Crea la cuenta y autentica |

## Reglas de negocio
- RN-028: El rol de una cuenta autoregistrada siempre es `client`; `operator`/`admin` solo se asignan manualmente (fuera del alcance de este endpoint).
