# RF-012 — Autenticación por rol

<!--
  ¿Qué? Requisito funcional que define la autenticación y el control de acceso por rol.
  ¿Para qué? Restringir acciones sensibles (tarifas, reportes, eliminación) solo a usuarios autorizados.
  ¿Impacto? Sin autenticación, cualquier persona con acceso al sistema podría alterar tarifas o eliminar historial.
-->

---

## Identificación

| Campo         | Valor                    |
| ------------- | ----------------------------|
| **ID**        | RF-012                       |
| **Nombre**    | Autenticación por rol         |
| **Módulo**    | Autenticación                  |
| **Prioridad** | Alta                            |
| **Estado**    | Planificado (Sprint 2)           |
| **Informe original** | RNF de seguridad (Acceso mediante autenticación, Control de permisos) |

---

## Descripción

El sistema debe autenticar usuarios mediante usuario y contraseña, e identificar su rol
(administrador u operario) para restringir el acceso a funcionalidades sensibles (tarifas,
reportes, eliminación de registros).

---

## Entradas

| Campo      | Tipo  | Obligatorio | Validaciones            |
| ---------- | ----- | ----------- | ---------------------------|
| `username` | Texto | Sí          | Debe existir en el sistema  |
| `password` | Texto | Sí          | Se valida contra el hash almacenado |

---

## Proceso

1. El usuario ingresa usuario y contraseña.
2. El backend valida las credenciales contra el hash almacenado (bcrypt).
3. Si son válidas, se emite un token de sesión (JWT) que incluye el rol del usuario.
4. Cada endpoint protegido valida el token y, cuando corresponde, el rol requerido.
5. Los mensajes de error de login son genéricos, sin revelar si el usuario existe.

---

## Salidas

| Escenario              | Código HTTP | Respuesta                       |
| --------------------------- | ----------- | ------------------------------------ |
| Login exitoso                | 200         | Token de sesión + rol del usuario     |
| Credenciales inválidas       | 401         | Mensaje genérico de error             |
| Acceso a recurso sin permiso | 403         | Mensaje: acción reservada a otro rol   |

---

## Endpoints asociados

| Método | Ruta                    | Auth requerida | Descripción            |
| ------ | --------------------------| -------------- | --------------------------|
| POST   | `/api/v1/auth/login`      | No             | Autentica y retorna el token |
| POST   | `/api/v1/auth/logout`     | Sí             | Invalida la sesión activa    |

---

## Reglas de negocio

- RN-019: Las contraseñas nunca se almacenan en texto plano — se hashean con bcrypt.
- RN-020: Los mensajes de error de autenticación no deben permitir enumerar usuarios existentes.
- RN-021: Cada endpoint sensible (tarifas, reportes, eliminar registros) valida explícitamente el rol requerido, no solo la autenticación.
