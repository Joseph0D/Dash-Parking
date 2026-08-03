# HU-012 — Autenticación por rol

<!--
  ¿Qué? Historia de usuario que describe el inicio de sesión y control de acceso por rol.
  ¿Para qué? Restringir acciones sensibles (tarifas, reportes, eliminación) solo a usuarios autorizados.
  ¿Impacto? Sin autenticación, cualquier persona con acceso al sistema podría alterar tarifas o eliminar historial.
-->

---

## Identificación

| Campo            | Valor                    |
| ---------------- | ---------------------------|
| **ID**           | HU-012                     |
| **Título**       | Autenticación por rol       |
| **Módulo**       | Autenticación                |
| **Prioridad**    | Alta (Core)                  |
| **Estado**       | Planificado (Sprint 2 — Autenticación y autorización) |
| **RF asociados** | RF-012                       |

---

## Historia

**Como** usuario del sistema,
**quiero** autenticarme con usuario y contraseña, y que el sistema identifique mi rol,
**para** que solo pueda realizar las acciones permitidas para ese rol.

---

## Criterios de aceptación

### CA-012.1 — Login con credenciales válidas

- **Dado que** ingreso un usuario y contraseña correctos,
- **cuando** envío el formulario de login,
- **entonces** accedo al sistema con el rol que tengo asignado (administrador u operario).

### CA-012.2 — Credenciales inválidas

- **Dado que** ingreso una contraseña incorrecta,
- **cuando** envío el formulario,
- **entonces** veo un mensaje de error genérico, sin indicar si el usuario existe o no.

### CA-012.3 — Restricción de acciones por rol

- **Dado que** inicié sesión como operario,
- **cuando** intento acceder a la administración de tarifas o reportes,
- **entonces** el sistema me niega el acceso a esa funcionalidad.

### CA-012.4 — Cierre de sesión

- **Dado que** tengo una sesión activa,
- **cuando** cierro sesión,
- **entonces** pierdo acceso a las funcionalidades protegidas hasta volver a autenticarme.
