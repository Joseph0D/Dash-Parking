# RF-016 — Registro de cuenta de cliente o dueño

## Identificación
| Campo | Valor |
|---|---|
| **ID** | RF-016 · **Módulo** | Autenticación · **Estado** | Implementado |
| **HUs asociadas** | HU-01, HU-32 |

## Descripción
Permite a un visitante crear una cuenta `client` o `owner`, sin intervención de un administrador.
Complementa RF-012 (login). Nunca permite autorregistrarse como operador o administrador de
plataforma.

## Entradas
| Campo | Tipo | Obligatorio | Validaciones |
|---|---|---|---|
| Datos de perfil | Texto | Sí | Campos requeridos y validados por el esquema de registro |
| `email` | Email | Sí | Formato válido, único en el sistema |
| `password` | Texto | Sí | Mínimo 8 caracteres y máximo compatible con bcrypt |
| `account_type` | Enum | Sí | `client` o `owner`; no admite roles privilegiados |

## Proceso
1. Se valida el formato de los datos.
2. Se verifica que el correo no exista.
3. Se hashea la contraseña (bcrypt) y se asigna `client` u `owner`.
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
- RN-028: El autorregistro solo asigna `client` u `owner`; `operator` y `admin` requieren una
  vía autorizada.
