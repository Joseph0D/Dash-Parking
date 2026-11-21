# RF-021 — Recuperación segura de contraseña por correo

## Identificación

| Campo | Valor |
|---|---|
| **ID** | RF-021 |
| **Módulo** | Autenticación |
| **HU asociada** | HU-35 |
| **Estado** | Implementado; envío real confirmado por el usuario |

## Requisito

El usuario solicita restablecer su contraseña, recibe por SMTP un enlace temporal y define una
nueva contraseña. Las solicitudes para cuentas existentes e inexistentes tienen la misma
respuesta pública.

## Reglas

- Token aleatorio, de un solo uso, almacenado como hash SHA-256 y válido por 30 minutos.
- Máximo tres solicitudes por correo y diez por IP dentro de una ventana móvil de una hora.
- Tokens anteriores se invalidan al emitir uno nuevo; contraseñas y tokens no aparecen en logs.
- La configuración SMTP y la URL del frontend provienen del entorno, nunca de valores secretos
  versionados.

## Endpoints y trazabilidad

- `POST /api/v1/auth/password-reset/request`
- `POST /api/v1/auth/password-reset/confirm`
- Backend: `be/app/routers/auth.py`, `be/app/services/password_reset_service.py`,
  `be/app/services/email_service.py`, migración `db/migrations/006_password_reset.sql`.
- Frontend: `fe/src/pages/ForgotPasswordPage.tsx`,
  `fe/src/pages/ResetPasswordPage.tsx`.
- Pruebas: `be/tests/test_password_reset.py`.
