# HU-016 — Registro de cuenta de cliente

<!--
  ¿Qué? Historia de autoregistro para clientes finales del parqueadero (no solo staff).
  ¿Para qué? Permitir que cualquier persona cree su cuenta sin intervención de un administrador.
  ¿Impacto? Sin autoregistro, cada cliente dependería de que un administrador lo cree manualmente.
-->

## Identificación

| Campo | Valor |
|---|---|
| **ID** | HU-016 |
| **Módulo** | Autenticación |
| **Prioridad** | Alta (Core — solicitado explícitamente por el cliente) |
| **Estado** | Implementado |
| **RF asociados** | RF-016 |

## Historia

**Como** visitante, **quiero** crear mi propia cuenta de cliente con nombre, correo y contraseña, **para** poder registrar mis vehículos, reservar y pagar desde la plataforma.

## Criterios de aceptación

### CA-016.1 — Registro exitoso
Dado que ingreso nombre, correo y contraseña válidos, cuando envío el formulario, entonces se crea una cuenta con rol `client` y quedo autenticado automáticamente.

### CA-016.2 — Correo ya registrado
Dado que el correo ya existe en el sistema, cuando intento registrarme, entonces el sistema rechaza la operación con un mensaje claro.

### CA-016.3 — Rol por defecto
Dado que me registro desde el formulario público, cuando la cuenta se crea, entonces el rol siempre es `client` — los roles `operator` y `admin` solo los asigna un administrador (ver RF-012).
